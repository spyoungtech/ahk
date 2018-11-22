# ahk

A (proof-of-concept) Python wrapper around AHK.

# Usage

```python
from ahk import AHK
ahk = AHK()
ahk.move_mouse(x=100, y=100, speed=10)  # blocks until mouse finishes moving
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

Right now this is just an idea. It may not even be a particularly good one.

Not much is implemented right now, but the vision is to provide additional interfaces that mirror the core functionality from the AHK API in a Pythonic way.