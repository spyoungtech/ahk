from __future__ import annotations

import os
import subprocess
import sys
import threading
from abc import ABC
from abc import abstractmethod
from textwrap import dedent
from typing import Any
from typing import Callable
from typing import Deque
from typing import Dict
from typing import List
from typing import Optional
from typing import Tuple
from typing import Type
from typing import TypeVar
from typing import Union

if sys.version_info >= (3, 10):
    from typing import ParamSpec
else:
    from typing_extensions import ParamSpec
import traceback
import logging
import tempfile
from jinja2 import Environment, BaseLoader
from queue import Queue

P_HotkeyCallbackParam = ParamSpec('P_HotkeyCallbackParam')
T_HotkeyCallbackReturn = TypeVar('T_HotkeyCallbackReturn')

_KEEPALIVE_SENTINEL = b'\xee\x80\x80'


def _default_ex_handler(hotkey: str, ex: Exception) -> None:
    logging.error(f'Failure in hotkey {hotkey!r}', exc_info=True)


class HotkeyTransportBase(ABC):
    def __init__(self, executable_path: str, default_ex_handler: Optional[Callable[[str, Exception], Any]] = None):
        self._executable_path = executable_path
        self._hotkeys: Dict[str, Tuple[Callable[[], Any], Optional[Callable[[str, Exception], Any]]]] = {}
        self._default_ex_handler: Callable[[str, Exception], Any] = default_ex_handler or _default_ex_handler
        # self._transport_options: Dict[Any, Any] = transport_options or {}
        self._hotstrings: Dict[str, str] = {}
        self._running: bool = False

    @abstractmethod
    def restart(self) -> Any:
        return NotImplemented

    @abstractmethod
    def start(self) -> Any:
        return NotImplemented

    @staticmethod
    def _validate_hotkey(hotkey: str) -> None:
        assert '\n' not in hotkey, 'Newlines not allowed in hotkeys'  # TODO: perform better validation

    @staticmethod
    def _validate_hotstring(trigger: str, replacement: str) -> None:
        assert '\n' not in trigger, 'newlines not allowed in hotstrings'  # TODO: perform better validation
        assert '\n' not in replacement, 'newlines not allowed in hotstrings'

    def add_hotkey(
        self, hotkey: str, callback: Callable[[], Any], ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ) -> None:
        self._validate_hotkey(hotkey)
        self._hotkeys[hotkey] = (callback, ex_handler)
        if self._running:
            self.restart()
        return None

    def add_hotstring(self, trigger_string: str, replacement: str) -> None:
        replacement = replacement.replace('\n', '`n').replace('\r', '`n')
        self._validate_hotstring(trigger_string, replacement)
        self._hotstrings[trigger_string] = replacement
        if self._running:
            self.restart()
        # TODO: add support for adding IfWinActive/IfWinExist
        return None


class STOP:
    ...


class ThreadedHotkeyTransport(HotkeyTransportBase):
    def __init__(self, executable_path: str, default_ex_handler: Optional[Callable[[str, Exception], Any]] = None):
        super().__init__(executable_path=executable_path, default_ex_handler=default_ex_handler)
        self._callback_threads: List[threading.Thread] = []
        self._proc: Optional[subprocess.Popen[bytes]] = None
        self._callback_queue: Queue[Union[str, Type[STOP]]] = Queue()
        self._listener_thread: Optional[threading.Thread] = None
        self._dispatcher_thread: Optional[threading.Thread] = None

    def _do_callback(
        self, hotkey: str, cb: Callable[[], Any], ex_handler: Optional[Callable[[str, Exception], Any]] = None
    ) -> None:
        if ex_handler is None:
            ex_handler = self._default_ex_handler
        try:
            cb()
        except Exception as cb_exc:
            ex_handler(hotkey, cb_exc)
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
        assert self._proc is not None
        self._running = False
        self._proc.kill()

        self._callback_queue.empty()
        self._callback_queue.put_nowait(STOP)
        print('Waiting for stop...')
        if self._dispatcher_thread is not None:
            self._dispatcher_thread.join()
            self._dispatcher_thread = None

        self._callback_queue.join()
        if self._listener_thread is not None:
            self._listener_thread.join()
            self._listener_thread = None

    def restart(self) -> None:
        self.stop()
        self.start()

    def dispatcher(self) -> None:
        while True:
            job = self._callback_queue.get()
            if job is STOP:
                self._callback_queue.task_done()
                break

            assert isinstance(job, str)
            if job not in self._hotkeys:
                logging.warning(f'Received request to dispatch unregistered hotkey: {job!r}. Ignoring.')
                self._callback_queue.task_done()
                continue

            cb, ex_handler = self._hotkeys[job]
            t = threading.Thread(target=self._do_callback, args=(job, cb, ex_handler), daemon=True)
            self._callback_threads.append(t)
            t.start()
            self._callback_queue.task_done()  # maybe _do_callback should handle this?

    def _render_hotkey_tempate(self) -> str:
        env = Environment(loader=BaseLoader())
        template = env.from_string(
            dedent(
                """\
        KEEPALIVE := Chr(57344)
        SetTimer, keepalive, 1000

        {% for hotkey in hotkeys %}

        {{ hotkey }}::
            FileAppend, %A_ThisHotkey%`n, *, UTF-8
            return

        {% endfor %}

        {% for trigger, replacement in hotstrings %}

        ::{{ trigger }}::{{replacement}}

        {% endfor %}
        keepalive:
        global KEEPALIVE
        FileAppend, %KEEPALIVE%`n, *, UTF-8
        """
            )
        )
        ret = template.render(hotkeys=list(self._hotkeys), hotstrings=self._hotstrings.items())
        assert isinstance(ret, str)
        return ret

    def listener(self) -> None:
        last_keepalive_received: Optional[float] = None

        hotkey_script_contents = self._render_hotkey_tempate()
        logging.debug('hotkey script contents:\n%s', hotkey_script_contents)
        with tempfile.TemporaryDirectory(prefix='python-ahk') as tmpdirname:
            exc_file = os.path.join(tmpdirname, 'executor.ahk')
            with open(exc_file, 'w') as f:
                f.write(hotkey_script_contents)
            self._proc = subprocess.Popen(
                [self._executable_path, '/CP65001', '/ErrorStdOut', exc_file],
                stdin=subprocess.PIPE,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            while self._running:
                assert self._proc.stdout is not None
                line = self._proc.stdout.readline()
                if line.rstrip(b'\n') == _KEEPALIVE_SENTINEL:
                    logging.debug('keepalive received')
                    continue
                logging.debug(f'Received {line!r}')
                self._callback_queue.put_nowait(line.decode('UTF-8').strip())
