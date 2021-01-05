import ast
import asyncio
import collections
from contextlib import suppress
import warnings
from types import CoroutineType
from ahk.script import ScriptEngine
from ahk.utils import escape_sequence_replace, make_logger, AsyncifyMeta, async_filter

logger = make_logger(__name__)


class WindowNotFoundError(ValueError):
    pass


class Control:
    def __init__(self):
        raise NotImplementedError

    def click(self):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlClick.htm

        :return:
        """
        raise NotImplementedError

    def focus(self):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlFocus.htm

        :return:
        """
        raise NotImplementedError

    def get(self, key):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlGet.htm

        :param key:
        :return:
        """
        raise NotImplementedError

    def has_focus(self):
        raise NotImplementedError

    @property
    def position(self):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlGetPos.htm

        :return:
        """
        raise NotImplementedError

    @property
    def text(self):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlGetText.htm

        :return:
        """
        raise NotImplementedError

    @text.setter
    def text(self, new_text):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlSetText.htm

        :param new_text:
        :return:
        """
        raise NotImplementedError

    def move(self):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlMove.htm

        :return:
        """
        raise NotImplementedError

    def send(self, raw=False):
        """
        REF: https://www.autohotkey.com/docs/commands/ControlSend.htm

        :param raw:
        :return:
        """
        raise NotImplementedError


class Window(object):

    MINIMIZED = "-1"
    MAXIMIZED = "1"
    NON_MIN_NON_MAX = "0"

    _set_subcommands = {
        'always_on_top': 'AlwaysOnTop',
        'bottom': 'Bottom',
        'top': 'Top',
        'disable': 'Disable',
        'enable': 'Enable',
        'redraw': 'Redraw',
        'style': 'Style',
        'ex_style': 'ExStyle',
        'region': 'Region',
        'transparent': 'Transparent',
        'transcolor': 'TransColor'
    }

    _get_subcommands = {
        'id': 'ID',
        'id_last': 'IDLast',
        'pid': 'PID',
        'process_name': 'ProcessName',
        'process_path': 'ProcessPath',
        'process': 'ProcessPath',
        'count': 'count',
        'list': 'list',
        'min_max': "MinMax",
        'controls': 'ControlList',
        'controls_hwnd': 'ControlListHwnd',
        'transparent': 'Transparent',
        'trans_color': 'TransColor',
        'style': 'Style',   # This will probably get a property later
        'ex_style': 'ExStyle',  # This will probably get a property later
    }

    #  add reverse lookups
    _set_subcommands.update({value: value for value in _set_subcommands.values()})
    _get_subcommands.update({value: value for value in _get_subcommands.values()})

    def __init__(self, engine: ScriptEngine, ahk_id: str, encoding=None):
        self.engine = engine  # should this be a weakref instead?
        self.id = ahk_id
        self.encoding = encoding

    @classmethod
    def from_mouse_position(cls, engine: ScriptEngine, **kwargs):
        script = engine.render_template('window/from_mouse.ahk')
        ahk_id = engine.run_script(script)
        return cls(engine=engine, ahk_id=ahk_id, **kwargs)

    @classmethod
    def from_pid(cls, engine: ScriptEngine, pid, **kwargs):
        script = engine.render_template('window/get.ahk',
                                        subcommand="ID",
                                        title=f'ahk_pid {pid}')
        ahk_id = engine.run_script(script)
        return cls(engine=engine, ahk_id=ahk_id, **kwargs)

    def __getattr__(self, attr):
        if attr.lower() in self._get_subcommands:
            return self.get(attr)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def _get(self, subcommand):
        sub = self._get_subcommands.get(subcommand)
        if not sub:
            raise ValueError(f'No such subcommand {subcommand}')

        script = self._render_template(
            'window/get.ahk',
            subcommand=sub,
            title=f"ahk_id {self.id}",
        )

        return script

    def get(self, subcommand):
        script = self._get(subcommand)
        return self.engine.run_script(script)

    def __repr__(self):
        return f'<ahk.window.Window ahk_id={self.id}>'

    def _set(self, subcommand, value):
        sub = self._set_subcommands.get(subcommand)
        if not sub:
            raise ValueError(f'No such subcommand {subcommand}')

        script = self._render_template(
            'window/win_set.ahk',
            subcommand=subcommand,
            value=value,
            title=f"ahk_id {self.id}"
        )
        return script

    def set(self, subcommand, value):
        script = self._set(subcommand, value)
        return self.engine.run_script(script)

    def _get_pos(self):
        script = self._render_template(
            'window/win_position.ahk',
            title=f"ahk_id {self.id}"
        )
        return script

    def get_pos(self):
        """
        Same as ``rect``

        :return:
        """
        script = self._get_pos()
        resp = self.engine.run_script(script)
        try:
            value = ast.literal_eval(resp)
            return value
        except SyntaxError:
            raise WindowNotFoundError('No window found')

    @property
    def rect(self):
        return self.get_pos()

    @rect.setter
    def rect(self, new_position):
        x, y, width, height = new_position
        self.move(x=x, y=y, width=width, height=height)

    @property
    def position(self):
        x, y, _, _ = self.get_pos()

        return x, y

    @position.setter
    def position(self, new_position):
        x, y = new_position
        self.move(x, y)

    @property
    def width(self):
        _, _, width, _ = self.get_pos()
        return width

    @width.setter
    def width(self, new_width):
        self.move(width=new_width)

    @property
    def height(self):
        _, _, _, height = self.get_pos()
        return height

    @height.setter
    def height(self, new_height):
        self.move(height=new_height)

    def _base_check(self, command):
        script = self._render_template(
            "window/base_check.ahk",
            command=command,
            title=f"ahk_id {self.id}"
        )
        return script

    def _base_property(self, command):
        script = self._base_check(command)
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

    @property
    def active(self):
        return self._base_property(command="WinActive")

    def is_active(self):
        return self.active

    @property
    def exist(self):
        return self._base_property(command="WinExist")

    def exists(self):
        return self.exist

    def _base_get_method_(self, command):
        script = self._render_template(
            "window/base_get_command.ahk",
            command=command,
            title=f"ahk_id {self.id}"
        )
        return script
    def _base_get_method(self, command):
        script = self._base_get_method_(command)
        result = self.engine.run_script(script, decode=False)
        if self.encoding:
            return result.stdout.decode(encoding=self.encoding)
        return result.stdout

    @property
    def title(self):
        return self._base_get_method("WinGetTitle")

    def get_title(self):
        return self.title

    def _set_title(self, value):
        script = self._render_template(
            "window/win_set_title.ahk",
            title=f"ahk_id {self.id}",
            new_title=value
        )
        return script

    @title.setter
    def title(self, value):
        script = self._set_title(value)
        return self.engine.run_script(script)

    def set_title(self, value):
        script = self._set_title(value)
        self.engine.run_script(script)

    @property
    def class_name(self):
        return self._base_get_method("WinGetClass")

    @property
    def text(self):
        return self._base_get_method("WinGetText")

    @property
    def minimized(self):
        return self.get("MinMax") == self.MINIMIZED

    @property
    def maximized(self):
        return self.get("MinMax") == self.MAXIMIZED

    def is_minimized(self):
        return self.minimized

    def is_maximized(self):
        return self.maximized

    @property
    def non_max_non_min(self):
        return self.get("MinMax") == self.NON_MIN_NON_MAX

    def is_minmax(self):
        return self.get("MinMax") != self.NON_MIN_NON_MAX

    def get_class_name(self):
        return self.class_name

    def get_text(self):
        return self.text

    @property
    def transparent(self) -> int:
        result = self.get("Transparent")
        if result:
            return int(result)
        else:
            return 255

    def get_transparency(self) -> int:
        return self.transparent

    @transparent.setter
    def transparent(self, value):
        if isinstance(value, int) and 0 <= value <= 255:
            self.set("Transparent", value)
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use [0, 255] integer')

    def set_transparency(self, new_value):
        self.transparent = new_value

    def _always_on_top(self):
        script = self._render_template(
            'window/win_is_always_on_top.ahk',
            title=f"ahk_id {self.id}"
        )
        return script

    @property
    def always_on_top(self) -> bool:
        script = self._always_on_top()
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

    def is_always_on_top(self) -> bool:
        return self.always_on_top

    @always_on_top.setter
    def always_on_top(self, value):
        if value in ('on', 'On', True, 1):
            self.set('AlwaysOnTop', 'On')
        elif value in ('off', 'Off', False, 0):
            self.set('AlwaysOnTop', 'Off')
        elif value in ('toggle', 'Toggle', -1):
            self.set('AlwaysOnTop', 'Toggle')
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use On/Off/Toggle/True/False/0/1/-1')

    def set_always_on_top(self, value):
        self.always_on_top = value

    def disable(self):
        """
        Distable the window
        
        :return: 
        """
        return self.set('Disable', '') or None

    def enable(self):
        """
        Enable the window
        
        :return: 
        """
        return self.set('Enable', '') or None

    def redraw(self):
        return self.set('Redraw', '') or None

    def to_bottom(self):
        """
        Send window to bottom (behind other windows)
        :return:
        """
        return self.set('Bottom', '') or None

    def to_top(self):
        """
        Bring the window to the foreground (above other windows)
        
        :return: 
        """
        return self.set('Top', '') or None

    def _render_template(self, *args, **kwargs):
        kwargs['win'] = self
        return self.engine.render_template(*args, **kwargs)

    def _base_method_(self, command, seconds_to_wait="", blocking=False):
        script = self._render_template(
            "window/base_command.ahk",
            command=command,
            title=f"ahk_id {self.id}",
            seconds_to_wait=seconds_to_wait
        )
        return script

    def _base_method(self, command, seconds_to_wait="", blocking=False):
        script = self._base_method_(command, seconds_to_wait=seconds_to_wait)
        return self.engine.run_script(script, blocking=blocking)

    def activate(self):
        """
        Activate the window.

        See also: `WinActivate`_

        .. _WinActivate: https://www.autohotkey.com/docs/commands/WinActivate.htm

        :return:
        """
        return self._base_method("WinActivate") or None

    def activate_bottom(self):
        """
        Calls `WinActivateBottom`_ on the window

        .. _WinActivateBottom: https://www.autohotkey.com/docs/commands/WinActivateBottom.htm

        :return:
        """
        return self._base_method("WinActivateBottom") or None

    def close(self, seconds_to_wait=""):
        """
        Closes the Window. See also: `WinClose`_

        .. _WinClose: https://www.autohotkey.com/docs/commands/WinClose.htm

        :param seconds_to_wait:
        :return:
        """
        return self._base_method("WinClose", seconds_to_wait=seconds_to_wait) or None

    def hide(self):
        """
        Hides the window. See also: `WinHide`_

        .. _WinHide: https://www.autohotkey.com/docs/commands/WinHide.htm
        
        
        :return:
        """
        return self._base_method("WinHide") or None

    def kill(self, seconds_to_wait=""):
        return self._base_method("WinKill", seconds_to_wait=seconds_to_wait) or None

    def maximize(self):
        """
        maximize the window
        
        :return: 
        """
        return self._base_method("WinMaximize") or None

    def minimize(self):
        """
        minimize the window
        
        :return: 
        """
        return self._base_method("WinMinimize") or None

    def restore(self):
        """
        restore the window
        
        :return: 
        """
        return self._base_method("WinRestore") or None

    def show(self):
        """
        show the window
        
        :return: 
        """
        return self._base_method("WinShow") or None

    def wait(self, seconds_to_wait=""):
        """
        
        :param seconds_to_wait: 
        :return: 
        """
        return self._base_method("WinWait", seconds_to_wait=seconds_to_wait, blocking=True) or None

    def wait_active(self, seconds_to_wait=""):
        """
        
        :param seconds_to_wait: 
        :return: 
        """
        return self._base_method("WinWaitActive", seconds_to_wait=seconds_to_wait, blocking=True) or None

    def wait_not_active(self, seconds_to_wait=""):
        """
        
        :param seconds_to_wait: 
        :return: 
        """
        return self._base_method("WinWaitNotActive", seconds_to_wait=seconds_to_wait, blocking=True) or None

    def wait_close(self, seconds_to_wait=""):
        """
        
        :param seconds_to_wait:
        :return: 
        """
        return self._base_method("WinWaitClose", seconds_to_wait=seconds_to_wait, blocking=True) or None

    def _move(self, x='', y='', width=None, height=None):
        script = self._render_template(
            'window/win_move.ahk',
            title=f"ahk_id {self.id}",
            x=x, y=y, width=width, height=height
        )
        return script

    def move(self, x='', y='', width=None, height=None):
        """
        Move the window to a position and/or change its geometry

        :param x: 
        :param y: 
        :param width: 
        :param height: 
        :return: 
        """
        script = self._move(x=x, y=y, width=width, height=height)
        self.engine.run_script(script)

    def _send(self, keys, delay=10, raw=False, blocking=False, escape=False, press_duration=-1):
        if escape:
            keys = escape_sequence_replace(keys)
        script = self._render_template(
            'window/win_send.ahk',
            title=f"ahk_id {self.id}",
            keys=keys, raw=raw, delay=delay,
            press_duration=press_duration, blocking=blocking
        )
        return script

    def send(self, keys, delay=10, raw=False, blocking=False, escape=False, press_duration=-1):
        """
        Send keystrokes directly to the window.
        Uses ControlSend
        https://autohotkey.com/docs/commands/Send.htm
        """
        script = self._send(keys, delay=delay, raw=raw, blocking=blocking, escape=escape, press_duration=press_duration)
        return self.engine.run_script(script, blocking=blocking)

    def _click(self, x=None, y=None, *, button=None, n=1, options=None, blocking=True):
        from ahk.mouse import resolve_button
        if x or y:
            if y is None and isinstance(x, collections.abc.Sequence) and len(x) == 2:
                #  alow position to be specified by a sequence of length 2
                x, y = x
            assert x is not None and y is not None, 'If provided, position must be specified by x AND y'
        button = resolve_button(button)

        script = self._render_template(
            'window/win_click.ahk',
            x=x, y=y, hwnd=f"ahk_id {self.id}", button=button, n=n, options=options
        )

        return script

    def click(self, *args, **kwargs):
        """
        Click at an x/y location on the screen.
        Uses ControlClick
        https://autohotkey.com/docs/commands/ControlClick.htm

        x/y position params may also be specified as a 2-item sequence

        :param x: x offset relative to topleft corner of the window
        :param y: y offset relative to the top of the window
        :param button: the button to press (default is left mouse)
        :param n: number of times to click
        :param options: per ControlClick documentation
        :param blocking:
        :return:
        """
        blocking = kwargs.get('blocking', True)
        script = self._click(*args, **kwargs)
        return self.engine.run_script(script, blocking=blocking)

    def __eq__(self, other):
        if not isinstance(other, Window):
            return False
        return self.id == other.id

    def __hash__(self):
        return hash(repr(self))


class WindowMixin(ScriptEngine):
    def __init__(self, *args, **kwargs):
        self.window_encoding = kwargs.pop('window_encoding', None)
        super().__init__(*args, **kwargs)

    def _win_get(self, title='', text='', exclude_title='', exclude_text=''):
        script = self.render_template(
            'window/get.ahk',
            subcommand='ID',
            title=title,
            text=text,
            exclude_text=exclude_text,
            exclude_title=exclude_title
        )
        return script

    def win_get(self, title='', text='', exclude_title='', exclude_text='', encoding=None):
        script = self._win_get(title=title, text=text, exclude_title=exclude_title, exclude_text=exclude_text)
        encoding = encoding or self.window_encoding
        ahk_id = self.run_script(script)
        return Window(engine=self, ahk_id=ahk_id, encoding=encoding)

    def _win_set(self, subcommand, *args, blocking=True):
        script = self.render_template(
            'window/set.ahk',  subcommand=subcommand, *args, blocking=blocking)
        return script

    def win_set(self, subcommand, *args, blocking=True):
        script = self.render_template(
            'window/set.ahk',  subcommand=subcommand, *args, blocking=blocking)
        self.run_script(script, blocking=blocking)

    @property
    def active_window(self):
        return self.win_get(title='A')

    def get_active_window(self):
        return self.active_window

    def _all_window_ids_(self):
        script = self.render_template('window/id_list.ahk')
        return script
    def _all_window_ids(self):
        script = self._all_window_ids_()
        result = self.run_script(script)
        return result.split('\n')[:-1]  # last one is always an empty string

    def windows(self):
        """
        Returns a list of windows

        :return:
        """
        windowze = []
        for ahk_id in self._all_window_ids():
            win = Window(engine=self, ahk_id=ahk_id, encoding=self.window_encoding)
            windowze.append(win)
        return windowze

    def find_windows(self, func=None, **kwargs):
        """
        Find all matching windows
        
        :param func: a callable to filter windows
        :param bool exact: if False (the default) partial matches are found. If True, only exact matches are returned
        :param kwargs: keywords of attributes of the window (has no effect if ``func`` is provided)
        
        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects. 
        """
        if func is None:
            exact = kwargs.pop('exact', False)

            def func(win):
                for attr, expected in kwargs.items():
                    if exact:
                        result = getattr(win, attr) == expected
                    else:
                        result = expected in getattr(win, attr)
                    if result is False:
                        return False
                return True
        for window in filter(func, self.windows()):
            yield window

    def find_window(self, func=None, **kwargs):
        """
        Like ``find_windows`` but only returns the first found window
        
        
        :param func: 
        :param kwargs: 
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """
        with suppress(StopIteration):
            return next(self.find_windows(func=func, **kwargs))

    def find_windows_by_title(self, title, exact=False):
        """
        Equivalent to ``find_windows(title=title)```
        
        Note that ``title`` is a ``bytes`` object
        
        :param bytes title: 
        :param exact: 
        :return: 
        """
        for window in self.find_windows(title=title, exact=exact):
            yield window

    def find_window_by_title(self, *args, **kwargs):
        """
        Like ``find_windows_by_title`` but only returns the first result.
        
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """
        with suppress(StopIteration):
            return next(self.find_windows_by_title(*args, **kwargs))

    def find_windows_by_text(self, text, exact=False):
        """
        
        :param text: 
        :param exact: 
        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects. 
        """
        for window in self.find_windows(text=text, exact=exact):
            yield window

    def find_window_by_text(self, *args, **kwargs):
        """
        
        :param args: 
        :param kwargs: 
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found 
        """
        with suppress(StopIteration):
            return next(self.find_windows_by_text(*args, **kwargs))

    def find_windows_by_class(self, class_name, exact=False):
        """
        
        :param class_name: 
        :param exact: 
        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects. 
        """
        for window in self.find_windows(class_name=class_name, exact=exact):
            yield window

    def find_window_by_class(self, *args, **kwargs):
        """
        
        :param args: 
        :param kwargs: 
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found 
        """
        with suppress(StopIteration):
            return next(self.find_windows_by_class(*args, **kwargs))


class AsyncWindow(Window, metaclass=AsyncifyMeta):
    # these methods are converted to async compatible versions automatically
    _asyncifiable = ['disable',
                    'enable',
                    'redraw',
                    'to_bottom',
                    'to_top',
                    'activate',
                    'activate_bottom',
                    'close',
                    'hide',
                    'kill',
                    'maximize',
                    'minimize',
                    'restore',
                    'show',
                    'wait',
                    'wait_active',
                    'wait_not_active',
                    'wait_close',
                    ]

    @classmethod
    async def from_mouse_position(cls, engine: ScriptEngine, **kwargs):
        script = engine.render_template('window/from_mouse.ahk')
        ahk_id = await engine.a_run_script(script)
        return cls(engine=engine, ahk_id=ahk_id, **kwargs)

    @classmethod
    async def from_pid(cls, engine: ScriptEngine, pid, **kwargs):
        script = engine.render_template('window/get.ahk',
                                        subcommand="ID",
                                        title=f'ahk_pid {pid}')
        ahk_id = await engine.a_run_script(script)
        return cls(engine=engine, ahk_id=ahk_id, **kwargs)

    def __getattr__(self, item):
        if item in self._get_subcommands:
            raise AttributeError(f"Unaccessable Attribute. Use get({item}) instead")
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{item}'")


    async def get(self, subcommand):
        script = self._get(subcommand)
        return await self.engine.a_run_script(script)

    async def set(self, subcommand, value):
        script = self._set(subcommand, value)
        await self.engine.a_run_script(script)

    async def get_pos(self):
        script = self._get_pos()
        resp = await self.engine.a_run_script(script)
        try:
            value = ast.literal_eval(resp)
            return value
        except SyntaxError:
            raise WindowNotFoundError('No window found')
    @staticmethod
    async def _loop():
        return asyncio.get_event_loop()

    @property
    async def rect(self):
        warnings.warn("rect property blocks event loop. Use get_rect() instead", stacklevel=2)
        return await self.get_pos()

    @rect.setter
    def rect(self, new_position):
        warnings.warn("rect setter only schedules coroutine. window may not change immediately. Use move() instead", stacklevel=2)
        x, y, width, height = new_position
        coro = self.move(x=x, y=y, width=width, height=height)
        asyncio.create_task(coro)

    @property
    async def position(self):
        warnings.warn("position property blocks event loop. Use get_rect() instead", stacklevel=2)
        x, y, _, _ = await self.get_pos()
        return x, y

    @position.setter
    def position(self, new_position):
        warnings.warn("position setter only schedules coroutine. window may not change immediately. use move() instead", stacklevel=2)
        x, y = new_position
        coro = self.move(x, y)
        asyncio.create_task(coro)

    @property
    async def width(self):
        warnings.warn("width property blocks event loop. Use get_rect() instead", stacklevel=2)
        _, _, width, _ = await self.get_pos()
        return width

    @width.setter
    def width(self, new_width):
        warnings.warn("width setter only schedules coroutine. window may not change immediately. use move() instead", stacklevel=2)
        coro = self.move(width=new_width)
        asyncio.create_task(coro)

    @property
    async def height(self):
        warnings.warn("height property blocks event loop. Use get_rect() instead", stacklevel=2)
        _, _, _, height = await self.get_pos()
        return height

    @height.setter
    def height(self, new_height):
        warnings.warn("height setter only schedules coroutine. window may not change immediately. use move() instead", stacklevel=2)
        coro = self.move(height=new_height)
        asyncio.create_task(coro)

    async def _base_property(self, command):
        script = self._base_check(command)
        resp = await self.engine.a_run_script(script)
        return bool(ast.literal_eval(resp))

    @property
    async def active(self):
        warnings.warn("active property blocks event loop. Use is_active() instead", stacklevel=2)
        return await self._base_property(command="WinActive")
    @property
    async def exist(self):
        warnings.warn("exist property blocks event loop. Use exists() instead", stacklevel=2)
        return await self._base_property(command="WinExist")

    async def exists(self):
        return await self._base_property('WinExist')

    async def _base_get_method(self, command):
        script = self._base_get_method_(command)
        result = await self.engine.a_run_script(script, decode=False)
        if self.encoding:
            return result.decode(encoding=self.encoding)
        return result

    @property
    async def title(self):
        warnings.warn("title property blocks event loop. Use get_title() instead", stacklevel=2)
        return await self._base_get_method("WinGetTitle")

    async def get_title(self):
        await self._base_get_method("WinGetTitle")

    async def set_title(self, value):
        script = self._set_title(value)
        await self.engine.a_run_script(script)

    @title.setter
    def title(self, new_title):
        warnings.warn("title setter only schedules coroutine. window may not change immediately. use set_title() instead", stacklevel=2)
        coro = self.set_title(new_title)
        asyncio.create_task(coro)

    @property
    async def class_name(self):
        warnings.warn("class_name property blocks event loop. use get_class_name() instead.")
        return await self._base_get_method("WinGetClass")

    async def get_class_name(self):
        return await self._base_get_method("WinGetClass")

    @property
    async def text(self):
        warnings.warn("text property blocks event loop. use get_text() instead.")
        return await self._base_get_method("WinGetText")

    async def get_text(self):
        return await self._base_get_method("WinGetText")

    @property
    async def minimized(self):
        warnings.warn('property blocks event loop. use is_minimized() instead')
        return await self.get("MinMax") == self.MINIMIZED

    @property
    async def maximized(self):
        warnings.warn('property blocks event loop. use is_maximized() instead')
        return await self.get("MinMax") == self.MAXIMIZED

    async def is_minimized(self):
        return await self._base_get_method("MinMax") == self.MINIMIZED

    async def is_maximized(self):
        return await self._base_get_method("MinMax") == self.MAXIMIZED

    @property
    async def non_max_non_min(self):
        warnings.warn('property blocks event loop. use is_minmax() instead')
        return await self.get("MinMax") == self.NON_MIN_NON_MAX

    async def is_minmax(self):
        return await self.get("MinMax") != self.NON_MIN_NON_MAX

    @property
    async def transparent(self) -> int:
        warnings.warn('property blocks event loop. use get_transparency() instead')
        result = await self.get("Transparent")
        if result:
            return int(result)
        else:
            return 255

    @transparent.setter
    def transparent(self, value):
        warnings.warn("transparent setter only schedules coroutine. window may not change immediately. use set_transparency() instead", stacklevel=2)

        if isinstance(value, int) and 0 <= value <= 255:
            coro = self.set("Transparent", value)
            asyncio.create_task(coro)
        else:
            raise ValueError('transparency must be integer in range [0, 255]')

    async def get_transparency(self) -> int:
        result = await self.get("Transparent")
        if result:
            return int(result)
        else:
            return 255

    async def set_transparency(self, value):
        if isinstance(value, int) and 0 <= value <= 255:
            await self.set("Transparent", value)
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use [0, 255] integer')

    @property
    async def always_on_top(self) -> bool:
        warnings.warn("always_on_top property blocks event loop. use is_always_on_top() instead")
        script = self._always_on_top()
        resp = await self.engine.a_run_script(script)
        return bool(ast.literal_eval(resp))

    async def is_always_on_top(self):
        script = self._always_on_top()
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

    @always_on_top.setter
    def always_on_top(self, value):
        warnings.warn(f"always_on_top setter only schedules coroutine. changes may not happen immediately. use set_always_on_top({repr(value)}) instead")
        if value in ('on', 'On', True, 1):
            coro = self.set('AlwaysOnTop', 'On')
        elif value in ('off', 'Off', False, 0):
            coro = self.set('AlwaysOnTop', 'Off')
        elif value in ('toggle', 'Toggle', -1):
            coro = self.set('AlwaysOnTop', 'Toggle')
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use On/Off/Toggle/True/False/0/1/-1')
        asyncio.create_task(coro)

    async def set_always_on_top(self, value):
        if value in ('on', 'On', True, 1):
            await self.set('AlwaysOnTop', 'On')
        elif value in ('off', 'Off', False, 0):
            await self.set('AlwaysOnTop', 'Off')
        elif value in ('toggle', 'Toggle', -1):
            await self.set('AlwaysOnTop', 'Toggle')
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use On/Off/Toggle/True/False/0/1/-1')

    async def move(self, x='', y='', width=None, height=None):
        script = self._move(x=x, y=y, width=width, height=height)
        return await self.engine.a_run_script(script)

    async def send(self, keys, delay=10, raw=False, blocking=True, escape=False, press_duration=-1):
        script = self._send(keys, delay=delay, raw=raw, blocking=blocking, escape=escape, press_duration=press_duration)
        return await self.engine.a_run_script(script, blocking=blocking)

    async def _base_method(self, command, seconds_to_wait="", blocking=False):
        script = self._base_method_(command, seconds_to_wait=seconds_to_wait)
        return await self.engine.a_run_script(script, blocking=blocking)


class AsyncWindowMixin(WindowMixin):
    async def win_get(self, *args, **kwargs):
        encoding = kwargs.pop('encoding', self.window_encoding)
        script = self._win_get(*args, **kwargs)
        ahk_id = await self.a_run_script(script)
        return AsyncWindow(engine=self, ahk_id=ahk_id, encoding=encoding)

    async def win_set(self, subcommand, *args, blocking=True):
        script = self.render_template(
            'window/set.ahk',  subcommand=subcommand, *args, blocking=blocking)
        await self.a_run_script(script, blocking=blocking)

    @property
    def active_window(self):
        warnings.warn("active_window property blocks event loop. use get_active_window() instead")
        return self.win_get(title='A')

    async def _all_window_ids(self):
        script = self._all_window_ids_()
        result = await self.a_run_script(script)
        return result.split('\n')[:-1]  # last one is always an empty string

    async def windows(self):
        """
        Returns a list of windows

        :return:
        """
        windowze = []
        for ahk_id in await self._all_window_ids():
            win = AsyncWindow(engine=self, ahk_id=ahk_id, encoding=self.window_encoding)
            windowze.append(win)
        return windowze

    async def find_windows(self, func=None, **kwargs):
        """
        Find all matching windows

        :param func: a callable to filter windows
        :param bool exact: if False (the default) partial matches are found. If True, only exact matches are returned
        :param kwargs: keywords of attributes of the window (has no effect if ``func`` is provided)

        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects.
        """
        if func is None:
            exact = kwargs.pop('exact', False)

            async def func(win):
                for attr, expected in kwargs.items():
                    if exact:
                        result = await getattr(win, attr) == expected
                    else:
                        result = expected in await getattr(win, attr)
                    if result is False:
                        return False
                return True
        async for window in async_filter(func, await self.windows()):
            yield window

    async def find_window(self, func=None, **kwargs):
        """
        Like ``find_windows`` but only returns the first found window


        :param func:
        :param kwargs:
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """
        async for window in self.find_windows(func=func, **kwargs):
            return window  # return the first result
        raise WindowNotFoundError("yikes")

    async def find_windows_by_title(self, title, exact=False):
        """
        Equivalent to ``find_windows(title=title)```

        Note that ``title`` is a ``bytes`` object

        :param bytes title:
        :param exact:
        :return:
        """
        async for window in self.find_windows(title=title, exact=exact):
            yield window

    async def find_window_by_title(self, title):
        """
        Like ``find_windows_by_title`` but only returns the first result.

        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """

        async for window in self.find_windows_by_title():
            return window

    async def find_windows_by_text(self, text, exact=False):
        """

        :param text:
        :param exact:
        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects.
        """
        async for window in self.find_windows(text=text, exact=exact):
            yield window

    async def find_window_by_text(self, *args, **kwargs):
        """

        :param args:
        :param kwargs:
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """
        async for window in self.find_windows_by_text(*args, **kwargs):
            return window

    async def find_windows_by_class(self, class_name, exact=False):
        """

        :param class_name:
        :param exact:
        :return: a generator containing any matching :py:class:`~ahk.window.Window` objects.
        """
        async for window in self.find_windows(class_name=class_name, exact=exact):
            yield window

    async def find_window_by_class(self, *args, **kwargs):
        """
        :param args:
        :param kwargs:
        :return: a :py:class:`~ahk.window.Window` object or ``None`` if no matching window is found
        """
        async for window in self.find_windows_by_class(*args, **kwargs):
            return window

