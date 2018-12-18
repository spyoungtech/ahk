# ahk

A Python wrapper around AHK.

[![Build](https://ci.appveyor.com/api/projects/status/2c53x6gglw9nxgj1/branch/master?svg=true)](https://ci.appveyor.com/project/spyoungtech/ahk/branch/master) 
[![version](https://img.shields.io/pypi/v/ahk.svg?colorB=blue)](https://pypi.org/project/ahk/) 
[![pyversion](https://img.shields.io/pypi/pyversions/ahk.svg?)](https://pypi.org/project/ahk/) 
[![Coverage](https://coveralls.io/repos/github/spyoungtech/ahk/badge.svg?branch=master)](https://coveralls.io/github/spyoungtech/ahk?branch=master) 


# Installation

```
pip install ahk
```


# Usage

```python
from ahk import AHK
ahk = AHK()
ahk.mouse_move(x=100, y=100, speed=10)  # blocks until mouse finishes moving
print(ahk.mouse_position)  #  (100, 100)
```

![ahk](https://raw.githubusercontent.com/spyoungtech/ahk/master/docs/_static/ahk.gif)

## non-blocking modes

You can also opt for a non-blocking interface, so you can do other stuff while AHK scripts run.

```python
import time
from ahk import AHK
ahk = AHK()
ahk.mouse_position = (200, 200)  # moves the mouse instantly to the position
start = time.time()
ahk.mouse_move(x=100, y=100, speed=30, blocking=False)
while True:  #  report mouse position while it moves
    t = round(time.time() - start, 4)
    position = ahk.mouse_position
    print(t, position)
    if position == (100, 100):
        break
```

You should see an output something like

```
0.032 (187, 187)
0.094 (173, 173)
0.137 (164, 164)
...
0.788 (100, 103)
0.831 (100, 101)
0.873 (100, 100)
```

## Windows

You can do stuff with windows, too.


Getting windows

```python
from ahk import AHK
from ahk.window import Window
ahk = AHK()
win = ahk.active_window  # get the active window
win = ahk.win_get(title='Untitled - Notepad')  # by title
win = list(ahk.windows())  # list of all windows
win = Window(ahk, ahk_id='0xabc123')  # by ahk_id
win = Window.from_mouse_position(ahk)  # a window under the mouse cursor
win = Window.from_pid('20366')  # by process ID


```

Working with windows
```python
win.move(x=200, y=300, width=500, height=800)
win.activate()  # give the window focus
win.disable()  # make the window non-interactable
win.enable()  # enable it again
win.to_top()  # moves window on top of other windows
win.to_bottom()
win.always_on_top = True  # make the windows always on top
win.close()

for window in ahk.windows():
    print(window.title)
#  some more attributes
print(window.text)
print(window.rect)  # (x, y, width, height)
print(window.id)  # ahk_id
print(window.pid)
print(window.process)
```

## Debugging

You can enable debug logging, which will output script text before execution, and some other potentially useful 
debugging information.

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Non-Python Dependencies

Just the AHK executable. It's expected to be on PATH by default. 

Alternatively you can set an `AHK_PATH` environment variable. 

Or, provide it inline

```python
from ahk import AHK
ahk = AHK(executable_path='C:\\ProgramFiles\\AutoHotkey\\AutoHotkey.exe')
```


# Development

Right now this is just an exploration of an idea. It may not even be a particularly good idea.

There's still a bit to be done in the way of implementation.

The vision is to provide additional interfaces that implement the most important parts of the AHK API in a Pythonic way.
