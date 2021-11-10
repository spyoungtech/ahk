import os
import subprocess
import sys
import threading
import time
import asyncio
from itertools import product
from unittest import TestCase, IsolatedAsyncioTestCase


project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AsyncAHK, AHK
from ahk.keys import ALT, CTRL, KEYS


class TestKeyboardAsync(IsolatedAsyncioTestCase):
    def setUp(self):
        """
        Record all open windows
        :return:
        """
        self.ahk = AsyncAHK()
        # self._normal_ahk = AHK()
        # self.before_windows = self._normal_ahk.windows()
        self.p = subprocess.Popen('notepad')
        time.sleep(1)

    async def asyncTearDown(self):
        self.p.terminate()
        await asyncio.sleep(0.5)

    async def test_window_send(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.send('hello world')
        await asyncio.sleep(1)
        self.assertIn(b'hello world', await notepad.get_text())

    async def test_send(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.activate()
        await self.ahk.send('hello world')
        self.assertIn(b'hello world', await notepad.get_text())

    async def test_send_input(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await self.ahk.send_input('Hello World')
        await asyncio.sleep(0.5)
        assert b'Hello World' in await notepad.get_text()

    async def test_type(self):
        notepad = await self.ahk.find_window(title=b'Untitled - Notepad')
        await notepad.activate()
        await self.ahk.type('Hello, World!')
        assert b'Hello, World!' in await notepad.get_text()


def a_down():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_down('a')


def release_a():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_up('a')


def press_a():
    time.sleep(0.5)
    ahk = AHK()
    ahk.key_press('a')


#
class TestKeysAsync(IsolatedAsyncioTestCase):
    def setUp(self):
        self.ahk = AsyncAHK()
        self._normal_ahk = AHK()
        self.thread = None
        self.hotkey = None

    def tearDown(self):
        if self.thread is not None:
            self.thread.join(timeout=3)
        if self._normal_ahk.key_state('a'):
            self._normal_ahk.key_up('a')
        if self._normal_ahk.key_state('Control'):
            self._normal_ahk.key_up('Control')

        notepad = self._normal_ahk.find_window(title=b'Untitled - Notepad')
        if notepad:
            notepad.kill()

        if self.hotkey and self.hotkey.running:
            self.hotkey.stop()

    async def a_key_wait_pressed(self):
        await self.ahk.key_wait('a', timeout=5)

    def test_key_wait_pressed(self):
        start = time.time()
        self.thread = threading.Thread(target=a_down)
        self.thread.start()
        asyncio.run(self.a_key_wait_pressed())
        end = time.time()
        assert end - start < 5

    async def a_key_wait_released(self):
        await self.ahk.key_wait('a', timeout=2)

    def test_key_wait_released(self):
        start = time.time()
        a_down()
        self.thread = threading.Thread(target=release_a)
        self.thread.start()
        asyncio.run(self.a_key_wait_released())
        end = time.time()
        assert end - start < 2

    async def a_key_wait_timeout(self):
        await self.ahk.key_wait('f', timeout=0.1)

    def test_key_wait_timeout(self):
        self.assertRaises(TimeoutError, asyncio.run, self.a_key_wait_timeout())

    async def test_key_state_when_not_pressed(self):
        self.assertFalse(await self.ahk.key_state('a'))

    async def test_key_state_pressed(self):
        await self.ahk.key_down('Control')
        self.assertTrue(await self.ahk.key_state('Control'))


#     def test_hotkey(self):
#         self.hotkey = self.ahk.hotkey(hotkey="a", script="Run Notepad")
#         self.thread = threading.Thread(target=a_down)
#         self.thread.start()
#         self.hotkey.start()
#         time.sleep(1)
#         self.assertIsNotNone(self.ahk.find_window(title=b"Untitled - Notepad"))
#
#     def test_hotkey_stop(self):
#         self.hotkey = self.ahk.hotkey(hotkey="a", script="Run Notepad")
#         self.hotkey.start()
#         assert self.hotkey.running
#         self.hotkey.stop()
#         self.ahk.key_press("a")
#         self.assertIsNone(self.ahk.find_window(title=b"Untitled - Notepad"))
