from ahk.script import ScriptEngine
import ast
from .utils import make_logger

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
    _subcommands = {
        'id': 'ID',
        'process_name': 'ProcessName',
        'pid': 'PID',
        'process_path': 'ProcessPath',
        'process': 'ProcessPath',
        'controls': 'ControlList',
        'controls_hwnd': 'ControlListHwnd',
        'transparency': 'Transparent',
        'trans_color': 'TransColor',
        'style': 'Style',   # This will probably get a property later
        'ex_style': 'ExStyle',  # This will probably get a property later
    }
    _subcommands.update({value: value for value in _subcommands.values()})

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
        if attr.lower() in self._subcommands:
            return self.get(attr)
        raise AttributeError(f"'{self.__class__.__name__}' object has no attribute '{attr}'")

    def get(self, subcommand):
        sub = self._subcommands.get(subcommand)
        if not sub:
            raise ValueError(f'No such subcommand {subcommand}')
        script = self._render_template('window/get.ahk',
                                       subcommand=sub,
                                       title=f'ahk_id {self.id}')

        return self.engine.run_script(script)

    def __repr__(self):
        return f'<ahk.window.Window ahk_id={self.id}>'

    def win_set(self, subcommand, value):
        script = self._render_template('window/win_set.ahk', subcommand=subcommand, value=value)
        self.engine.run_script(script)

    def _get_pos(self):
        script = self._render_template('window/win_position.ahk')
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

    def disable(self):
        self.win_set('Disable', '')

    def enable(self):
        self.win_set('Enable', '')

    def redraw(self):
        self.win_set('Redraw', '')

    @property
    def title(self):
        script = self._render_template('window/win_get_title.ahk')
        result = self.engine.run_script(script, decode=False)
        if self.encoding:
            return result.stdout.decode(encoding=self.encoding)
        return result.stdout

    @property
    def text(self):
        script = self._render_template('window/win_get_text.ahk')
        result = self.engine.run_script(script, decode=False)
        if self.encoding:
            return result.stdout.decode(encoding=self.encoding)
        return result.stdout

    @property
    def always_on_top(self):
        script = self.render_template('window/win_is_always_on_top.ahk')
        resp = self.engine.run_script(script)
        return bool(ast.literal_eval(resp))

    @always_on_top.setter
    def always_on_top(self, value):
        if value in ('on', 'On', True, 1):
            self.win_set('AlwaysOnTop', 'On')
        elif value in ('off', 'Off', False, 0):
            self.win_set('AlwaysOnTop', 'Off')
        elif value in ('toggle', 'Toggle', -1):
            self.win_set('AlwaysOnTop', 'Toggle')
        else:
            raise ValueError(f'"{value}" not a valid option. Please use On/Off/Toggle/True/False/0/1/-1')

    def close(self, seconds_to_wait=''):
        script = self._render_template('window/win_close.ahk', seconds_to_wait=seconds_to_wait)
        self.engine.run_script(script)

    def to_bottom(self):
        """
        Send window to bottom (behind other windows)
        :return:
        """
        self.win_set('Bottom', '')

    def to_top(self):
        self.win_set('Top', '')

    def _render_template(self, *args, **kwargs):
        kwargs['win'] = self
        return self.engine.render_template(*args, **kwargs)

    def activate(self):
        script = self._render_template('window/win_activate.ahk')
        self.engine.run_script(script)

    def move(self, x='', y='', width=None, height=None):
        script = self._render_template('window/win_move.ahk', x=x, y=y, width=width, height=height)
        self.engine.run_script(script)


class WindowMixin(ScriptEngine):
    def __init__(self, *args, **kwargs):
        self.window_encoding = kwargs.pop('window_encoding', None)
        super().__init__(*args, **kwargs)

    def win_get(self, title='', text='', exclude_title='', exclude_text='', encoding=None):
        encoding = encoding or self.window_encoding
        script = self.render_template('window/get.ahk',
                                      subcommand='ID',
                                      title=title,
                                      text=text,
                                      exclude_text=exclude_text,
                                      exclude_title=exclude_title)
        ahk_id = self.run_script(script)
        return Window(engine=self, ahk_id=ahk_id, encoding=encoding)

    def win_set(self, subcommand, *args, blocking=True):
        script = self.render_template('window/set.ahk',  subcommand=subcommand, *args, blocking=blocking)
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
        Generator of windows
        :return:
        """
        for ahk_id in self._all_window_ids():
            yield Window(engine=self, ahk_id=ahk_id, encoding=self.window_encoding)

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
        return next(self.find_windows(func=func, **kwargs))

    def find_windows_by_title(self, title, exact=False):
        for window in self.find_windows(title=title, exact=exact):
            yield window

    def find_window_by_title(self, *args, **kwargs):
        return next(self.find_windows_by_title(*args, **kwargs))

    def find_windows_by_text(self, text, exact=False):
        for window in self.find_windows(text=text, exact=exact):
            yield window

    def find_window_by_text(self, *args, **kwargs):
        return next(self.find_windows_by_text(*args, **kwargs))
