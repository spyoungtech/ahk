import ast
import warnings
import logging

from ahk.script import ScriptEngine
from ahk.utils import escape_sequence_replace
from ahk.keys import Key
from ahk.directives import InstallKeybdHook, InstallMouseHook

import pathlib
import threading
import os
import time

class Bindable_Hotkey:

    def __init__(self, engine: ScriptEngine, hotkey: str, function, script = "", check_wait=.1):
        """
            Takes an instance of AHK as first arg, the AHK hotkey, the function
            to bind to the hotkey, (optional) the script to run on hotkey press, 
            (optional) check_wait the amount of time between hotkey checks, defines precision.
        """
        self.script = script
        self.hotkey = hotkey
        self.engine = engine
        self.stop_thread = False
        self.bound_function = function
        self.path = pathlib.Path(os.path.abspath("."))/"hotkey_file"
        self.check_time = check_wait
        self.thread = threading.Thread(target=self.heartbeat)

    @property
    def running(self):
        return hasattr(self, '_proc')

    def heartbeat(self):
        pos = 0
        next_time = time.time() + self.check_time
        while self.running:
            if time.time() >= next_time:
                try:
                    # Fix when both ahk, and python try to access at same time
                    with open(self.path) as file:
                        file.seek(pos)
                        data = file.read()
                        if data:
                            print('got data:', data)
                            self._on_hotkey()
                        else:
                            print('No data yet...')
                        pos = file.tell()
                except FileNotFoundError:
                    next_time = time.time() + self.check_time

            if self.stop_thread == True:
                return

    def _on_hotkey(self):
        self.bound_function()

    def _start(self, script):
        try:
            proc = self.engine.run_script(script, blocking=False)
            print(script)
            yield proc
        finally:
            self._stop()

    def start(self):
        """
        Starts an AutoHotkey process with the hotkey script
        """
        if self.running:
            raise RuntimeError('Hotkey is already running')
        script = self.engine.render_template('bindable_hotkey.ahk', blocking=False, script=self.script, hotkey=self.hotkey)
        self._gen = self._start(script)
        proc = next(self._gen)
        self._proc = proc
        self.thread.start()

    def _stop(self):
        if not self.running:
            return
        self._proc.terminate()
        del self._proc

    def stop(self):
        """
        Stops the process if it is running
        """
        if not self.running:
            raise RuntimeError('Hotkey is not running')
        try:
            next(self._gen)
        except StopIteration:
            pass
        finally:
            self.stop_thread = True
            del self._gen
   

class Hotkey:
    def __init__(self, engine: ScriptEngine, hotkey: str, script: str):
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
        """
        Starts an AutoHotkey process with the hotkey script
        """
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
        """
        Stops the process if it is running
        """
        if not self.running:
            raise RuntimeError('Hotkey is not running')
        try:
            next(self._gen)
        except StopIteration:
            pass
        finally:
            del self._gen


class KeyboardMixin(ScriptEngine):
    def hotkey(self, *args, **kwargs):
        """
        Convenience function for creating ``Hotkey`` instance using current engine.

        :param args:
        :param kwargs:
        :return:
        """
        return Hotkey(engine=self, *args, **kwargs)

    def key_state(self, key_name, mode=None) -> bool:
        """
        Check the state of a key.

        https://autohotkey.com/docs/commands/GetKeyState.htm

        :param key_name: the name of the key (or virtual key code)
        :param mode: see AHK docs
        :return: True if pressed down, else False
        """
        script = self.render_template('keyboard/key_state.ahk', key_name=key_name, mode=mode, directives=(InstallMouseHook, InstallKeybdHook))
        result = ast.literal_eval(self.run_script(script))
        return bool(result)

    def key_wait(self, key_name, timeout: int=None, logical_state=False, released=False):
        """
        Wait for key to be pressed or released (default is pressed; specify ``released=True`` to wait for key release).

        https://autohotkey.com/docs/commands/KeyWait.htm

        :param key_name: The name of the key
        :param timeout: how long (in seconds) to wait for the key. If not specified, waits indefinitely
        :param logical_state: Check the logical state of the key, which is the state that the OS and the active window believe the key to be in (not necessarily the same as the physical state). This option is ignored for joystick buttons.
        :param released: Set to True to wait for the key to be released rather than pressed
        :return:
        :raises TimeoutError: if the key was not pressed (or released, if specified) within timeout
        """
        options = ''
        if not released:
            options += 'D'
        if logical_state:
            options += 'L'
        if timeout:
            options += f'T{timeout}'
        script = self.render_template('keyboard/key_wait.ahk', key_name=key_name, options=options)
        result = self.run_script(script)
        if result == "1":
            raise TimeoutError(f'timed out waiting for {key_name}')

    def type(self, s):
        """
        Sends keystrokes using send_input, also escaping the string for use in AHK.
        """
        s = escape_sequence_replace(s)
        self.send_input(s)

    def send(self, s, raw=False, delay=None):
        """
        https://autohotkey.com/docs/commands/Send.htm

        :param s:
        :param raw:
        :param delay:
        :return:
        """
        script = self.render_template('keyboard/send.ahk', s=s, raw=raw, delay=delay)
        return self.run_script(script)

    def send_raw(self, s, delay=None):
        """
        https://autohotkey.com/docs/commands/Send.htm

        :param s:
        :param delay:
        :return:
        """
        return self.send(s, raw=True, delay=delay)

    def send_input(self, s):
        """
        https://autohotkey.com/docs/commands/Send.htm

        :param s:
        :return:
        """
        if len(s) > 5000:
            warnings.warn('String length greater than allowed. Characters beyond 5000 may not be sent. '
                          'See https://autohotkey.com/docs/commands/Send.htm#SendInputDetail for details.')

        script = self.render_template('keyboard/send_input.ahk', s=s)
        self.run_script(script)

    def send_play(self, s):
        """
        https://autohotkey.com/docs/commands/Send.htm


        :param s:
        :return:
        """
        script = self.render_template('keyboard/send_play.ahk', s=s)
        self.run_script(script)

    def send_event(self, s, delay=None):
        """
        https://autohotkey.com/docs/commands/Send.htm

        :param s:
        :param delay:
        :return:
        """
        script = self.render_template('keyboard/send_event.ahk', s=s, delay=delay)
        self.run_script(script)

    def key_press(self, key, release=True):
        """
        Press and (optionally) release a single key

        :param key:
        :param release:
        :return:
        """

        self.key_down(key)
        if release:
            self.key_up(key)

    def key_release(self, key):
        """
        Release a key that is currently in pressed down state

        :param key:
        :return:
        """
        if isinstance(key, str):
            key = Key(key_name=key)
        return self.send_input(key.UP)

    def key_down(self, key):
        """
        Press down a key (without releasing it)

        :param key:
        :return:
        """
        if isinstance(key, str):
            key = Key(key_name=key)
        return self.send_input(key.DOWN)

    def key_up(self, key):
        """
        Alias for :meth:~`KeyboardMixin.key_release`
        """
        return self.key_release(key)
