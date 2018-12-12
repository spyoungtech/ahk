# ahk

A Python wrapper around AHK.

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

# Installation

```
pip install ahk
```

## Dependencies

Just the AHK executable. It's expected to be on PATH by default. 

Alternatively you can set an `AHK_PATH` environment variable. 

Or, provide it inline

```python
from ahk import AHK
ahk = AHK(executable_path=r'C:\ProgramFiles\AutoHotkey\AutoHotkey.exe')
```

# Development

Right now this is just an exploration of an idea. It may not even be a particularly good idea.

There's still a bit to be done in the way of implementation.

The vision is to provide additional interfaces that implement the most important parts of the AHK API in a Pythonic way.
