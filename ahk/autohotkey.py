from tempfile import NamedTemporaryFile
import os
import ast
import subprocess
import shutil
from textwrap import dedent
import time
from contextlib import suppress
import logging

class AHK(object):
    def __init__(self, executable_path: str='', keep_scripts: bool=False):
        """

        :param executable_path: the path to the AHK executable. Defaults to environ['AHK_PATH'] otherwise tries 'AutoHotkeyA32.exe'
        :param keep_scripts:
        :raises RuntimeError: if AHK executable is not provided and cannot be found in environment variables or PATH
        """
        self.speed = 2
        self.keep_scripts = bool(keep_scripts)
        executable_path = executable_path or os.environ.get('AHK_PATH') or shutil.which('AutoHotkey.exe') or shutil.which('AutoHotkeyA32.exe')
        self.executable_path = executable_path

    def _run_script(self, script_path, **kwargs):
        result = subprocess.run([self.executable_path, script_path], stdin=None, stderr=None, stdout=subprocess.PIPE, **kwargs)
        return result.stdout.decode()

    def run_script(self, script_text:str, delete=None, blocking=True, **runkwargs):
        if blocking is False:
            script_text = script_text.lstrip('#Persistent')
        if delete is None:
            delete = not self.keep_scripts
        try:
            with NamedTemporaryFile(mode='w', delete=False) as temp_script:
                temp_script.write(script_text)
            result = self._run_script(temp_script.name)
        except Exception as e:
            logging.critical('Something went terribly wrong: %s', e)
            result = None
        finally:
            if delete:
                with suppress(OSError):
                    os.remove(temp_script.name)
        return result

    def _mouse_position(self):
        return dedent('''
        #Persistent
        MouseGetPos, xpos, ypos
        s .= Format("({}, {})", xpos, ypos)
        FileAppend, %s%, *
        ExitApp
        ''')

    @property
    def mouse_position(self):
        response = self.run_script(self._mouse_position())
        return ast.literal_eval(response)

    @mouse_position.setter
    def mouse_position(self, position):
        x, y = position
        self.move_mouse(x=x, y=y, speed=0, relative=False)

    def _move_mouse(self, x=None, y=None, speed=None, relative=False):
        if x is None and y is None:
            raise ValueError('Position argument(s) missing. Must provide x and/or y coordinates')
        if speed is None:
            speed = self.speed
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
        script = dedent(f'''\
            #Persistent
            MouseMove, {x}, {y} , {speed}{relative}
            ExitApp
        ''')
        return script

    def move_mouse(self, *args, **kwargs):
        script = self._move_mouse(*args, **kwargs)
        response = self.run_script(script_text=script)
        return response or None
