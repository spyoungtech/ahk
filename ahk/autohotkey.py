from collections import deque
from ahk.mouse import MouseMixin
from ahk.window import Window, WindowMixin
from ahk.script import ScriptEngine
from ahk.screen import ScreenMixin
from ahk.keyboard import KeyboardMixin
from ahk.sound import SoundMixin
from ahk.registery import RegisteryMixin


class AHK(
    WindowMixin, MouseMixin, KeyboardMixin,
    ScreenMixin, SoundMixin, RegisteryMixin
):
    pass


class ActionChain(AHK):
    def __init__(self, *args, **kwargs):
        self._actions = deque()
        super().__init__(*args, **kwargs)

    def run_script(self, *args, **kwargs):
        """
        override run_script to defer to queue
        """
        kwargs['decode'] = False  #
        self._actions.appendleft((args, kwargs))

    def perform(self):
        results = []
        while self._actions:
            args, kwargs = self._actions.pop()
            results.append(super().run_script(*args, **kwargs))
        return results

    def sleep(self, n):
        """
        :param n: how long (in seconds) to sleep
        :return:
        """
        n = n * 1000  # convert to milliseconds
        script = self.render_template('base.ahk', body=f'Sleep {n}', directives={'#Persistent', })
        self.run_script(script)
