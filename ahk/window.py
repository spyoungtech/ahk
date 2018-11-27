from ahk.script import ScriptEngine
from ahk.utils import make_script
import ast


class WindowNotFoundError(ValueError):
    pass


class Window(object):
    def __init__(self, engine, title='', text='', exclude_title='', exclude_text='', match_mode=None):
        self.engine = engine
        if title is None and text is None:
            raise ValueError
        self._title = title
        self._text = text
        self._exclude_title = exclude_title
        self._exclude_text = exclude_text
        self.match_mode = match_mode

    def _win_set(self, subcommand, value):
        script = make_script(f'''\
        WinSet, {subcommand}, {value}, {self.title}, {self.text, self._exclude_title, self._exclude_text}
        ''')
        return script

    def win_set(self, *args, **kwargs):
        script = self._win_set(*args, **kwargs)
        self.engine.run_script(script)

    def _position(self):
        return make_script(f'''
        WinGetPos, x, y, width, height, {self.title}, {self.text}, {self._exclude_title}, {self._exclude_text}
        s .= Format("({{}}, {{}}, {{}}, {{}})", x, y, width, height)
        FileAppend, %s%, *
        ''')

    def _get_pos(self):
        resp = self.engine.run_script(self._position())
        try:
            value = ast.literal_eval(resp)
            return value
        except SyntaxError:
            raise WindowNotFoundError('No window found')

    @property
    def position(self):
        x, y, _, _ = self._get_pos()
        return x, y

    @property
    def width(self):
        _, _, width, _ = self._get_pos()
        return width

    @property
    def height(self):
        _, _, _, height = self._get_pos()
        return height

    def disable(self):
        self.win_set('Disable', '')

    def enable(self):
        self.win_set('Enable', '')

    def redraw(self):
        raise NotImplemented

    @property
    def title(self):
        return self._title

    @property
    def text(self):
        return ''

    def style(self):
        raise NotImplemented

    def ex_style(self):
        raise NotImplemented

    def _always_on_top(self):
        return make_script(f'''
        WinGet, ExStyle, ExStyle, {self._title}, {self._text}, {self._exclude_title}, {self._exclude_text}
        if (ExStyle & 0x8)  ; 0x8 is WS_EX_TOPMOST.
            FileAppend, 1, *
        else
            FileAppend, 0, *
        ''')

    @property
    def always_on_top(self):
        resp = self.engine.run_script(self._always_on_top())
        return bool(ast.literal_eval(resp))

    @always_on_top.setter
    def always_on_top(self, value):
        if value in ('On', True, 1):
            self.win_set('AlwaysOnTop', 'On')
        elif value in ('Off', False, 0):
            self.win_set('AlwaysOnTop', 'Off')
        elif value == 'Toggle':
            self.win_set('AlwaysOnTop', 'Toggle')

    def _close(self, seconds_to_wait=''):
        return make_script(f'''\
        WinClose, {self.title}, {self.text}, {seconds_to_wait}, {self._exclude_title}, {self._exclude_text}

        ''')

    def close(self, seconds_to_wait=''):
        self.engine.run_script(self._close(seconds_to_wait=seconds_to_wait))

    def to_bottom(self):
        """
        Sent
        :return:
        """
        self.win_set('Bottom', '')

    def to_top(self):
        self.win_set('Top', '')


class WindowMixin(ScriptEngine):
    def win_get(self, *args, **kwargs):
        return Window(engine=self, *args, **kwargs)

    @property
    def active_window(self):
        return Window(engine=self, title='A')

    def win_set(self, subcommand, value, **windowkwargs):
        win = Window(engine=self, **windowkwargs)
        win.win_set(subcommand, value)
        return win

    def windows(self):
        """
        Return a list of all windows
        :return:
        """
        raise NotImplemented
