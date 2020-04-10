from ahk import AHK
from ahk.window import Window
from ahk.directives import NoTrayIcon


def _console_spy(*args, **kwargs):
    ahk = AHK(directives={NoTrayIcon})

    while True:
        position = ahk.mouse_position
        window = Window.from_mouse_position(engine=ahk)
        color = ahk.pixel_get_color(*position)
        print(f'Mouse Position: {position} Pixel Color: {color} Window Title: {window.title}                ', end='\r')

def _main():
    _console_spy()
