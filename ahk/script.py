import os
import subprocess
from shutil import which
from ahk.utils import logger


class ScriptEngine(object):
    def __init__(self, executable_path: str='', **kwargs):
        """
        :param executable_path: the path to the AHK executable.
        Defaults to environ['AHK_PATH'] if not explicitly provided
        If environment variable not present, tries to look for 'AutoHotkey.exe' or 'AutoHotkeyA32.exe' with shutil.which
        :param keep_scripts:
        :raises RuntimeError: if AHK executable is not provided and cannot be found in environment variables or PATH
        """
        if not executable_path:
            executable_path = os.environ.get('AHK_PATH') or which('AutoHotkey.exe') or which('AutoHotkeyA32.exe')
        self.executable_path = executable_path

    def _run_script(self, script_text, **kwargs):
        blocking = kwargs.pop('blocking', True)
        runargs = [self.executable_path, '/ErrorStdOut', '*']
        decode = kwargs.pop('decode', False)
        script_bytes = bytes(script_text, 'utf-8')
        if blocking:
            result = subprocess.run(runargs, input=script_bytes, stderr=subprocess.PIPE, stdout=subprocess.PIPE, **kwargs)
            if decode:
                return result.stdout.decode()
            else:
                return result
        else:
            proc = subprocess.Popen(runargs, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            try:
                proc.communicate(script_bytes, timeout=0)
            except subprocess.TimeoutExpired:
                pass  # for now, this seems needed to avoid blocking and use stdin
            return proc

    def run_script(self, script_text: str, decode=True, blocking=True, **runkwargs):
        try:
            result = self._run_script(script_text, decode=decode, blocking=blocking, **runkwargs)
        except Exception as e:
            logger.fatal('Error running temp script: %s', e)
            raise
        return result
