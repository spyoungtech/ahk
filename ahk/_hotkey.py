from __future__ import annotations

import atexit
import functools
import logging
import re
import subprocess
import sys
import tempfile
import threading
import time
import warnings
from abc import ABC
from abc import abstractmethod
from base64 import b64encode
from queue import Queue
from typing import Any
from typing import Callable
from typing import Dict
from typing import List
from typing import Literal
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import Type
from typing import TypeVar
from typing import Union

import jinja2

from ._constants import HOTKEYS_SCRIPT_TEMPLATE as _HOTKEY_SCRIPT
from ._constants import HOTKEYS_SCRIPT_V2_TEMPLATE as _HOTKEY_V2_SCRIPT
from .directives import Directive
from ahk._utils import hotkey_escape
from ahk._utils import try_remove

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec


P_HotkeyCallbackParam = ParamSpec('P_HotkeyCallbackParam')
T_HotkeyCallbackReturn = TypeVar('T_HotkeyCallbackReturn')

_KEEPALIVE_SENTINEL = b'\xee\x80\x80'

_CLIPBOARD_SENTINEL = '\ue001'


def _default_ex_handler(failure: Union[str, int], ex: Exception) -> None:
    if isinstance(failure, str):
        logging.error(f'Failure in hotkey/hotstring {failure!r}', exc_info=True)
    elif isinstance(failure, int):
        logging.error(f'Failure in clipboard callback {failure!r}', exc_info=True)
    else:
        logging.fatal(f'Ex handler called with bad value {failure!r}', exc_info=False)
        raise TypeError(f'bad value for ex handler {failure!r}') from ex


class HotkeyTransportBase(ABC):
    def __init__(
        self,
        executable_path: str,
        default_ex_handler: Optional[Callable[[str, Exception], Any]] = None,
        directives: Optional[list[Directive | Type[Directive]]] = None,
        version: Optional[Literal['v1', 'v2']] = None,
    ):
        self._version = version
        self._executable_path = executable_path
        self._hotkeys: Dict[str, Hotkey] = {}
        self._default_ex_handler: Callable[[str, Exception], Any] = default_ex_handler or _default_ex_handler
        self._hotstrings: Dict[str, Hotstring] = {}
        self._running: bool = False
        self._get_callback_registry = functools.lru_cache(maxsize=None)(self._callback_registry_uncached)
        self._clipboard_callback: Optional[Callable[[int], Any]] = None
        self._clipboard_ex_handler: Optional[Callable[[int, Exception], Any]] = None
        if directives is None:
            directives = []
        self._directives: list[Directive | Type[Directive]] = [d for d in directives if d.apply_to_hotkeys_process]

    @property
    def _callback_registry(self) -> Dict[str, Union[Hotkey, Hotstring]]:
        return self._get_callback_registry()

    def _callback_registry_uncached(self) -> Dict[str, Union[Hotkey, Hotstring]]:
        registry: Dict[str, Union[Hotkey, Hotstring]] = dict(self._hotkeys)
        registry.update(self._hotstrings)
        return registry

    @abstractmethod
    def restart(self) -> Any:
        return NotImplemented

    @abstractmethod
    def start(self) -> Any:
        return NotImplemented

    def add_hotkey(self, hotkey: Hotkey) -> None:
        if hotkey._id in self._callback_registry:
            warnings.warn('Hotkey was already registered! This action will remove the original entry.', stacklevel=2)
        self._hotkeys[hotkey._id] = hotkey
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        return None

    def add_hotstring(self, hotstring: Hotstring) -> None:
        if hotstring._id in self._callback_registry:
            warnings.warn('Hotstring was already registered! This action will remove the original entry.', stacklevel=2)
        self._hotstrings[hotstring._id] = hotstring
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        # TODO: add support for adding IfWinActive/IfWinExist
        return None

    def remove_hotkey(self, hotkey: Hotkey) -> None:
        if hotkey._id not in self._callback_registry:
            raise ValueError(f'Hotkey {hotkey.keyname!r} is not registered')
        del self._hotkeys[hotkey._id]
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        return None

    def clear_hotkeys(self) -> None:
        self._hotkeys.clear()
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        return None

    def remove_hotstring(self, hotstring: Hotstring) -> None:
        if hotstring._id not in self._callback_registry:
            raise ValueError(f'Hostring {hotstring.trigger!r} is not registered')
        del self._hotstrings[hotstring._id]
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        return None

    def clear_hotstrings(self) -> None:
        self._hotstrings.clear()
        self._get_callback_registry.cache_clear()
        if self._running:
            self.restart()
        return None

    def on_clipboard_change(
        self, callback: Callable[[int], Any], ex_handler: Optional[Callable[[int, Exception], Any]] = None
    ) -> None:
        self._clipboard_callback = callback
        if ex_handler is not None:
            self._clipboard_ex_handler = ex_handler
        if self._running:
            self.restart()


class STOP: ...


class ThreadedHotkeyTransport(HotkeyTransportBase):
    def __init__(
        self,
        executable_path: str,
        default_ex_handler: Optional[Callable[[str, Exception], Any]] = None,
        directives: Optional[list[Directive | Type[Directive]]] = None,
        version: Optional[Literal['v1', 'v2']] = None,
    ):
        super().__init__(
            executable_path=executable_path,
            default_ex_handler=default_ex_handler,
            directives=directives,
            version=version,
        )
        self._callback_threads: List[threading.Thread] = []
        self._proc: Optional[subprocess.Popen[bytes]] = None
        self._callback_queue: Queue[Union[str, Type[STOP]]] = Queue()
        self._listener_thread: Optional[threading.Thread] = None
        self._dispatcher_thread: Optional[threading.Thread] = None
        loader: jinja2.BaseLoader

        if version is None or version == 'v1':
            template_name = 'hotkeys.ahk'
            const_script = _HOTKEY_SCRIPT
        elif version == 'v2':
            template_name = 'hotkeys-v2.ahk'
            const_script = _HOTKEY_V2_SCRIPT
        else:
            raise ValueError(f'Invalid version {version!r}')

        try:
            loader = jinja2.PackageLoader('ahk', 'templates')
        except ValueError:
            # see: https://github.com/spyoungtech/ahk/issues/201
            warnings.warn(
                'Jinja could not find templates with PackageLoader. Falling back to BaseLoader',
                category=UserWarning,
            )
            loader = jinja2.BaseLoader()
        self._jinja_env: jinja2.Environment = jinja2.Environment(loader=loader, autoescape=False)
        self._template: jinja2.Template
        try:
            self._template = self._jinja_env.get_template(template_name)
        except jinja2.TemplateNotFound:
            warnings.warn('hotkey template not found, falling back to constant', category=UserWarning)
            self._template = self._jinja_env.from_string(const_script)

    def _do_callback(
        self,
        hotkey_or_clip_change_type: Union[str, int],
        cb: Callable[[], Any],
        ex_handler: Optional[Union[Callable[[str, Exception], Any], Callable[[int, Exception], Any]]] = None,
    ) -> None:
        if ex_handler is None:
            ex_handler = self._default_ex_handler
        try:
            cb()
        except Exception as cb_exc:
            ex_handler(hotkey_or_clip_change_type, cb_exc)  # type: ignore[arg-type]
        return None

    def start(self) -> None:
        self._callback_queue.empty()
        assert self._running is False, 'Already running!'
        assert self._listener_thread is None, 'Listener is already active!'
        assert self._dispatcher_thread is None, 'Dispatcher is already active!'
        self._running = True
        listener_thread = threading.Thread(target=self.listener, daemon=True)
        self._listener_thread = listener_thread
        listener_thread.start()
        dispatcher_thread = threading.Thread(target=self.dispatcher, daemon=True)
        self._dispatcher_thread = dispatcher_thread
        dispatcher_thread.start()

    def stop(self) -> None:
        assert self._running is True, 'Not running! Must be started first!'
        assert self._dispatcher_thread is not None
        for i in range(1, 11):
            if self._proc is not None:
                break
            logging.debug(f'stop called before dispatched has started proc. Waiting for proc ({i}/10)')
            time.sleep(0.1)
        assert self._proc is not None
        self._running = False

        self._callback_queue.empty()
        self._callback_queue.put_nowait(STOP)
        logging.debug('Waiting for stop...')
        if self._dispatcher_thread is not None:
            try:
                self._dispatcher_thread.join(timeout=3)
            except TimeoutError:
                logging.debug('DISPATCHER JOIN TIMED OUT!')
            self._dispatcher_thread = None
        logging.debug('Waiting for callback stop...')
        self._callback_queue.join()
        if self._listener_thread is not None:
            try:
                self._listener_thread.join(timeout=3)
            except TimeoutError:
                logging.debug('LISTENER JOIN TIMED OUT!')
            self._listener_thread = None
        self._proc.kill()

    def restart(self) -> None:
        self.stop()
        self.start()

    def dispatcher(self) -> None:
        while True:
            ex_handler: Union[Callable[[str, Exception], Any], Callable[[int, Exception], Any]]
            cb: Union[Callable[[], Any], Callable[[int], Any]]
            job = self._callback_queue.get()
            if job is STOP:
                self._callback_queue.task_done()
                break
            assert isinstance(job, str)
            if job.startswith(_CLIPBOARD_SENTINEL):
                assert self._clipboard_callback is not None
                clip_change_type = int(job.lstrip(_CLIPBOARD_SENTINEL))
                callback = self._clipboard_callback

                def f() -> None:
                    callback(clip_change_type)

                cb = f
                if self._clipboard_ex_handler is not None:
                    ex_handler = self._clipboard_ex_handler
                else:
                    ex_handler = _default_ex_handler
            elif job not in self._callback_registry:
                logging.warning(f'Received request to dispatch unregistered hotkey: {job!r}. Ignoring.')
                self._callback_queue.task_done()
                continue
            else:
                hot_thing: Union[Hotstring, Hotkey] = self._callback_registry[job]
                assert hot_thing.callback is not None
                cb = hot_thing.callback
                assert hot_thing.ex_handler is not None
                ex_handler = hot_thing.ex_handler
            assert cb is not None
            assert ex_handler is not None
            t = threading.Thread(target=self._do_callback, args=(job, cb, ex_handler), daemon=True)
            self._callback_threads.append(t)
            t.start()
            self._callback_queue.task_done()  # maybe _do_callback should handle this?

    def _render_hotkey_template(self) -> str:
        if self._clipboard_callback is not None:
            on_clipboard = True
        else:
            on_clipboard = False
        ret = self._template.render(
            hotkeys=list(self._hotkeys.values()),
            hotstrings=self._hotstrings.values(),
            on_clipboard=on_clipboard,
            directives=self._directives,
        )
        return ret

    def listener(self) -> None:
        hotkey_script_contents = self._render_hotkey_template()
        logging.debug('hotkey script contents:\n%s', hotkey_script_contents)
        with tempfile.NamedTemporaryFile(
            mode='w', prefix='python-ahk-hotkeys-', suffix='.ahk', delete=False, encoding='utf-8'
        ) as f:
            f.write(hotkey_script_contents)
        atexit.register(try_remove, f.name)
        self._proc = subprocess.Popen(
            [self._executable_path, '/CP65001', '/ErrorStdOut', f.name],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
        )
        atexit.register(kill, self._proc)
        assert self._proc.stdout is not None
        assert self._proc.stdin is not None
        while self._running:
            line = self._proc.stdout.readline()
            if line.rstrip(b'\n') == _KEEPALIVE_SENTINEL:
                logging.debug('keepalive received')
                self._proc.stdin.write(b'\xee\x80\x80\n')
                self._proc.stdin.flush()
                continue
            if not line.strip():
                logging.debug('Listener: Process probably died, exiting')
                break
            logging.debug(f'Received {line!r}')
            self._callback_queue.put_nowait(line.decode('UTF-8').strip())
        # although redundant with the atexit handler, this will prevent
        # excessive use of disk space in cases where the hotkey process is [re]started many times
        try_remove(f.name)


class Hotkey:
    def __init__(
        self, keyname: str, callback: Callable[[], Any], *, ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ):
        self._keyname: str = keyname
        self.callback: Callable[[], Any] = callback
        self.ex_handler: Callable[[str, Exception], Any] = ex_handler or _default_ex_handler
        self._validate()

    @property
    def keyname(self) -> str:
        return self._keyname

    def __hash__(self) -> int:
        return hash(self.keyname)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Hotkey):
            return NotImplemented
        return hash(self) == hash(other)

    def _validate(self) -> None:
        assert '\n' not in self.keyname, 'Newlines not allowed in hotkey trigger keys'
        return None

    @property
    def _id(self) -> str:
        return str(hash(self))


class Hotstring:
    def __init__(
        self,
        trigger: str,
        replacement_or_callback: Union[str, Callable[[], Any]],
        *,
        ex_handler: Optional[Callable[[str, Exception], Any]] = None,
        options: str = '',
    ):
        self.replacement: Optional[str]
        self.callback: Optional[Callable[[], Any]]
        self.ex_handler: Optional[Callable[[str, Exception], Any]]
        self._trigger: str = hotkey_escape(trigger)
        self._options: str = options
        if callable(replacement_or_callback):
            self.replacement = None
            self.callback = replacement_or_callback
            self.ex_handler = ex_handler or _default_ex_handler
        else:
            if not isinstance(replacement_or_callback, str):
                raise TypeError('Expected callable or str for hotstring')
            if ex_handler is not None:
                raise TypeError(
                    'ex_handler may only be specified when a callable is used. Must be None when using string replacement.'
                )
            assert isinstance(replacement_or_callback, str)
            self.replacement = replacement_or_callback
            self.callback = None
            self.ex_handler = None
        self._validate()

    @property
    def options(self) -> str:
        return self._options

    @property
    def trigger(self) -> str:
        return self._trigger

    def __hash__(self) -> int:
        return hash(self.trigger)

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Hotstring):
            return NotImplemented
        return hash(self) == hash(other)

    @property
    def _id(self) -> str:
        return str(hash(self)).replace('-', '0')

    @property
    def _replacement_as_b64(self) -> str:
        assert self.replacement is not None
        data = bytes(self.replacement, 'UTF-8')
        return str(b64encode(data), 'UTF-8')

    def _validate(self) -> None:
        if not isinstance(self.trigger, str):
            raise TypeError(f'trigger must be a string. Got {self.trigger!r}')
        if self.options:
            assert '\n' not in self.options, 'Newlines not allowed in options'
            assert 'x' not in self.options.lower(), 'X is not an allowed option. Use a callback instead.'
            assert re.fullmatch(
                r'(\*|\?|C|C1|K\d+|O|P\d+|S[IPE]|T|Z)+', self.options.upper()
            ), f'Invalid options: {self.options!r}'
        return None


@runtime_checkable
class Killable(Protocol):
    def kill(self) -> None: ...


def kill(proc: Killable) -> None:
    try:
        proc.kill()
    except:  # noqa
        pass
