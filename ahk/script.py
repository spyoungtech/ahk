from tempfile import NamedTemporaryFile
import os
import subprocess
from contextlib import suppress
from shutil import which
from ahk.utils import logger
import time

class ScriptEngine(object):
    def __init__(self, executable_path: str='', keep_scripts: bool=False, **kwargs):
        """
        :param executable_path: the path to the AHK executable.
        Defaults to environ['AHK_PATH'] if not explicitly provided
        If environment variable not present, tries to look for 'AutoHotkey.exe' or 'AutoHotkeyA32.exe' with shutil.which
        :param keep_scripts:
        :raises RuntimeError: if AHK executable is not provided and cannot be found in environment variables or PATH
        """
        self.keep_scripts = bool(keep_scripts)
        if not executable_path:
            executable_path = os.environ.get('AHK_PATH') or which('AutoHotkey.exe') or which('AutoHotkeyA32.exe')
        self.executable_path = executable_path

    def _run_script(self, script_path, **kwargs):
        blocking = kwargs.pop('blocking', True)
        runargs = [self.executable_path, script_path]
        decode = kwargs.pop('decode', False)
        if blocking:
            result = subprocess.run(runargs, stdin=None, stderr=None, stdout=subprocess.PIPE, **kwargs)
            if decode:
                return result.stdout.decode()
            else:
                return result.stdout
        else:
            p = subprocess.Popen(runargs, stdout=subprocess.PIPE, **kwargs)
            p.stdout.readline()  # give script a chance to read the script or else we'll delete it too quick
            return p

    def run_script(self, script_text: str, delete=None, decode=True, **runkwargs):
        if delete is None:
            delete = not self.keep_scripts
        with NamedTemporaryFile(mode='w', delete=False, newline='\r\n') as temp_script:
            temp_script.write(script_text)
            logger.debug('Script location: %s', temp_script.name)
            logger.debug('Script text: \n%s', script_text)
        try:
            result = self._run_script(temp_script.name, decode=decode, **runkwargs)
        except Exception as e:
            logger.fatal('Error running temp script: %s', e)
            raise
        finally:
            if delete:
                logger.debug('cleaning up temp script')
                with suppress(OSError):
                    os.remove(temp_script.name)
        return result
