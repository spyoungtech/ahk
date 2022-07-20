# ahk

A Python wrapper around AHK.

[![Docs](https://readthedocs.org/projects/ahk/badge/?version=latest)](https://ahk.readthedocs.io/en/latest/?badge=latest)
[![Build](https://ci.appveyor.com/api/projects/status/2c53x6gglw9nxgj1/branch/master?svg=true)](https://ci.appveyor.com/project/spyoungtech/ahk/branch/master)
[![version](https://img.shields.io/pypi/v/ahk.svg?colorB=blue)](https://pypi.org/project/ahk/)
[![pyversion](https://img.shields.io/pypi/pyversions/ahk.svg?)](https://pypi.org/project/ahk/)
[![Coverage](https://coveralls.io/repos/github/spyoungtech/ahk/badge.svg?branch=master)](https://coveralls.io/github/spyoungtech/ahk?branch=master)
[![Downloads](https://pepy.tech/badge/ahk)](https://pepy.tech/project/ahk)

# Installation

```
pip install ahk
```
Requires Python 3.6+

[Async API](#async-api) requires Python 3.8+

See also [Non-Python dependencies](#non-python-dependencies)


# Usage

```python
from ahk import AHK

ahk = AHK()

ahk.mouse_move(x=100, y=100, blocking=True)  # Blocks until mouse finishes moving (the default)
ahk.mouse_move(x=150, y=150, speed=10, blocking=True) # Moves the mouse to x, y taking 'speed' seconds to move
print(ahk.mouse_position)  #  (150, 150)
```

![ahk](https://raw.githubusercontent.com/spyoungtech/ahk/master/docs/_static/ahk.gif)

# Examples

Non-exhaustive examples of some of the functions available with this package. Full documentation coming soon!

## Mouse

```python
from ahk import AHK

ahk = AHK()

ahk.mouse_position  # Returns a tuple of mouse coordinates (x, y)
ahk.mouse_move(100, 100, speed=10, relative=True)  # Moves the mouse reletave to the current position
ahk.mouse_position = (100, 100)  # Moves the mouse instantly to absolute screen position
ahk.click()  # Click the primary mouse button
ahk.double_click() # Clicks the primary mouse button twice
ahk.click(200, 200)  # Moves the mouse to a particular position and clicks
ahk.right_click() # Clicks the secondary mouse button
ahk.mouse_drag(100, 100, relative=True) # Holds down primary button and moves the mouse
```

## Keyboard

```python
from ahk import AHK

ahk = AHK()

ahk.type('hello, world!')  # Send keys, as if typed (performs ahk string escapes)
ahk.send_input('Hello`, World{!}')  # Like AHK SendInput, must escape strings yourself!
ahk.key_state('Control')  # Return True or False based on whether Control key is pressed down
ahk.key_state('CapsLock', mode='T')  # Check toggle state of a key (like for NumLock, CapsLock, etc)
ahk.key_press('a')  # Press and release a key
ahk.key_down('Control')  # Press down (but do not release) Control key
ahk.key_up('Control')  # Release the key
ahk.key_wait('a', timeout=3)  # Wait up to 3 seconds for the "a" key to be pressed. NOTE: This throws
                              # a TimeoutError if the key isn't pressed within the timeout window
ahk.set_capslock_state("on")  # Turn CapsLock on
```

## Windows

You can do stuff with windows, too.


### Getting windows

```python
from ahk import AHK
from ahk.window import Window

ahk = AHK()

win = ahk.active_window                        # Get the active window
win = ahk.win_get(title='Untitled - Notepad')  # by title
win = list(ahk.windows())                      # list of all windows
win = Window(ahk, ahk_id='0xabc123')           # by ahk_id
win = Window.from_mouse_position(ahk)          # the window under the mouse cursor
win = Window.from_pid(ahk, pid='20366')                 # by process ID

# Wait for a window
try:
    # wait up to 5 seconds for notepad
    win = ahk.win_wait(title='Untitled - Notepad', timeout=5)
except TimeoutError:
    print('Notepad was not found!')
```

### Working with windows

```python
from ahk import AHK

ahk = AHK()

ahk.run_script('Run Notepad') # Open notepad
win = ahk.find_window(title=b'Untitled - Notepad') # Find the opened window

win.send('hello')  # Send keys directly to the window (does not need focus!)
win.move(x=200, y=300, width=500, height=800)

win.activate()           # Give the window focus
win.activate_bottom()    # Give the window focus
win.close()              # Close the window
win.hide()               # Hide the windwow
win.kill()               # Kill the window
win.maximize()           # Maximize the window
win.minimize()           # Minimize the window
win.restore()            # Restore the window
win.show()               # Show the window
win.disable()            # Make the window non-interactable
win.enable()             # Enable it again
win.to_top()             # Move the window on top of other windows
win.to_bottom()          # Move the window to the bottom of the other windows

win.always_on_top = True # Make the window always on top

for window in ahk.windows():
    print(window.title)

    # Some more attributes
    print(window.text)
    print(window.rect)   # (x, y, width, height)
    print(window.id)     # ahk_id
    print(window.pid)
    print(window.process)


if window.active:        # Check if window active
    window.minimize()

if window.exist:         # Check if window exist
    window.maximize()

```

## Screen

```python
from ahk import AHK

ahk = AHK()

ahk.image_search('C:\\path\\to\\image.jpg')  # Find an image on screen

# Find an image within a boundary on screen
ahk.image_search('C:\\path\\to\\image.jpg', upper_bound=(100, 100),  # upper-left corner of search area
                                            lower_bound=(400, 400))  # lower-right corner of search area
ahk.pixel_get_color(100, 100)  # Get color of pixel located at coords (100, 100)
ahk.pixel_search('0x9d6346')  # Get coords of the first pixel with specified color
```

## Sound

```python
from ahk import AHK

ahk = AHK()

ahk.sound_play('C:\\path\\to\\sound.wav')  # Play an audio file
ahk.sound_beep(frequency=440, duration=1000)  # Play a beep for 1 second (duration in microseconds)
ahk.get_volume(device_number=1)  # Get volume of a device
ahk.set_volume(50, device_number=1)  # Set volume of a device
ahk.sound_get(device_number=1, component_type='MASTER', control_type='VOLUME') # Get sound device property
ahk.sound_set(50, device_number=1, component_type='MASTER', control_type='VOLUME') # Set sound device property
```

## GUI

```python
from ahk import AHK

ahk = AHK()
ahk.show_tooltip("hello4", second=2, x=10, y=10)                              # ToolTip
ahk.show_info_traytip("Info", "It's also info", silent=False, blocking=True)  # Default info traytip
ahk.show_warning_traytip("Warning", "It's warning")                           # Warning traytip
ahk.show_error_traytip("Error", "It's error")                                 # Error trytip
```

## non-blocking modes

For some functions, you can also opt for a non-blocking interface, so you can do other stuff while AHK scripts run.

```python
import time

from ahk import AHK

ahk = AHK()

ahk.mouse_position = (200, 200)  # Moves the mouse instantly to the start position
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
## Add directives

You can add directives that will be added to all generated scripts.
For example, to prevent the AHK trayicon from appearing, you can add the NoTrayIcon directive.

```python
from ahk import AHK
from ahk.directives import NoTrayIcon

ahk = AHK(directives=[NoTrayIcon])
```

By default, some directives are automatically added to ensure functionality and are merged with any user-provided directives.

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
FileAppend, %data%, *, UTF-8 ; send data var to stdout
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


## Preview features

Preview features are experimental features that are may not be fully functional.
These features are (even more) likely to have breaking changes without warning.

Github issues are provided for convenience to collect feedback on these features.


## AHKDaemon

Normally, `AHK` works by creating a new subprocess for every command invocation. Because processes are expensive
to create in Windows, this can lead to performance issues for some use-cases. `AHKDaemon` allows all AHK commands to be
carried out in a single process, as opposed to running each command in a new subprocess, improving performance.

Some other details change in Daemon mode, such as persistence of state (e.g. changes to CoordMode).


```python
from ahk.daemon import AHKDaemon
daemon = AHKDaemon()
daemon.start()
daemon.mouse_move(100, 100)
```

For the most part, the AHK Daemon works just like the regular `AHK` class, with a few caveats. Most notably, AHKDaemon
does not allow you to run arbitrary AutoHotkey scripts and does not yet support Hotkeys. However, you can always use
the normal `AHK` class alongside the daemon for these needs.

`AsyncAHKDaemon` is also available for asyncio support.

In the future, AHKDaemon may become the default implementation.


## Async API

An async API is provided so functions can be called using `async`/`await`.
All the same methods from the synchronous API are available in the async API.

```python
from ahk import AsyncAHK
import asyncio
ahk = AsyncAHK()

async def main():
    await ahk.mouse_move(100, 100)
    x, y = await ahk.get_mouse_position()
    print(x, y)

asyncio.run(main())
```
For the most part, the async API is identical to that of the normal API, with a few exceptions:

While properties (like `.mouse_position` or `.title` for windows) can be `await`ed,
additional methods (like `get_mouse_position()` and `get_title()`) have been added for a more intuitive API.

Property setters have different (probably undesired) behavior
in the async API. Instead, you should use a comparable method. If you _do_ use the property setters, the invocation is created using `asyncio.create_task()`, which means
that the task won't run until control is yielded back to the event loop. For now, this will also raise a warning to the same.


Lastly, while it's possible to pass `blocking=False` in the async API, this sometimes will cause problems with certain functions. For now, a warning is raised in this case.

```python
ahk = AsyncAHK()
async def main():
    pos = ahk.mouse_position  # BAD! Does not work!
    pos = await ahk.mouse_position # OK. Works, but looks kind of weird
    pos = await ahk.get_mouse_position() # GOOD!

    # BAD: You probably don't want to do this
    ahk.mouse_position = (100, 100) # won't do anything right away. Raises warning
    print(await ahk.get_mouse_position()) # probably won't be 100,100

    # GOOD: Instead, do this:
    await ahk.mouse_move(100, 100, speed=0)
    assert await ahk.get_mouse_position() == (100, 100)
```


### Hotkeys

[GH-9]

Hotkeys now have a primitive implementation. You give it a hotkey (a string the same as in an ahk script, without the `::`)
and the body of an AHK script to execute as a response to the hotkey.

Right now, only AHK code is supported as callbacks for hotkeys.
Support for Python callbacks via the Async API is planned.

```python
from ahk import AHK, Hotkey

ahk = AHK()

key_combo = '#n' # Define an AutoHotkey key combonation
script = 'Run Notepad' # Define an ahk script
hotkey = Hotkey(ahk, key_combo, script) # Create Hotkey
hotkey.start()  #  Start listening for hotkey
```
At this point, the hotkey is active.
If you press <kbd>![Windows Key][winlogo]</kbd> + <kbd>n</kbd>, the script `Run Notepad` will execute.

There is no need to add `return` to the provided script, as it is provided by the template.

To stop the hotkey call the `stop()` method.

```python
hotkey.stop()
```

See also the [relevant AHK documentation](https://www.autohotkey.com/docs/Hotkeys.htm)

### ActionChain

[GH-25]

`ActionChain`s let you define a set of actions to be performed in order at a later time.

They work just like the `AHK` class, except the actions are deferred until the `perform` method is called.

An additional method `sleep` is provided to allow for waiting between actions.

```python
from ahk import ActionChain

ac = ActionChain()

# An Action Chain doesn't perform the actions until perform() is called on the chain

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
(See the [logging module documentation](https://docs.python.org/3/library/logging.html) for more information)

Also note that, for now, errors with running AHK scripts will often pass silently. In the future, better error handling
will be added.

<a name="deps" />

## Non-Python dependencies

To use this package, you need the [AutoHotkey executable](https://www.autohotkey.com/download/). It's expected to be on PATH by default.

A convenient way to do this is to install the `binary` extra (requires version 0.13 or higher of this package)

```
pip install "ahk[binary]"
```

For versions < 0.13 you can install the ahk-binary package directly:

```
pip install "ahk-binary<2"
```

You can also use the `AHK_PATH` environment variable to specify the executable location.

```console
set AHK_PATH=C:\Path\To\AutoHotkey.exe
```

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
