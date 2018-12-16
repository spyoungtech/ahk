from collections import namedtuple
from ahk.script import ScriptEngine
from ahk.utils import make_logger
import ast

logger = make_logger(__name__)


_BUTTONS = {
    1: 'L',
    2: 'R',
    3: 'M',
    'left': 'L',
    'right': 'R',
    'middle': 'M',
    'wheelup': 'WU',
    'wheeldown': 'WD',
    'wheelleft': 'WL',
    'wheelright': 'WR',
}

def resolve_button(button):
    if isinstance(button, str):
        button = button.lower()

    if button in _BUTTONS:
        button = _BUTTONS.get(button)
    elif isinstance(button, int) and button > 3:
        #  for addtional mouse buttons
        button = f'X{button-3}'
    return button


class MouseMixin(ScriptEngine):
    def __init__(self, mouse_speed=2, mode=None, **kwargs):
        if mode is None:
            mode = 'Screen'
        self.mode = mode
        self._mouse_speed = mouse_speed
        super().__init__(**kwargs)

    @property
    def mouse_speed(self):
        if callable(self._mouse_speed):
            return self._mouse_speed()
        else:
            return self._mouse_speed

    @mouse_speed.setter
    def mouse_speed(self, value):
        self._mouse_speed = value

    def _mouse_position(self, mode=None):
        if mode is None:
            mode = self.mode
        return self.render_template('mouse/mouse_position.ahk', mode=mode)

    @property
    def mouse_position(self):
        script = self._mouse_position()
        response = self.run_script(script)
        return ast.literal_eval(response)

    @mouse_position.setter
    def mouse_position(self, position):
        x, y = position
        self.mouse_move(x=x, y=y, speed=0, relative=False)

    def _mouse_move(self, x=None, y=None, speed=None, relative=False, mode=None, blocking=True):
        if x is None and y is None:
            raise ValueError('Position argument(s) missing. Must provide x and/or y coordinates')
        if speed is None:
            speed = self.mouse_speed
        if mode is None:
            mode = self.mode
        if relative and (x is None or y is None):
            x = x or 0
            y = y or 0
        elif not relative and (x is None or y is None):
            posx, posy = self.mouse_position
            x = x or posx
            y = y or posy

        return self.render_template('mouse/mouse_move.ahk', x=x, y=y, speed=speed, relative=relative, mode=mode, blocking=blocking)

    def mouse_move(self, *args, **kwargs):
        blocking = kwargs.get('blocking', True)
        script = self._mouse_move(*args, **kwargs)
        print(script)
        self.run_script(script, blocking=blocking)

    def _click(self, *args, mode=None, blocking=True):
        if mode is None:
            mode = self.mode
        return self.render_template('mouse/click.ahk', args=args, mode=mode, blocking=blocking)

    def click(self, x=None, y=None, *, button=None, n=None, direction=None, relative=None, blocking=True, mode=None):
        if x or y:
            if y is None and not isinstance(x, int) and len(x) == 2:
                #  alow position to be specified by a two-sequence
                x, y = x
            assert x is not None and y is not None, 'If provided, position must be specified by x AND y'

        button = resolve_button(button)

        if relative:
            relative = 'Rel'
        args = [arg for arg in (x, y, button, n, direction, relative) if arg is not None]
        script = self._click(*args, blocking=blocking, mode=mode)
        self.run_script(script, blocking=blocking)

    def double_click(self, *args, **kwargs):
        n = kwargs.get('n', 1)
        kwargs['n'] = n * 2
        self.click(*args, **kwargs)

    def right_click(self, *args, **kwargs):
        kwargs['button'] = 2
        self.click(*args, **kwargs)

    def mouse_wheel(self, direction, *args, **kwargs):
        assert direction in ('up', 'down')
        kwargs['button'] = f'Wheel{direction}'
        self.click(*args, **kwargs)

    def wheel_up(self, *args, **kwargs):
        self.mouse_wheel('up', *args, **kwargs)

    def wheel_down(self, *args, **kwargs):
        self.mouse_wheel('down', *args, **kwargs)

    def mouse_drag(self, x, y=None, *, from_position=None, speed=None, button=1, relative=None, blocking=True, mode=None):
        if from_position is None:
            x1, y1 = self.mouse_position
        else:
            x1, y1 = from_position

        if y is None:
            x2, y2 = x
        else:
            x2 = x
            y2 = y

        button = resolve_button(button)

        if speed is None:
            speed = self.mouse_speed

        if mode is None:
            mode = self.mode

        script = self.render_template('mouse/mouse_drag.ahk',
                                      button=button,
                                      x1=x1,
                                      y1=y1,
                                      x2=x2,
                                      y2=y2,
                                      speed=speed,
                                      relative=relative,
                                      blocking=blocking,
                                      mode=mode)

        self.run_script(script, blocking=blocking)
