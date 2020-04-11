import os
import sys

from ahk import AHK
from ahk.window import Window
from ahk.directives import NoTrayIcon
import ctypes
from ctypes import wintypes
from ctypes.wintypes import *
import textwrap

_last_title_length = 0


def _print_fields(position, color, title):
    global _last_title_length
    title_message = f'Window Title: {title}'
    needed_whitespace = _last_title_length - len(title_message)
    whitespace = ' ' * needed_whitespace
    _last_title_length = len(title_message)

    lines = [
        f'Mouse Position: {position}        ',
        f'Pixel Color: {color}     ',
        f'{title_message}{whitespace}'
    ]
    for index, line in enumerate(lines):
        buffer.set_position(0, index)
        buffer.write(line)

    buffer.show(console_handle)


def _console_spy(*args, **kwargs):
    os.system('cls')
    ahk = AHK(directives={NoTrayIcon})

    while True:
        position = ahk.mouse_position
        window = Window.from_mouse_position(engine=ahk)
        color = ahk.pixel_get_color(*position)
        _print_fields(position, color, window.title)


class Char(ctypes.Union):
    _fields_ = [("UnicodeChar", WCHAR), ("AsciiChar", CHAR)]


class CHAR_INFO(ctypes.Structure):
    _anonymous_ = ("Char",)
    _fields_ = [("Char", Char), ("Attributes", WORD)]


class CONSOLE_CURSOR_INFO(ctypes.Structure):
    _fields_ = [('dwSize', DWORD), ('bVisible', BOOL)]


PCHAR_INFO = ctypes.POINTER(CHAR_INFO)
COORD = wintypes._COORD


class CONSOLE_FONT_INFO(ctypes.Structure):
    _fields_ = [('nFont', DWORD), ('dwFontSize', COORD)]


class CONSOLE_SCREEN_BUFFER_INFO(ctypes.Structure):
    _fields_ = [
        ('dwSize', COORD),
        ('dwCursorPosition', COORD),
        ('wAttributes', WORD),
        ('srWindow', SMALL_RECT),
        ('dwMaximumWindowSize', COORD),
    ]



Kernel32 = ctypes.WinDLL('Kernel32.dll')
User32 = ctypes.WinDLL('User32.dll')
Gdi32 = ctypes.WinDLL('Gdi32.dll')


class ConsoleBuffer:
    def __init__(self, width, height):
        self.buff = Kernel32.CreateConsoleScreenBuffer(
            0x80000000 | 0x40000000, 0x00000001 | 0x00000002, None, 1, None
        )
        if self.buff == HANDLE(-1):
            raise RuntimeError("Could not create screen buffer")
        self.width = width
        self.height = height
        self.cursor_info = CONSOLE_CURSOR_INFO()
        self.cursor_info.dwSize = 25
        self.buff_size = COORD(width, height)
        Kernel32.SetConsoleScreenBufferSize(self.buff, self.buff_size)
        self.buff_start_coord = COORD(0, 0)
        self.read_region = SMALL_RECT(0, 0, width - 1, height - 1)
        self.write_region = SMALL_RECT(0, 0, width - 1, height - 1)
        self.written = DWORD()

    @property
    def handle(self):
        return self.buff

    def set_color(self, color):
        Kernel32.SetConsoleTextAttribute(self.buff, color)

    def set_position(self, x, y, stdout=None):
        coord = COORD(x, y)
        if stdout is None:
            Kernel32.SetConsoleCursorPosition(self.buff, coord)
        else:
            Kernel32.SetConsoleCursorPosition(stdout, coord)

    @staticmethod
    def wrap_text(text, w):
        return textwrap.fill(text, w, replace_whitespace=False, drop_whitespace=False) + '\n'

    def write(self, msg):
        msg = self.wrap_text(msg, self.buff_size.X)
        success = Kernel32.WriteConsoleW(self.buff, msg, DWORD(len(msg)), ctypes.byref(self.written), None)

        if not success:
            raise RuntimeError('write console failed')

    def show(self, handle):
        char_buffer = (CHAR_INFO * (self.buff_size.X * self.buff_size.Y))()

        success = Kernel32.ReadConsoleOutputW(
            self.buff, ctypes.byref(char_buffer), self.buff_size, self.buff_start_coord, ctypes.byref(self.read_region)
        )

        if not success:
            raise RuntimeError('Could not read console')

        success = Kernel32.WriteConsoleOutputW(
            handle, ctypes.byref(char_buffer), self.buff_size, self.buff_start_coord, ctypes.byref(self.write_region)
        )

        if not success:
            raise RuntimeError('Could not write console')


console_handle = Kernel32.GetStdHandle(DWORD(-11))

if console_handle == HANDLE(-1):
    raise RuntimeError('could not get buffer handle')

width = User32.GetSystemMetrics(0)
buffer = ConsoleBuffer(width, 5)
buffer.set_position(0, 0)


def _main():
    try:
        _console_spy()
    except KeyboardInterrupt:
        buffer.set_position(0, 3, console_handle)
        buffer.write('Exiting.')
        buffer.show(console_handle)
