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

## Experimental features

Experimental features are things that are minimally functional, (even more) likely to have breaking changes, even 
for minor releases. 

Github issues are provided for convenience to collect feedback on these features.


### Hotkeys

[GH-9]

Hotkeys now have a primitive implementation. You give it a hotkey (a string the same as in an ahk script, without the `::`) 
and the body of an AHK script to execute as a response to the hotkey.



```python
from ahk import AHK, Hotkey
ahk = AHK()
key_combo = '#n'
script = 'Run Notepad'
hotkey = Hotkey(ahk, key_combo, script)
hotkey.start()  #  listener process activated
```
At this point, the hotkey is active. 
If you press <kbd>![Windows Key][winlogo]</kbd> + <kbd>n</kbd>, the script `Run Notepad` will execute.

There is no need to add `return` to the provided script, as it is provided by the template.

To stop the hotkey call the `stop()` method.

```python
hotkey.stop()
```


### ActionChain

[GH-25]

`ActionChain`s let you define a set of actions to be performed in order at a later time.

They work just like the `AHK` class, except the actions are deferred until the `perform` method is called.

An additional method `sleep` is provided to allow for waiting between actions.

```python
from ahk import ActionChain
ac = ActionChain()
ac.mouse_move(100, 100, speed=10)  # nothing yet
ac.sleep(1)  # still nothing happening
ac.mouse_move(500, 500, speed=10)  # not yet
ac.perform()  # *now* each of the actions run in order
```

Just like anywhere else, scripts running simultaneously may conflict with one another, so using blocking interfaces is 
generally recommended.


### find_window/find_windows methods

[GH-26]

Right now, these are implemented by iterating over all window handles and filtering with Python.

`AHK.find_windows` returns a generator filtering results based on attributes provided as keyword arguments.  
`AHK.find_window` is similar, but returns the first matching window instead of all matching windows.

There are couple convenience functions, but not sure if these will stay around or maybe we'll add more, depending on feedback.

* find_windows_by_title
* find_window_by_title
* find_windows_by_text
* find_window_by_text


## Non-Python Dependencies

Just the AHK executable. It's expected to be on PATH by default. 

Alternatively you can set an `AHK_PATH` environment variable. 

Or, provide it inline

```python
from ahk import AHK
ahk = AHK(executable_path='C:\\path\\to\\AutoHotkey.exe')
```


# Contributing

All contributions are welcomed and appreciated.

Please feel free to open a GitHub issue or PR for feedback, ideas, feature requests or questions.

There's still some work to be done in the way of implementation. 


The vision is to provide additional interfaces that implement the most important parts of the AHK API in a Pythonic way.


[winlogo]: http://i.stack.imgur.com/Rfuw7.png
[GH-9]: https://github.com/spyoungtech/ahk/issues/9
[GH-25]: https://github.com/spyoungtech/ahk/issues/25
[GH-26]: https://github.com/spyoungtech/ahk/issues/26