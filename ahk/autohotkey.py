import atexit
from collections import deque
from ahk.mouse import MouseMixin
from ahk.window import Window, WindowMixin
from ahk.script import ScriptEngine
from ahk.screen import ScreenMixin
from ahk.keyboard import KeyboardMixin
from ahk.sound import SoundMixin
from ahk.communication import EventListener

class AHK(WindowMixin, MouseMixin, KeyboardMixin, ScreenMixin, SoundMixin):

    def __init__(self, *args, **kwargs):
        super().__init__(self, *args, **kwargs)
        is_main = kwargs.pop("use_event_loop", None)
        if is_main == None:
            self.EventListener = EventListener()
        atexit.register(self._on_exit)
        
    def _on_exit(self):
        if self.EventListener:
            self.EventListener.stop()


class ActionChain(AHK):
    def __init__(self, *args, **kwargs):
        self._actions = deque()
        kwargs.append("use_event_loop", True)
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
        script = self.render_template('base.ahk', body=f'Sleep {n}', directives={'#Persistent',})
        self.run_script(script)
