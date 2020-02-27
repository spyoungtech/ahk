import ast
from contextlib import suppress

from ahk.script import ScriptEngine
from ahk.utils import escape_sequence_replace, make_logger

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

    def get(self, subcommand):
        sub = self._get_subcommands.get(subcommand)
        if not sub:
            raise ValueError(f'No such subcommand {subcommand}')

        script = self._render_template(
            'window/get.ahk',
            subcommand=sub,
            title=f"ahk_id {self.id}",
        )

        return self.engine.run_script(script)

    def __repr__(self):
        return f'<ahk.window.Window ahk_id={self.id}>'

    def set(self, subcommand, value):
        sub = self._set_subcommands.get(subcommand)
        if not sub:
            raise ValueError(f'No such subcommand {subcommand}')

        script = self._render_template(
            'window/win_set.ahk',
            subcommand=subcommand,
            value=value,
            title=f"ahk_id {self.id}"
        )
        return self.engine.run_script(script)

    def _get_pos(self):
        script = self._render_template(
            'window/win_position.ahk',
            title=f"ahk_id {self.id}"
        )
        resp = self.engine.run_script(script)
        try:
            value = ast.literal_eval(resp)
            return value
        except SyntaxError:
            raise WindowNotFoundError('No window found')

    @property
    def rect(self):
        return self._get_pos()

    @rect.setter
    def rect(self, new_position):
        x, y, width, height = new_position
        self.move(x=x, y=y, width=width, height=height)

    @property
    def position(self):
        x, y, _, _ = self._get_pos()

        return x, y

    @position.setter
    def position(self, new_position):
        x, y = new_position
        self.move(x, y)

    @property
    def width(self):
        _, _, width, _ = self._get_pos()
        return width

    @width.setter
    def width(self, new_width):
        self.move(width=new_width)

    @property
    def height(self):
        _, _, _, height = self._get_pos()
        return height

    @height.setter
    def height(self, new_height):
        self.move(height=new_height)

    def _base_property(self, command):
        script = self._render_template(
            "window/base_check.ahk",
            command=command,
            title=f"ahk_id {self.id}"
        )
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

    @property
    def active(self):
        return self._base_property(command="WinActive")

    @property
    def exist(self):
        return self._base_property(command="WinExist")

    def _base_get_method(self, command):
        script = self._render_template(
            "window/base_get_command.ahk",
            command=command,
            title=f"ahk_id {self.id}"
        )
        result = self.engine.run_script(script, decode=False)
        if self.encoding:
            return result.stdout.decode(encoding=self.encoding)
        return result.stdout

    @property
    def title(self):
        return self._base_get_method("WinGetTitle")

    @title.setter
    def title(self, value):
        script = self._render_template(
            "window/win_set_title.ahk",
            title=f"ahk_id {self.id}",
            new_title=value
        )
        return self.engine.run_script(script)

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

    @property
    def non_max_non_min(self):
        return self.get("MinMax") == self.NON_MIN_NON_MAX

    @property
    def transparent(self) -> int:
        result = self.get("Transparent")
        if result:
            return int(result)
        else:
            return 255

    @transparent.setter
    def transparent(self, value):
        if isinstance(value, int) and 0 <= value <= 255:
            self.set("Transparent", value)
        else:
            raise ValueError(
                f'"{value}" not a valid option. Please use [0, 255] integer')

    @property
    def always_on_top(self) -> bool:
        script = self._render_template(
            'window/win_is_always_on_top.ahk',
            title=f"ahk_id {self.id}"
        )
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

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

    def disable(self):
        self.set('Disable', '')

    def enable(self):
        self.set('Enable', '')

    def redraw(self):
        self.set('Redraw', '')

    def to_bottom(self):
        """
        Send window to bottom (behind other windows)
        :return:
        """
        self.set('Bottom', '')

    def to_top(self):
        self.set('Top', '')

    def _render_template(self, *args, **kwargs):
        kwargs['win'] = self
        return self.engine.render_template(*args, **kwargs)

    def _base_method(self, command, seconds_to_wait="", blocking=False):
        script = self._render_template(
            "window/base_command.ahk",
            command=command,
            title=f"ahk_id {self.id}",
            seconds_to_wait=seconds_to_wait
        )

        return self.engine.run_script(script, blocking=blocking)

    def activate(self):
        self._base_method("WinActivate")

    def activate_buttom(self):
        self._base_method("WinActivateBottom")

    def close(self, seconds_to_wait=""):
        self._base_method("WinClose", seconds_to_wait=seconds_to_wait)

    def hide(self):
        self._base_method("WinHide")

    def kill(self, seconds_to_wait=""):
        self._base_method("WinKill", seconds_to_wait=seconds_to_wait)

    def maximize(self):
        self._base_method("WinMaximize")

    def minimize(self):
        self._base_method("WinMinimize")

    def restore(self):
        self._base_method("WinRestore")

    def show(self):
        self._base_method("WinShow")

    def wait(self, seconds_to_wait=""):
        self._base_method("WinWait", seconds_to_wait=seconds_to_wait, blocking=True)

    def wait_active(self, seconds_to_wait=""):
        self._base_method("WinWaitActive", seconds_to_wait=seconds_to_wait, blocking=True)

    def wait_not_active(self, seconds_to_wait=""):
        self._base_method("WinWaitNotActive", seconds_to_wait=seconds_to_wait, blocking=True)

    def wait_close(self, seconds_to_wait=""):
        self._base_method("WinWaitClose", seconds_to_wait=seconds_to_wait, blocking=True)

    def move(self, x='', y='', width=None, height=None):
        script = self._render_template(
            'window/win_move.ahk',
            title=f"ahk_id {self.id}",
            x=x, y=y, width=width, height=height
        )
        self.engine.run_script(script)

    def send(self, keys, delay=None, raw=False, blocking=False, escape=False):
        """
        Send keystrokes directly to the window.
        Uses ControlSend
        https://autohotkey.com/docs/commands/Send.htm
        """
        if escape:
            keys = escape_sequence_replace(keys)
        script = self._render_template(
            'window/win_send.ahk',
            title=f"ahk_id {self.id}",
            keys=keys, raw=raw, delay=delay, blocking=blocking
        )
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

    def win_get(self, title='', text='', exclude_title='', exclude_text='', encoding=None):
        encoding = encoding or self.window_encoding
        script = self.render_template(
            'window/get.ahk',
            subcommand='ID',
            title=title,
            text=text,
            exclude_text=exclude_text,
            exclude_title=exclude_title
        )
        ahk_id = self.run_script(script)
        return Window(engine=self, ahk_id=ahk_id, encoding=encoding)

    def win_set(self, subcommand, *args, blocking=True):
        script = self.render_template(
            'window/set.ahk',  subcommand=subcommand, *args, blocking=blocking)
        self.run_script(script, blocking=blocking)

    @property
    def active_window(self):
        return self.win_get(title='A')

    def _all_window_ids(self):
        script = self.render_template('window/id_list.ahk')
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
        with suppress(StopIteration):
            return next(self.find_windows(func=func, **kwargs))

    def find_windows_by_title(self, title, exact=False):
        for window in self.find_windows(title=title, exact=exact):
            yield window

    def find_window_by_title(self, *args, **kwargs):
        with suppress(StopIteration):
            return next(self.find_windows_by_title(*args, **kwargs))

    def find_windows_by_text(self, text, exact=False):
        for window in self.find_windows(text=text, exact=exact):
            yield window

    def find_window_by_text(self, *args, **kwargs):
        with suppress(StopIteration):
            return next(self.find_windows_by_text(*args, **kwargs))

    def find_windows_by_class(self, class_name, exact=False):
        for window in self.find_windows(class_name=class_name, exact=exact):
            yield window

    def find_window_by_class(self, *args, **kwargs):
        with suppress(StopIteration):
            return next(self.find_windows_by_class(*args, **kwargs))
