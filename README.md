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

See also [Non-Python dependencies](#deps)  


# Usage

```python
from ahk import AHK
ahk = AHK()
ahk.mouse_move(x=100, y=100, speed=10, blocking=True)  # blocks until mouse finishes moving (the default)
print(ahk.mouse_position)  #  (100, 100)
```

![ahk](https://raw.githubusercontent.com/spyoungtech/ahk/master/docs/_static/ahk.gif)


# Examples

Non-exhaustive examples of some of the functions available with this package. Full documentation coming soon!


## Mouse


```python
from ahk import AHK
ahk = AHK()

ahk.mouse_position  # tuple of mouse coordinates (x,y)
ahk.mouse_move(100, 100, speed=10, relative=True)  # move mouse offset from current position
ahk.mouse_position = (100, 100)  # moves mouse instantly to absolute position
ahk.click()  # click primary mouse button
ahk.double_click()
ahk.click(200, 200)  # click a particular position
ahk.right_click()
ahk.mouse_drag(100, 100, relative=True)
```

## Keyboard

```python
from ahk import AHK
ahk = AHK()

ahk.type('hello, world!')  # sends keys, as if typed (performs ahk string escapes)
ahk.send_input('Hello`, World{!}')  # Like AHK SendInput, must escape strings yourself!
ahk.key_wait('a', timeout=3)  # wait up to 3 seconds for the "a" key to be pressed
ahk.key_state('Control')  # return True or False based on whether Control key is pressed down
ahk.key_state('CapsLock', mode='T')  # check toggle state of a key (like for NumLock, CapsLock, etc)
ahk.key_press('a')  # press and release a key
ahk.key_down('Control')  # press down (but do not release) Control key
ahk.key_up('Control')  # release the key
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
from ahk import AHK
ahk = AHK()
ahk.run_script('Run Notepad')
win = ahk.find_window(title=b'Untitled - Notepad')
win.send('hello')  # send keys directly to a window (does not need focus!)
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

## Screen

```python
from ahk import AHK
ahk = AHK()
ahk.image_search('C:\\path\\to\\image.jpg')  # find an image on screen
# find image within a boundary on screen
ahk.image_search('C:\\path\\to\\image.jpg', upper_bound=(100, 100),  # upper-left corner of search area
                                            lower_bound=(400, 400))  # lower-right corner of search area
ahk.pixel_get_color(100, 100)  # get color of pixel located at coords (100, 100)
ahk.pixel_search('0x9d6346')  # get coords of first pixel with specified color
```

## Sound

```python
from ahk import AHK
ahk = AHK()

ahk.sound_play('C:\\path\\to\\sound.wav')  # play an audio file
ahk.sound_beep(frequency=440, duration=1000)  # play a beep
ahk.get_volume(device_number=1)  # get volume of a device
ahk.set_volume(50, device_number=1)  # set volume of a device
ahk.sound_get(device_number=1, component_type='MASTER', control_type='VOLUME') # get sound device property
ahk.sound_set(50, device_number=1, component_type='MASTER', control_type='VOLUME') # set sound device property
```

## non-blocking modes

For some functions, you can also opt for a non-blocking interface, so you can do other stuff while AHK scripts run.

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


## Run arbitrary AutoHotkey scripts

```python
from ahk import AHK
ahk = AHK()
ahk_script = 'Run Notepad'
ahk.run_script(ahk_script, blocking=False)
```


### Communicating data from ahk to Python

If you're writing your own ahk scripts to use with this library, you can use `FileAppend` with the `*` parameter to get data from your ahk script into Python.

Suppose you have a script like so

```autohotkey
#Persistent
data := "Hello Data!"
FileAppend, %data%, * ; send data var to stdout
ExitApp
```

```py
result = ahk.run_script(my_script)
print(result)  # Hello Data!
```

If your autohotkey returns something that can't be decoded, add the keyword argument `decode=False` in which case you'll get back a `CompletedProcess` object where stdout (and stderr) will be bytes and you can handle it however you choose.

```py
result = ahk.run_script(my_script, decode=False)
print(result.stdout)  # b'Hello Data!'
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
generally recommended. Currently, there is limited support for interacting with windows in actionchains, you may want to use `win_set`)


### find_window/find_windows methods

[GH-26]

Right now, these are implemented by iterating over all window handles and filtering with Python.  
They may be optimized in the future.

`AHK.find_windows` returns a generator filtering results based on attributes provided as keyword arguments.  
`AHK.find_window` is similar, but returns the first matching window instead of all matching windows.

There are couple convenience functions, but not sure if these will stay around or maybe we'll add more, depending on feedback.

* find_windows_by_title
* find_window_by_title
* find_windows_by_text
* find_window_by_text

## Errors and Debugging

You can enable debug logging, which will output script text before execution, and some other potentially useful 
debugging information.

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Also note that, for now, errors with running AHK scripts will often pass silently. In the future, better error handling 
will be added.

<a name="deps" />

## Non-Python dependencies

To use this package, you need the [AutoHotkey executable](https://www.autohotkey.com/download/). 

It's expected to be on PATH by default. You can also use the `AHK_PATH` environment variable to specify the executable location.

Alternatively, you may provide the path in code

```python
from ahk import AHK
ahk = AHK(executable_path='C:\\path\\to\\AutoHotkey.exe')
```


# Contributing

All contributions are welcomed and appreciated.

Please feel free to open a GitHub issue or PR for feedback, ideas, feature requests or questions.

There's still some work to be done in the way of implementation. The ideal interfaces are still yet to be determined and 
*your* help would be invaluable.


The vision is to provide access to the most useful features of the AutoHotkey API in a Pythonic way.


[winlogo]: http://i.stack.imgur.com/Rfuw7.png
[GH-9]: https://github.com/spyoungtech/ahk/issues/9
[GH-25]: https://github.com/spyoungtech/ahk/issues/25
[GH-26]: https://github.com/spyoungtech/ahk/issues/26

# Similar projects

These are some similar projects that are commonly used for automation with Python.

* [Pyautogui](https://pyautogui.readthedocs.io) - Al Sweigart's creation for cross-platform automation
* [Pywinauto](https://pywinauto.readthedocs.io) - Automation on Windows platforms with Python.
* [keyboard](https://github.com/boppreh/keyboard) - Pure Python cross-platform keyboard hooks/control and hotkeys!
* [mouse](https://github.com/boppreh/mouse) - From the creators of `keyboard`, Pure Python *mouse* control!
* [pynput](https://github.com/moses-palmer/pynput) - Keyboard and mouse control

