# ahk

A fully typed Python wrapper around AutoHotkey.

[![Docs](https://readthedocs.org/projects/ahk/badge/?version=latest)](https://ahk.readthedocs.io/en/latest/?badge=latest)
[![Build](https://github.com/spyoungtech/ahk/actions/workflows/test.yaml/badge.svg)](https://github.com/spyoungtech/ahk/actions/workflows/test.yaml)
[![version](https://img.shields.io/pypi/v/ahk.svg?colorB=blue)](https://pypi.org/project/ahk/)
[![pyversion](https://img.shields.io/pypi/pyversions/ahk.svg?)](https://pypi.org/project/ahk/)
[![Coverage](https://coveralls.io/repos/github/spyoungtech/ahk/badge.svg?branch=master)](https://coveralls.io/github/spyoungtech/ahk?branch=master)
[![Downloads](https://pepy.tech/badge/ahk)](https://pepy.tech/project/ahk)

# Installation

```
pip install ahk
```

Requires Python 3.8+

Supports AutoHotkey v1 and v2. See also: [Non-Python dependencies](#deps)

# Usage

```python
from ahk import AHK

ahk = AHK()

ahk.mouse_move(x=100, y=100, blocking=True)  # Blocks until mouse finishes moving (the default)
ahk.mouse_move(x=150, y=150, speed=10, blocking=True) # Moves the mouse to x, y taking 'speed' seconds to move
print(ahk.mouse_position)  #  (150, 150)
```

![ahk](https://raw.githubusercontent.com/spyoungtech/ahk/9d049a327c7a10c9f19dfef89fc63668695023fc/docs/_static/ahk.gif)

# Examples

Non-exhaustive examples of some functions available with this package. See the [full documentation](https://ahk.readthedocs.io/en/latest/?badge=latest)
for complete API references and additional features.

## Hotkeys

Hotkeys can be configured to run python functions as callbacks.

For example:

```python
from ahk import AHK

def my_callback():
    print('Hello callback!')

ahk = AHK()
# when WIN + n is pressed, fire `my_callback`
ahk.add_hotkey('#n', callback=my_callback)
ahk.start_hotkeys()  # start the hotkey process thread
ahk.block_forever()  # not strictly needed in all scripts -- stops the script from exiting; sleep forever
```

Now whenever you press <kbd>![Windows Key][winlogo]</kbd> + <kbd>n</kbd>, the `my_callback` callback function will be called in a background thread.

You can also add an exception handler for your callback:

```python
from ahk import AHK
ahk = AHK()

def go_boom():
    raise Exception('boom!')

def my_ex_handler(hotkey: str, exception: Exception):
    print('exception with callback for hotkey', hotkey, 'Here was the error:', exception)

ahk.add_hotkey('#n', callback=go_boom, ex_handler=my_ex_handler)
```

There are also methods for removing hotkeys:

```python
# ...
ahk.remove_hotkey('#n') # remove a hotkey by its keyname
ahk.clear_hotkeys()  # remove all hotkeys
```

Note that:

- Hotkeys run in a separate process that must be started manually (with `ahk.start_hotkeys()`)
- Hotkeys can be stopped with `ahk.stop_hotkeys()` (will not stop actively running callbacks)
- Hotstrings (discussed below) share the same process with hotkeys and are started/stopped in the same manner
- If hotkeys or hotstrings are added or removed while the process is running, the underlying AHK process is restarted automatically


See also the [relevant AHK documentation](https://www.autohotkey.com/docs/Hotkeys.htm)

## Hotstrings


[Hotstrings](https://www.autohotkey.com/docs/Hotstrings.htm) can also be added to the hotkey process thread.

In addition to Hotstrings supporting normal AHK string replacements, you can also provide Python callbacks (with optional exception handlers) in response to hotstrings triggering.

```python
from ahk import AHK
ahk = AHK()

def my_callback():
    print('hello callback!')

ahk.add_hotstring('btw', 'by the way')  # string replacements
ahk.add_hotstring('btw', my_callback) # call python function in response to the hotstring
```

You can also remove hotstrings:

```python
ahk.remove_hotstring('btw')  # remove a hotstring by its trigger sequence
ahk.clear_hotstrings()  # remove all registered hotstrings
```

## Mouse

```python
from ahk import AHK

ahk = AHK()

ahk.mouse_position  # Returns a tuple of mouse coordinates (x, y) (relative to active window)
ahk.get_mouse_position(coord_mode='Screen') # get coordinates relative to the screen
ahk.mouse_move(100, 100, speed=10, relative=True)  # Moves the mouse reletave to the current position
ahk.mouse_position = (100, 100)  # Moves the mouse instantly to absolute screen position
ahk.click()  # Click the primary mouse button
ahk.click(200, 200)  # Moves the mouse to a particular position and clicks (relative to active window)
ahk.click(100, 200, coord_mode='Screen') # click relative to the screen instead of active window
ahk.click(button='R', click_count=2) # Clicks the right mouse button twice
ahk.right_click() # Clicks the secondary mouse button
ahk.mouse_drag(100, 100, relative=True) # Holds down primary button and moves the mouse
```

## Keyboard

```python
from ahk import AHK

ahk = AHK()

ahk.type('hello, world!')  # Send keys, as if typed (performs string escapes for you)
ahk.send_input('Hello, {U+1F30E}{!}')  # Like AHK SendInput
                                   # Unlike `type`, control sequences must be escaped manually.
                                   # For example the characters `!^+#=` and braces (`{` `}`) must be escaped manually.
ahk.key_state('Control')  # Return True or False based on whether Control key is pressed down
ahk.key_state('CapsLock', mode='T')  # Check toggle state of a key (like for NumLock, CapsLock, etc)
ahk.key_press('a')  # Press and release a key
ahk.key_down('Control')  # Press down (but do not release) Control key
ahk.key_up('Control')  # Release the key
ahk.set_capslock_state("On")  # Turn CapsLock on
if ahk.key_wait('x', timeout=3):  # wait for a key to be pressed; returns a boolean
    print('X was pressed within 3 seconds')
else:
    print('X was not pressed within 3 seconds')
```

## Windows

You can do stuff with windows, too.


### Getting windows

```python
from ahk import AHK

ahk = AHK()

win = ahk.active_window                        # Get the active window
win = ahk.win_get(title='Untitled - Notepad')  # by title
all_windows = ahk.list_windows()               # list of all windows
win = ahk.win_get_from_mouse_position()        # the window under the mouse cursor
win = ahk.win_get(title='ahk_pid 20366')       # get window from pid

# Wait for a window
try:
    # wait up to 5 seconds for notepad
    win = ahk.win_wait(title='Untitled - Notepad', timeout=5)
    # see also: win_wait_active, win_wait_not_active
except TimeoutError:
    print('Notepad was not found!')
```

### Working with windows

```python
from ahk import AHK

ahk = AHK()

ahk.run_script('Run Notepad') # Open notepad
win = ahk.find_window(title='Untitled - Notepad') # Find the opened window; returns a `Window` object

# Window object methods
win.send('hello', control='Edit1')  # Send keys directly to the window (does not need focus!)
# OR ahk.control_send(title='Untitled - Notepad', control='Edit1')
win.move(x=200, y=300, width=500, height=800)

win.activate()                  # Give the window focus
win.close()                     # Close the window
win.hide()                      # Hide the window
win.kill()                      # Kill the window
win.maximize()                  # Maximize the window
win.minimize()                  # Minimize the window
win.restore()                   # Restore the window
win.show()                      # Show the window
win.disable()                   # Make the window non-interactable
win.enable()                    # Enable it again
win.to_top()                    # Move the window on top of other windows
win.to_bottom()                 # Move the window to the bottom of the other windows
win.get_class()                 # Get the class name of the window
win.get_minmax()                # Get the min/max status
win.get_process_name()          # Get the process name (e.g., "notepad.exe")
win.process_name                # Property; same as `.get_process_name()` above
win.is_always_on_top()          # Whether the window has the 'always on top' style applied
win.list_controls()             # Get a list of controls (list of `Control` objects)
win.redraw()                    # Redraw the window
win.set_style("-0xC00000")      # Set a style on the window (in this case, removing the title bar)
win.set_ex_style("^0x80")       # Set an ExStyle on the window (in this case, removes the window from alt-tab list)
win.set_region("")              # See: https://www.autohotkey.com/docs/v2/lib/WinSetRegion.htm
win.set_trans_color("White")    # Makes all pixels of the chosen color invisible inside the specified window.
win.set_transparent(155)        # Makes the specified window semi-transparent (or "Off" to turn off transparency)


win.always_on_top = 'On' # Make the window always on top
# or
win.set_always_on_top('On')

for window in ahk.list_windows():  # list all (non-hidden) windows -- ``detect_hidden_windows=True`` to include hidden
    print(window.title)

    # Some more attributes
    print(window.text)           # window text -- or .get_text()
    print(window.get_position()) # (x, y, width, height)
    print(window.id)             # the ahk_id of the window
    print(window.pid)            # process ID -- or .get_pid()
    print(window.process_path)   # or .get_process_path()


if win.active:        # or win.is_active()
    ...

if win.exist:         # or win.exists()
    ...

# Controls

edit_control = win.list_controls()[0]  # get the first control for the window, in this case "Edit1" for Notepad
edit_control.get_text()      # get the text in Notepad
edit_control.get_position()  # returns a `Postion` namedtuple: e.g. Position(x=6, y=49, width=2381, height=1013)

```

Various window methods can also be called directly without first creating a `Window` object by using the underlying `win_*` methods on the `AHK` class.
For example, instead of `win.close()` as above, one could call `ahk.win_close(title='Untitled - Notepad')` instead.



## Screen

```python
from ahk import AHK

ahk = AHK()

ahk.image_search('C:\\path\\to\\image.jpg')  # Find an image on screen

# Find an image within a boundary on screen
ahk.image_search('C:\\path\\to\\image.jpg', upper_bound=(100, 100),  # upper-left corner of search area
                                            lower_bound=(400, 400))  # lower-right corner of search area
ahk.pixel_get_color(100, 100)  # Get color of pixel located at coords (100, 100)
ahk.pixel_search(color='0x9d6346', search_region_start=(0, 0), search_region_end=(500, 500))  # Get coords of the first pixel with specified color
```

## Clipboard

Get/set `Clipboard` data

```python
from ahk import AHK
ahk = AHK()

ahk.set_clipboard('hello \N{EARTH GLOBE AMERICAS}')  # set clipboard text contents
ahk.get_clipboard() # get clipboard text contents
# 'hello 🌎'
ahk.set_clipboard("")  # Clear the clipboard

ahk.clip_wait(timeout=3)  # Wait for clipboard contents to change (with text or file(s))
ahk.clip_wait(timeout=3, wait_for_any_data=True)  # wait for _any_ clipboard contents
```

You may also get/set `ClipboardAll` -- however, you should never try to call `set_clipboard_all` with any other
data than as _exactly_ as returned by `get_clipboard_all` or unexpected problems may occur.

```python
from ahk import AHK
ahk = AHK()

# save all clipboard contents in all formats
saved_clipboard = ahk.get_clipboard_all()
ahk.set_clipboard('something else')
...
ahk.set_clipboard_all(saved_clipboard)  # restore saved content from earlier
```

You can also set a callback to execute when the clipboard contents change. As with Hotkey methods mentioned above,
you can also set an exception handler. Like hotkeys, `on_clipboard_change` callbacks also require `.start_hotkeys()`
to be called to take effect.

The callback function must accept one positional argument, which is an integer indicating the clipboard datatype.

```python
from ahk import AHK
ahk = AHK()
def my_clipboard_callback(change_type: int):
    if change_type == 0:
        print('Clipboard is now empty')
    elif change_type == 1:
        print('Clipboard has text contents')
    elif change_type == 2:
        print('Clipboard has non-text contents')

ahk.on_clipboard_change(my_clipboard_callback)
ahk.start_hotkeys()  # like with hotkeys, must be called at least once for listening to start
# ...
ahk.set_clipboard("hello") # will cause the message "Clipboard has text contents" to be printed by the callback
ahk.set_clipboard("") # Clears the clipboard, causing the message "Clipboard is now empty" to be printed by the callback
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


Tooltips/traytips

```python
import time
from ahk import AHK

ahk = AHK()
ahk.show_tooltip("hello4", x=10, y=10)
time.sleep(2)
ahk.hide_tooltip() # hide the tooltip
ahk.show_info_traytip("Info", "It's also info", silent=False, blocking=True)  # Default info traytip
ahk.show_warning_traytip("Warning", "It's a warning")                           # Warning traytip
ahk.show_error_traytip("Error", "It's an error")                                 # Error trytip
```

Dialog boxes

```python
from ahk import AHK, MsgBoxButtons
ahk = AHK()

ahk.msg_box(text='Do you like message boxes?', title='My Title', buttons=MsgBoxButtons.YES_NO)
ahk.input_box(prompt='Password', title='Enter your password', hide=True)
ahk.file_select_box(title='Select one or more mp3 files', multi=True, filter='*.mp3', file_must_exist=True)
ahk.folder_select_box(prompt='Select a folder')
```

## Global state changes

You can change various global states such as `CoordMode`, `DetectHiddenWindows`, etc. so you don't have to pass
these parameters directly to function calls

```python
from ahk import AHK

ahk = AHK()

ahk.set_coord_mode('Mouse', 'Screen')  # set default Mouse CoordMode to be relative to Screen
ahk.set_detect_hidden_windows(True) # Turn on detect hidden windows by default
ahk.set_send_level(5)  # Change send https://www.autohotkey.com/docs/v1/lib/SendLevel.htm

ahk.set_title_match_mode('Slow') # change title match speed and/or mode
ahk.set_title_match_mode('RegEx')
ahk.set_title_match_mode(('RegEx', 'Slow'))  # or both at the same time
ahk.set_send_mode('Event')  # change the default SendMode
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

Directives are not applied for the AHK process used for handling hotkeys and hotstrings (discussed below) by default. To apply a directive
to the hotkeys process using the keyword argument `apply_to_hotkeys_process=True`:

```python
from ahk import AHK
from ahk.directives import NoTrayIcon

directives = [
    NoTrayIcon(apply_to_hotkeys_process=True)
]

ahk = AHK(directives=directives)
```

## Menu tray icon

As discussed above, you can hide the tray icon if you wish. Additionally, there are some methods available for
customizing the tray icon.


```python
from ahk import AHK
ahk = AHK()

# change the tray icon (in this case, using a builtin system icon)
ahk.menu_tray_icon('Shell32.dll', 174)
# revert it back to the original:
ahk.menu_tray_icon()

# change the tooltip that shows up when hovering the mouse over the tray icon
ahk.menu_tray_tooltip('My Program Name')

# Hide the tray icon
ahk.menu_tray_icon_hide()

# Show the tray icon that was previously hidden by ``NoTrayIcon`` or ``menu_tray_icon_hide``
ahk.menu_tray_icon_show()
```

## Registry methods

You can read/write/delete registry keys:

```python
from ahk import AHK
ahk = AHK()

ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\my-software', value='test')
ahk.reg_write('REG_SZ', r'HKEY_CURRENT_USER\SOFTWARE\my-software', value_name='foo', value='bar')
ahk.reg_read(r'HKEY_CURRENT_USER\SOFTWARE\my-software')  # 'test'
ahk.reg_delete(r'HKEY_CURRENT_USER\SOFTWARE\my-software')
```

If a key does not exist or some other problem occurs, an exception is raised.

## non-blocking modes

Most methods in this library supply a non-blocking interface, so your Python scripts can continue executing while
your AHK scripts run.

By default, all calls are _blocking_ -- each function will execute completely before the next function is ran.

However, sometimes you may want to run other code while AHK executes some code.  When the `blocking` keyword
argument is supplied with `False`, function calls will return immediately while the AHK function is carried out
in the background.


As an example, you can move the mouse slowly and report its position as it moves:

```python
import time

from ahk import AHK

ahk = AHK()

ahk.mouse_position = (200, 200)  # Moves the mouse instantly to the start position
start = time.time()

# move the mouse very slowly
ahk.mouse_move(x=100, y=100, speed=30, blocking=False)

# This code begins executing right away, even though the mouse is still moving
while True:
    t = round(time.time() - start, 4)
    position = ahk.mouse_position
    print(t, position) #  report mouse position while it moves
    if position == (100, 100):
        break
```


When you specify `blocking=False` you will always receive a special `FutureResult` object (or `AsyncFutureResult` object in the async API, discussed below)
which allows you to wait on the function to complete and retrieve return value through a `get_result` function. Even
when a function normally returns `None`, this can be useful to ensure AHK has finished executing the function.

nonblocking calls:

- Are isolated in a new AHK process that will terminate after the call is complete
- Always start immediately
- Do not inherit previous global state changes (e.g., from `set_coord_mode` calls or similar) -- this may change in a future version.
- will not block other calls from starting
- will always return a special `FutureResult` object (or `AsyncFutureResult` object in the async API, discussed below)
which allows you to wait on the function to complete and retrieve return value through the `result` function. Even
when a function normally returns `None`, this can be useful to ensure AHK has finished executing the function.

```python
from ahk import AHK
ahk = AHK()
future_result = ahk.mouse_move(100, 100, speed=40, blocking=False)
...
# wait on the mouse_move to finish
future_result.result(timeout=10) # timeout keyword is optional
```



## Async API (asyncio)

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

The async API is identical to that of the normal API, with a few notable differences:

- While properties (like `.mouse_position` or `.title` for windows) can be `await`ed,
additional methods (like `get_mouse_position()` and `get_title()`) have been added for a more intuitive API and
are recommended over the use of properties.
- Property _setters_ (e.g., `ahk.mouse_postion = (200, 200)`) are not allowed in the async API (a RunTimeError is raised).
Property setters remain available in the sync API.
- `AsyncFutureResult` objects (returned when specifying `blocking=False`) work the same as the `FutureResult` objects in the sync API, except the `timeout` keyword is not supported for the `result` method).

Note also that:
- by default, awaited tasks on a single `AsyncAHK` instance will not run concurrently. You must either
use `blocking=False`, as in the sync API, or use multiple instances of `AsyncAHK`.
- There is no difference in working with hotkeys (and their callbacks) in the async vs sync API.


## type-hints and mypy

This library is fully type-hinted, allowing you to leverage tools like `mypy` to help validate the type-correctness
of your code. IDEs that implement type-checking features are also able to leverage type hints to help ensure your
code is safe.


## Run arbitrary AutoHotkey scripts

You can also run arbitrary AutoHotkey code either as a `.ahk` script file or as a string containing AHK code.

```python
from ahk import AHK
ahk = AHK()
my_script = '''\
MouseMove, 100, 100
; etc...
'''

ahk.run_script(my_script)
```

```python
from ahk import AHK
ahk = AHK()
script_path = r'C:\Path\To\myscript.ahk'
ahk.run_script(script_path)
```


<a name="deps"></a>

# Non-Python dependencies

To use this package, you need the [AutoHotkey executable](https://www.autohotkey.com/download/) (e.g., `AutoHotkey.exe`).
It's expected to be on PATH by default OR in a default installation location (`C:\Program Files\AutoHotkey\AutoHotkey.exe` for v1 or `C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe` for v2)

AutoHotkey v1 and v2 are both fully supported, though some behavioral differences will occur depending on which version
you use. See notes below.

The recommended way to supply the AutoHotkey binary (for both v1 and v2) is to install the `binary` extra for this package. This will
provide the necessary executables and help ensure they are correctly placed on PATH.

```
pip install "ahk[binary]"
```


Alternatively, you may provide the path in code:

```python
from ahk import AHK

ahk = AHK(executable_path='C:\\path\\to\\AutoHotkey.exe')
```

You can also use the `AHK_PATH` environment variable to specify the executable location.

```console
set AHK_PATH=C:\Path\To\AutoHotkey.exe
python myscript.py
```

## Using AHK v2

By default, when no `executable_path` parameter (or `AHK_PATH` environment variable) is set, only AutoHotkey v1 binary names
are searched for on PATH or default install locations. This behavior may change in future versions to allow v2 to be used by default.

To use AutoHotkey version 2, you can do any of the following things:

1. provide the `executable_path` keyword argument with the location of the AutoHotkey v2 binary
2. set the `AHK_PATH` environment variable with the location of an AutoHotkey v2 binary
3. Provide the `version` keyword argument with the value `v2` which enables finding the executable using AutoHotkey v2 binary names and default install locations.

For example:

```python
from ahk import AHK


ahk = AHK(executable_path=r'C:\Program Files\AutoHotkey\v2\AutoHotkey64.exe')
# OR
ahk = AHK(version='v2')
```

When you provide the `version` keyword argument (with either `"v1"` or `"v2"`) a check is performed to ensure the provided (or discovered) binary matches the requested version. When
the `version` keyword is omitted, the version is determined automatically from the provided (or discovered) executable binary.



### Differences when using AutoHotkey v1 vs AutoHotkey v2

The API of this project is originally designed against AutoHotkey v1 and function signatures are the same, even when using AutoHotkey v2.
While most of the behavior remains the same, some behavior does change when using AutoHotkey v2 compared to v1. This is mostly due to
[underlying differences](https://www.autohotkey.com/docs/v2/v2-changes.htm) between the two versions.

Some of the notable differences that you may experience when using AutoHotkey v2 with this library include:

1. Functions that find and return windows will often raise an exception rather than returning `None` (as in AutoHotkey v2, a TargetError is thrown in most cases where the window or control cannot be found)
2. The behavior of `ControlSend` (`ahk.control_send` or `Window.send` or `Control.send`) differs in AutoHotkey v2 when the `control` parameter is not specified. In v1, keys are sent to the topmost controls, which is usually the correct behavior. In v2, keys are sent directly to the window. This means in many cases, you need to specify the control explicitly when using V2.
3. Some functionality is not supported in v2 -- specifically: the `secondstowait` paramater for `TrayTip` (`ahk.show_traytip`) was removed in v2. Specifying this parameter in the Python wrapper will cause a warning to be emitted and the parameter is ignored.
4. Some functionality that is present in v1 is not yet implemented in v2 -- this is expected to change in future versions. Specifically: some [sound functions](https://www.autohotkey.com/docs/v2/lib/Sound.htm) are not implemented.
5. The default SendMode changes in v2 to `Input` rather than `Event` in v1 (as a consequence, for example, mouse speed parameters to `mouse_move` and `mouse_drag` will be ignored in V2 unless the send mode is changed)
6. The default [TitleMatchMode](https://www.autohotkey.com/docs/v2/lib/SetTitleMatchMode.htm) is `2` in AutoHotkey v2. It is `1` in AutoHotkey v1. Use the `title_match_mode` keyword arguments to `win_get` and other methods that accept this keyword to control this behavior or use `set_title_match_mode` to change the default behavior (non-blocking calls are run in separate processes and are not affected by `set_title_match_mode`)

## Extending: add your own AutoHotkey code (beta)

You can develop extensions for extending functionality of `ahk` -- that is: writing your own AutoHotkey code and adding
additional methods to the AHK class. See the [extending docs](https://ahk.readthedocs.io/en/latest/extending.html) for
more information.

# Contributing

All contributions are welcomed and appreciated.

Please feel free to open a GitHub issue or PR for feedback, ideas, feature requests or questions.

[winlogo]: http://i.stack.imgur.com/Rfuw7.png


# Similar projects

These are some similar projects that are commonly used for automation with Python.

* [Pyautogui](https://pyautogui.readthedocs.io) - Al Sweigart's creation for cross-platform automation
* [Pywinauto](https://pywinauto.readthedocs.io) - Automation on Windows platforms with Python.
* [keyboard](https://github.com/boppreh/keyboard) - Pure Python cross-platform keyboard hooks/control and hotkeys!
* [mouse](https://github.com/boppreh/mouse) - From the creators of `keyboard`, Pure Python *mouse* control!
* [pynput](https://github.com/moses-palmer/pynput) - Keyboard and mouse control
