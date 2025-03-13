# Contribution Guide

This guide is a work in progress, but aims to help a new contributor make a successful contribution to this project.

If you have questions about contributing not answered here, always feel free to [open an issue](https://github.com/spyoungtech/ahk/issues)
or [discussion](https://github.com/spyoungtech/ahk/discussions) and I will help you the best that I am able.

## Before contributing

Generally, all contributions should be associated with an [open issue](https://github.com/spyoungtech/ahk/issues).
Contributors are strongly encouraged to comment on an existing issue or create a new issue before working on a PR,
especially for feature work. Some contributions don't necessarily require this, such as typo fixes or documentation
improvements. When in doubt, create an issue.



## Initial development setup

- Activated virtualenv with Python version 3.9 or later (`py -m venv venv` and `venv\Scripts\activate`)
- Installed the dev requirements (`pip install -r requirements-dev.txt`) (this includes a binary redistribution of AutoHotkey)
- Installed pre-commit hooks (`pre-commit install`)


### Code formatting, linting, etc.

All matters of code style, linting, etc. are all handled by pre-commit hooks. All the proper parameters for formatting
and correct order of operations are provided there. If you try to run `black` or similar formatters directly on the
project, it will likely produce a lot of unintended changes that will not be accepted.

For these reasons and more, it is critical that you use the `pre-commit` hooks in order to make a successful contribution.


## Running tests

The test suite is managed by [`tox`](https://tox.wiki/en/latest/) (installed as part of `requirements-dev`)

You can run the test suite with the following command:

```bash
tox -e py
```

Tox runs tests in an isolated environment.

Although `tox` is the recommended way of testing, with all dev requirements installed,
you can run the tests directly with `pytest`:

```bash
pytest tests
```

Notes:

- The test suite expects the presence of the (legacy since Windows 11) `notepad.exe` program. This is included by default in Windows 10, but you may have to install this manually in later versions of Windows
- You will pretty much need to leave your computer alone during the test suite run. Moving the mouse, typing on the keyboard, or doing much of anything will make tests fail
- Due to the nature of this library, the test suite takes a long time to run
- Some tests (which only run locally, not in CI) for pixelsearch/imagesearch may fail depending on your monitor settings. This can safely be ignored.
- Some tests are flaky -- the tox configuration adds appropriate reruns to pytest to compensate for this, but reruns are not always 100% effective
- You can also simply rely on the GitHub Actions workflows for running tests

## Unasync Code Generation

This project leverages a [fork](https://github.com/spyoungtech/unasync/tree/unasync-remove) of [`unasync`](https://github.com/python-trio/unasync)
to automatically generate synchronous code (output to the `ahk/_sync` directory) from async code in the `ahk/_async` directory.

To be clear: **you will _never_ need to write code directly in the `ahk/_sync` directory**. This is all auto-generated code.

Code generation runs as part of the pre-commit hooks.


## Pre-commit hooks

Pre-commit hooks are an essential part of development for this project. They will ensure your code is properly formatted
and linted. It is also essential for performing code generation, as discussed in the previous section.

To run the pre-commit hooks:

```bash
pre-commit run --all-files
```

## How this project works, generally

This project is a wrapper around AutoHotkey. That is: it does not directly implement the underlying functionality, but
instead relies directly on AutoHotkey itself to function; specifically, AutoHotkey is invoked as a subprocess.

In typical usage, an AutoHotkey subprocess is created and runs the "daemon" script (found in `ahk/templates/`). The
[Auto-Execute section](https://www.autohotkey.com/docs/v2/Scripts.htm#auto) of which is an infinite loop that awaits
inputs via `stdin` to execute functions and return responses. The request and response formats are specialized.

A typical function call (like, say, `ahk.mouse_move`) works roughly like this:

0. If the AutoHotkey subprocess has not been previously started (or if the call is made with `blocking=False`), a new AutoHotkey process is created, running the daemon AHK script.
1. Python takes the keyword arguments of the method (if any) and prepares them into a request message (fundamentally, a list of strings, starting with the function name followed by any arguments)
2. The request is sent via `stdin` to the AutoHotkey subprocess (by implementation detail, arguments are base64 encoded and pipe-delimited and the mesage is newline-terminated)
3. The AutoHotkey subprocess (which is a loop reading `stdin`) reads/decodes the message and calls the corresponding function -- All such function calls to AutoHotkey **ALWAYS** return a response, even when the return value is ultimately `None`.
4. The AutoHotkey functions return a response, which is then written to `stdout` to send back to Python. The message contains information about the return type (such as a string, tuple, Exception, etc.) and the payload itself
5. Python then reads the response from the subprocess's `stdout` handle, translates the response to the return value expected by the caller. Responses can also be exception types, in which case, an exception can be raised as a result of decoding the message


Technically, a subprocess is only one possible transport. Although it is the only one implemented directly in this library,
alternate transports can be used, such as in the [ahk-client](https://github.com/spyoungtech/ahk-client) project, which implements
AHK function calls over HTTP (to a server running [ahk-server](https://github.com/spyoungtech/ahk-server)).


### Hotkeys

Hotkeys work slightly different from typical functions. Hotkeys are powered by a separate subprocess, which is started
with the `start_hotkeys` method. This subprocess runs the hotkeys script (e.g. `ahk/templates/hotkeys-v2.ahk`). This works
like a normal AutoHotkey script and when hotkeys are triggered, they write to `stdout`. A Python thread reads
from `stdout` and triggers the registered hotkey function. Unlike normal functions found in `ahk/_async`, the implementation of hotkeys
(found in `ahk/hotkeys.py`) is not implemented async-first -- it is all synchronous Python.


## Implementing a new method

This section will guide you through the steps of implementing a basic new feature. This is very closely related to the
documented process of [writing an extension](https://ahk.readthedocs.io/en/latest/extending.html), except that you are
including the functionality directly in the project, rather than using the extensions interface. It is highly
recommended that you read the extension docs!

This involves three basic steps:

1. Writing the AutoHotkey function(s) -- for both v1 and v2
2. Writing the (async) Python method(s)
3. Generating the sync code and testing (which implies writing tests at some point!)


In this example, we'll add a simple method that simply calls into AHK to do some arithemetic. Normally,
such a method wouldn't be prudent to implement in this library since Python can obviously handle arithmetic without
AutoHotkey, but we'll ignore this just for the sake of the example.

It is recommended, but not required, that you start by checking out a new branch named after the GitHub issue number
you're working on in the format `gh-<issue-number>` e.g.:

```bash
git checkout -b gh-12345
```


### Writing the AutoHotkey code

For example, in `ahk/templates/daemon-v2.ahk`, you may add a new function as so:

```AutoHotkey
AHKSimpleMath(lhs, rhs, operator) {
    if (operator = "+") {
        result := (lhs + rhs)
    } else if (operator = "*") {
        result := (lhs * rhs)
    } else { ; invalid operator argument
        return FormatResponse("ahk.message.ExceptionResponseMessage", Format("Invalid operator: {}", operator))
    }
    return FormatResponse("ahk.message.IntegerResponseMessage", result)
}
```

And you would add the same to `ahk/templates/daemon.ahk` for AHK V1.

Note that functions must always return a response (e.g. as provided by `FormatResponse`). Refer to the [extension guide](https://ahk.readthedocs.io/en/latest/extending.html)
for more information about available message formats and implementing new message formats.


### Writing the Python code


For example, in `ahk/_async/engine.py` you might add the following method to the `AsyncAHK` class:

```python
async def simple_math(self, lhs: int, rhs: int, operator: Literal['+', '*']) -> int:
    """
    Exposes arithmetic functions in AutoHotkey for plus and times operators
    """
    assert isinstance(lhs, int)
    assert isinstance(rhs, int)

    # Normally, you probably want to validate all inputs, but we'll comment this out to demo bubbling up AHK exceptions
    # assert operator in ('+', '*')

    args = [str(lhs), str(rhs), operator]  # all args must be strings
    result = await self._transport.function_call('AHKSimpleMath', args, blocking=True)
    return result
```


The most important part of this code is that the last part of the function returns the value of `await self._transport.function_call("FUNCTION NAME", ...)`.

:warning: For functions that accept the `blocking` keyword argument, it is important that no further manipulation be done on the value returned
(since it can be a _future_ result and not the ultimate value). If additional processing of the return value is needed, it
should be implemented in the message type instead.


### Testing and code generation

In `tests/_async` create a new testcase in a new file like `tests/_async/test_math.py` with some basic test cases
that cover a range of possible inputs and expected exceptional cases:

```python
import unittest

import pytest

from ahk import AsyncAHK

class MathTestCases(unittest.IsolatedAsyncioTestCase):
    async def test_simple_math_plus_operator(self):
        ahk = AsyncAHK()
        result = await ahk.simple_math(1, 2, '+')
        expected = 3
        assert result == expected

    async def test_simple_math_times_operator(self):
        ahk = AsyncAHK()
        result = await ahk.simple_math(2, 3, '*')
        expected = 6
        assert result == expected

    async def test_simple_math_bad_operator(self):
        ahk = AsyncAHK()
        with pytest.raises(Exception) as exc_info:
            await ahk.simple_math(1, 2, '>>>')
        assert "Invalid operator:" in str(exc_info.value)
```

Finally, run the `pre-commit` hooks to generate the synchronous code (both for your implementation and your tests)

```bash
pre-commit run --all-files
```

You'll notice that the `ahk/_sync` directory and the `tests/_sync` directories now contain the synchronous
versions of your implementation code and your tests, respectively.

And then run the tests:

```bash
tox -e py
```

When all tests are passing, you are ready to open a pull request to get your contributions reviewed and merged.

## About your contributions :balance_scale:

When you submit contributions to this project, you should understand that your contributions will be licensed under
the license terms of the project (found in `LICENSE`).

Moreover, by submitting a pull request to this project, you are representing that the code you are contributing is your own and is
unencumbered by any other licensing requirements.

Do not submit unoriginal code that is either unlicensed or licensed under any other terms without stating its source and
ensuring the contribution is fully compliant with any such licensing terms (which usually requires, at a minimum,
including the license itself). Even when contributing work under implied, creative commons, or licenses that do not
require attribution or notices (e.g. [_unlicence_](https://unlicense.org/) or similar), you are expected to explicitly
state the source of any material you submit that is not your own work. This includes, for example, code snippets found
on StackOverflow, the AutoHotkey forums, or any other source other than your own brain.
