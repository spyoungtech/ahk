from ahk.utils import make_script
from ahk.script import ScriptEngine
import ast


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


    def _mouse_position(self, mode=None):
        if mode is None:
            mode = self.mode
        return make_script(f'''
        CoordMode, Mouse, {mode}
        MouseGetPos, xpos, ypos
        s .= Format("({{}}, {{}})", xpos, ypos)
        FileAppend, %s%, *
        ''')

    @property
    def mouse_position(self):
        response = self.run_script(self._mouse_position())
        return ast.literal_eval(response)

    @mouse_position.setter
    def mouse_position(self, position):
        x, y = position
        self.mouse_move(x=x, y=y, speed=0, relative=False)

    def _mouse_move(self, x=None, y=None, speed=None, relative=False, mode=None, persistent=True, blocking=True):
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

        if relative:
            relative = ', R'
        else:
            relative = ''
        script = make_script(f'''
            CoordMode Mouse, {mode}
            MouseMove, {x}, {y} , {speed}{relative}
        ''', persistent=persistent, blocking=blocking)
        return script

    def mouse_move(self, *args, **kwargs):
        blocking = kwargs.get('blocking', True)
        script = self._mouse_move(*args, **kwargs)
        self.run_script(script, blocking=blocking)
