from ahk.script import ScriptEngine
import ast
from .utils import make_logger

logger = make_logger(__name__)


class WindowNotFoundError(ValueError):
    pass


class Window(object):
    def __init__(self, engine: ScriptEngine, title='', text='', exclude_title='', exclude_text='', match_mode=None):
        self.engine = engine
        if title is None and text is None:
            raise ValueError
        self._title = title
        self._text = text
        self._exclude_title = exclude_title
        self._exclude_text = exclude_text
        self.match_mode = match_mode

    @classmethod
    def from_ahk_id(cls, engine, ahk_id):
        raise NotImplemented

    def _win_set(self, subcommand, value):
        script = self.engine.render_template(win=self, subcommand=subcommand, value=value)
        return script

    def win_set(self, *args, **kwargs):
        script = self._win_set(*args, **kwargs)
        self.engine.run_script(script)

    def _position(self):
        return self.engine.render_template('window/position.ahk', win=self)

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
        return self.engine.render_template('window/is_always_on_top.ahk', win=self)

    @property
    def always_on_top(self):
        resp = self.engine.run_script(self._always_on_top())
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

    def _close(self, seconds_to_wait=''):
        return self.engine.render_template('window/close.ahk', win=self, seconds_to_wait=seconds_to_wait)

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

    def _win_title_from_ahk_id(self, ahk_id):
        pass

    def _all_window_titles(self):
        script = self.render_template('window/title_list.ahk')
        result = self.run_script(script, decode=False)
        resp = result.stdout
        titles = []
        for title_bytes in resp.split(bytes('\n', 'ascii')):  # FIXME
            if not title_bytes.strip():
                continue
            try:
                titles.append(title_bytes.decode())
            except UnicodeDecodeError as e:
                logger.exception('Could not decode title; %s', str(e))

        return titles

    def windows(self):
        """
        Return a list of all windows
        :return:
        """
        return [self.win_get(title=title) for title in self._all_window_titles()]