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
    """
    Resolve a string of a button name to a canonical name used for AHK script

    :param button:
    :type button: str
    :return:
    """
    if isinstance(button, str):
        button = button.lower()

    if button in _BUTTONS:
        button = _BUTTONS.get(button)
    elif isinstance(button, int) and button > 3:
        #  for addtional mouse buttons
        button = f'X{button-3}'
    return button


class MouseMixin(ScriptEngine):
    """
    Provides mouse functionality for the AHK class
    """
    def __init__(self, mouse_speed=2, mode=None, **kwargs):
        """

        :param mouse_speed: default mouse speed
        :param mode:
        :param kwargs:
        """
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
        if callable(speed):
            speed = speed()
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
        """
        REF: https://www.autohotkey.com/docs/commands/MouseMove.htm

        :param x: the x coordinate to move to. If omitted, current position is used
        :param y: the y coordinate to move to. If omitted, current position is used
        :param speed: 0 (fastest) to 100 (slowest). Can be a callable or string AHK expression
        :param relative: Move the mouse realtive to current position rather than absolute x,y coordinates
        :param mode:
        :param blocking:
        :return:

        """
        blocking = kwargs.get('blocking', True)
        script = self._mouse_move(*args, **kwargs)
        self.run_script(script, blocking=blocking)

    def _click(self, *args, mode=None, blocking=True):
        if mode is None:
            mode = self.mode
        return self.render_template('mouse/click.ahk', args=args, mode=mode, blocking=blocking)

    def click(self, x=None, y=None, *, button=None, n=None, direction=None, relative=None, blocking=True, mode=None):
        """
        Click mouse button at a specified position. REF: https://www.autohotkey.com/docs/commands/Click.htm

        :param x:
        :param y:
        :param button:
        :param n: number of times to click the button
        :param direction:
        :param relative:
        :param blocking:
        :param mode:
        :return:
        """
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
        """
        Convenience function to double click, equivalent to ``click`` with ``n=2``

        :param args:
        :param kwargs:
        :return:
        """
        n = kwargs.get('n', 1)
        kwargs['n'] = n * 2
        self.click(*args, **kwargs)

    def right_click(self, *args, **kwargs):
        """
        Convenience function clicking right mouse button. Equivalent to ``click`` with ``button='R'``

        :param args:
        :param kwargs:
        :return:
        """
        kwargs['button'] = 2
        self.click(*args, **kwargs)

    def mouse_wheel(self, direction, *args, **kwargs):
        """
        Convenience function for 'clicking' the mouse wheel in a given direction.

        :param direction: the string 'up' or 'down'
        :param args: args passed to ``click``
        :param kwargs: keyword args passed to ``click``
        :return:
        """
        assert direction in ('up', 'down')
        kwargs['button'] = f'Wheel{direction}'
        self.click(*args, **kwargs)

    def wheel_up(self, *args, **kwargs):
        """
        Convenience function for ``click`` with wheel up button

        :param args:
        :param kwargs:
        :return:
        """
        self.mouse_wheel('up', *args, **kwargs)

    def wheel_down(self, *args, **kwargs):
        """
        Convenience function for ``click`` with wheel down button

        :param args:
        :param kwargs:
        :return:
        """
        self.mouse_wheel('down', *args, **kwargs)

    def mouse_drag(self, x, y=None, *, from_position=None, speed=None, button=1, relative=None, blocking=True, mode=None):
        """
        Click and drag the mouse

        :param x:
        :param y:
        :param from_position: (x,y) tuple of an optional starting position. Current position is used if omitted
        :param speed:
        :param button: The button the click and drag; defaults to left mouse button
        :param relative: click and drag to a relative position rather than an absolute position
        :param blocking:
        :param mode:
        :return:
        """
        if from_position is None:
            x1, y1 = self.mouse_position
        else:
            x1, y1 = from_position

        if y is None:
            x2, y2 = x
        else:
            x2 = x
            y2 = y

        if relative:
            x1, y1 = (0, 0)

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
