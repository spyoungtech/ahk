import os
import asyncio
import warnings
from ahk.autohotkey import AsyncAHK, AHK
import subprocess
import threading
import queue
import atexit

def escape(s):
    s = s.replace('\n', '`n')
    return s

class STOP:
    """A sentinel value"""
    ...

class AHKDaemon(AHK):
    proc: subprocess.Popen
    _template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
    _template = os.path.join(_template_path, 'daemon.ahk')
    _template_overrides = os.listdir(f'{_template_path}/daemon')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = queue.Queue()
        self.result_queue = queue.Queue()
        self.proc: asyncio.subprocess.Process
        self.proc = None
        self.thread = None
        self._is_running = False
        self.run_lock = threading.Lock()
        template = self.env.get_template('_daemon.ahk')
        with open(self._template, 'w') as f:
            f.write(template.render())

    def _run(self):
        if self._is_running:
            raise RuntimeError("Already running")
        self._is_running = True
        runargs = [self.executable_path, self._template]
        proc = subprocess.Popen(runargs,
                                   stdin=subprocess.PIPE,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE)
        self.proc = proc
        atexit.register(self.proc.terminate)

    def worker(self):
        while True:
            command = self.queue.get()
            if command is STOP:
                break
            self.proc.stdin.write(command + b'\n')
            self.proc.stdin.flush()
            num_lines = int(self.proc.stdout.readline().strip())
            res = b''.join(self.proc.stdout.readline() for _ in range(num_lines + 1))
            self.result_queue.put_nowait(res[:-1])
            self.queue.task_done()

    def _start(self):
        try:
            self.thread = threading.Thread(target=self.worker, daemon=True)
            self.thread.start()
            yield
        finally:
            if self.proc is not None:
                self.proc.kill()

    def stop(self):
        if self._is_running:
            if hasattr(self, '_gen') and self._gen is not None:
                try:
                    next(self._gen)
                except StopIteration:
                    pass
            self.queue.put_nowait(STOP)
            if self.thread is not None:
                self.thread.join()
            self._is_running = False

    def start(self):
        self._gen = self._start()
        self._gen.send(None)
        self._run()

    def render_template(self, template_name, directives=None, blocking=True, **kwargs):
        name = template_name.split('/')[-1]
        if name in self._template_overrides:
            template_name = f'daemon/{name}'
        blocking = False
        directives = None
        kwargs['_daemon'] = True
        return super().render_template(template_name, directives=directives, blocking=blocking, **kwargs)

    def run_script(self, script_text: str, decode=True, blocking=True, **runkwargs):
        if not blocking:
            warnings.warn("blocking=False in daemon mode is not supported", stacklevel=3)
        if not self._is_running:
            raise RuntimeError("Not running! Must call .start() first!")
        script_text = script_text.replace('#NoEnv', '', 1)
        with self.run_lock:
            for line in script_text.split('\n'):
                line = line.strip()
                if not line or line.startswith("FileAppend"):
                    continue
                self.queue.put_nowait(line.encode('utf-8'))
            self.queue.join()
            res = []
            while not self.result_queue.empty():
                res.append(self.result_queue.get_nowait())
        res = b'\n'.join(i for i in res if i)
        if decode:
            return res.decode('utf-8')
        return res

    def type(self, s, *args, **kwargs):
        kwargs['raw'] = True
        s = escape(s)
        self.send(s, *args, **kwargs)

    def show_tooltip(self, text: str, second=None, x="", y="", id="", blocking=True):
        return super().show_tooltip(text, second=second, x=x, y=y, id=id, blocking=blocking)

    def hide_tooltip(self, id):
        return super().show_tooltip(text='', second='', x='', y='', id=id)

    def hide_traytip(self):
        self.run_script("HideTrayTip")

    @staticmethod
    def escape_sequence_replace(s):
        s = escape(s)
        return s


class AsyncAHKDaemon(AsyncAHK):
    proc: asyncio.subprocess.Process
    _template_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
    _template = os.path.join(_template_path, 'daemon.ahk')
    _template_overrides = os.listdir(f'{_template_path}/daemon')
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.queue = asyncio.Queue()
        self.result_queue = asyncio.Queue()
        self.proc: asyncio.subprocess.Process
        self.proc = None
        self._is_running = False
        self.run_lock = asyncio.Lock()
        template = self.env.get_template('_daemon.ahk')
        with open(self._template, 'w') as f:
            f.write(template.render())

    async def _run(self):
        if self._is_running:
            raise RuntimeError("Already running")
        self._is_running = True
        runargs = [self.executable_path, self._template]
        proc = await asyncio.subprocess.create_subprocess_exec(*runargs,
                                                               stdin=asyncio.subprocess.PIPE,
                                                               stdout=asyncio.subprocess.PIPE,
                                                               stderr=asyncio.subprocess.PIPE)
        self.proc = proc

    async def _get_command(self):
        return await self.queue.get()

    async def worker(self):
        if not self._is_running:
            await self.start()
        while True:
            command = await self.queue.get()
            self.proc.stdin.write(command + b'\n')
            await self.proc.stdin.drain()
            num_lines = int(await self.proc.stdout.readline())
            lines = []
            for _ in range(num_lines + 1):
                line = await self.proc.stdout.readline()
                lines.append(line)
            res = b''.join(lines)
            self.result_queue.put_nowait(res[:-1])
            self.queue.task_done()

    def _start(self):
        try:
            asyncio.create_task(self.worker())
            yield
        finally:
            if self.proc is not None:
                self.proc.kill()

    def stop(self):
        if hasattr(self, '_gen') and self._gen is not None:
            try:
                next(self._gen)
            except StopIteration:
                pass
        self._is_running = False

    async def start(self):
        self._gen = self._start()
        self._gen.send(None)
        await self._run()

    def render_template(self, template_name, directives=None, blocking=True, **kwargs):
        name = template_name.split('/')[-1]
        if name in self._template_overrides:
            template_name = f'daemon/{name}'
        blocking = False
        directives = None
        kwargs['_daemon'] = True
        return super().render_template(template_name, directives=directives, blocking=blocking, **kwargs)

    async def a_run_script(self, script_text: str, decode=True, blocking=True, **runkwargs):
        if not self._is_running:
            raise RuntimeError("Not running! Must await .start() first!")
        script_text = script_text.replace('#NoEnv', '', 1)
        async with self.run_lock:
            for line in script_text.split('\n'):
                line = line.strip()
                if not line or line.startswith("FileAppend"):
                    continue
                self.queue.put_nowait(line.encode('utf-8'))
            await self.queue.join()
            res = []
            while not self.result_queue.empty():
                res.append(self.result_queue.get_nowait())
        res = b'\n'.join(i for i in res if i)
        if decode:
            return res.decode('utf-8')
        return res

    async def type(self, s, *args, **kwargs):
        kwargs['raw'] = True
        s = escape(s)
        await self.send(s, *args, **kwargs)

    def show_tooltip(self, text: str, second=None, x="", y="", id="", blocking=True):
        return super().show_tooltip(text, second=second, x=x, y=y, id=id, blocking=blocking)

    def hide_tooltip(self, id):
        return super().show_tooltip(text='', second='', x='', y='', id=id)

    async def hide_traytip(self):
        await self.run_script("HideTrayTip")

    @staticmethod
    def escape_sequence_replace(s):
        s = escape(s)
        return s

    run_script = a_run_script
