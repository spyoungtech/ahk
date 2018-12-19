from collections import deque
from ahk.mouse import MouseMixin
from ahk.window import Window, WindowMixin
from ahk.script import ScriptEngine

class AHK(WindowMixin, MouseMixin):
    pass


class Hotkey:
    def __init__(self, engine: ScriptEngine, hotkey, script):
        self.hotkey = hotkey
        self.script = script
        self.engine = engine

    @property
    def running(self):
        return hasattr(self, '_proc')

    def _start(self, script):
        try:
            proc = self.engine.run_script(script, blocking=False)
            yield proc
        finally:
            self._stop()

    def start(self):
        if self.running:
            raise RuntimeError('Hotkey is already running')
        script = self.engine.render_template('hotkey.ahk', blocking=False, script=self.script, hotkey=self.hotkey)
        self._gen = self._start(script)
        proc = next(self._gen)
        self._proc = proc

    def _stop(self):
        if not self.running:
            return
        self._proc.terminate()
        del self._proc

    def stop(self):
        if not self.running:
            return
        try:
            next(self._gen)
        except StopIteration:
            pass
        finally:
            del self._gen


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
        n = n * 1000  # convert to miliseconds
        script = self.render_template('base.ahk', body=f'Sleep {n}', directives={'#Persistent',})
        self.run_script(script)
