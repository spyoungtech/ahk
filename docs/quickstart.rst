Quickstart
==========

This document assumes you have Python 3.6 or newer installed

Installing AHK
--------------

AHK requires the AutoHotkey software in addition to the Python package

1. Download and install AutoHotkey (1.1.x). It can be downloaded from the `autohotkey website`_.

2. Install the Python ``ahk`` package ::

    py -m pip install ahk

3. Write your first script::

    from ahk import AHK
    ahk = AHK()
    ahk.run_script('Run Notepad')
    notepad_window = ahk.find_window_by_title(b'Untitled - Notepad')
    notepad_window.send('Hello World')

Run the script!

If you get an :py:class:`~ahk.script.ExecutableNotFoundError` it's because AutoHotkey was installed to a location that
is not on PATH or the default location (``C:\Program Files\AutoHotkey\AutoHotkey.exe``). You can either place the
executable on PATH, in the default location, or specify the location manually in code: ::

   ahk = AHK(executable_path='C:\\Path\\To\\AutoHotkey.exe')

.. _autohotkey website: https://www.autohotkey.com/download/
