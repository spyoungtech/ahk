# ahk

A Python wrapper around AHK.

# Usage

```python
from ahk import AHK
ahk = AHK()
ahk.mouse_move(x=100, y=100, speed=10)  # blocks until mouse finishes moving
print(ahk.mouse_position)  #  (100, 100)
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