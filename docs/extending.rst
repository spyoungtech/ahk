Extending AHK
=============

.. attention::
   The extension feature is in early stages of development and may change at any time, including breaking changes in minor version releases.

You can extend AHK to add more functionality. This is particularly useful for those who may want to
contribute their own solutions into the ecosystem that others can use.

For users of an extension, their interface will typically look like this:

1. Install the extension (e.g., ``pip install ...``)
2. import the extension(s) and enable extensions when instantiating the ``AHK`` class

.. code-block::

    from my_great_extension import the_extension
    from ahk import AHK
    ahk = AHK(extensions='auto')  # use all available/imported extensions
    ahk.my_great_method('foo', 'bar', 'baz')  # new methods are available from the extension!


This document will describe how you can create your own extensions and also cover some basics of packaging and
distributing an extension for ``ahk`` on PyPI.


Background
----------

First, a little background is necessary into the inner mechanisms of how ``ahk`` does what it does. It is important for
extension authors to understand these key points:

- Python calls AHK functions by name and can pass any number of strings as parameters.
- Functions written in AHK accept zero or more string arguments and must return a string in a specific message format (we'll discuss these specifics later)
- The message returned from AHK to Python indicates the type of the return value so Python can parse the response message into an appropriate Python type. There are several predefined message types available in the :py:mod:`ahk.message` module. Extension authors may also create their own message types (discussed later).



Writing an extension
--------------------

The basics of writing an extension requires two key components:


- A function written in AHK that conforms to the required spec (accepts zero or more arguments and returns a formatted message).
- A python function that accepts an instance of ``AHK`` (or ``AsyncAHK`` for ``async`` functions) as its first parameter (think of it like a method of the ``AHK`` class). It may also accept any additional parameters.


Example
^^^^^^^

This simple example extension will provide a new method on the ``AHK`` class called ``simple_math``. This new method
accepts three arguments: two operands (``lhs`` and ``rhs``) and an operator (``+`` or ``*``).

When complete, the interface will look something like this:

.. code-block::

    ahk = AHK(extensions='auto')
    print(ahk.simple_math(2, 2, '+')) # 4


Let's begin writing the extension.

First, we'll start with the AutoHotkey code. This will be an AHK function that, in this case, accepts 3 arguments.

Ultimately, the function will perform some operation utilizing these inputs and will return a formatted response. We use
the ``FormatResponse`` function (which is available by default) to do this. ``FormatResponse`` accepts two arguments: the message type name
and the raw payload as a string. By default, message type names are the fully qualified name of the Python class that
implements the message type (more on message types later).


.. code-block::


    SimpleMath(lhs, rhs, operator) {
        if (operator = "+") {
            result := (lhs + rhs)
        } else if (operator = "*") {
            result := (lhs * rhs)
        } else { ; invalid operator argument
            return FormatResponse("ahk.message.ExceptionResponseMessage", Format("Invalid operator: {}", operator))
        }
        return FormatResponse("ahk.message.IntegerResponseMessage", result)
    }



Next, we'll create the Python components of our extension: a Python function and the extension itself. The extension
itself is an instance of the ``Extension`` class and it accepts an argument ``script_text`` which will be a string
containing the AutoHotkey code we just wrote above.


.. code-block::

    from ahk import AHK
    from ahk.extensions import Extension
    from typing import Literal

    script_text = r'''
    ; a string of your AHK script
    ; Omitted here for brevity -- copy/paste from the previous code block
    '''
    simple_math_extension = Extension(script_text=script_text)

    @simple_meth_extension.register  # register the method for the extension
    def simple_math(ahk: AHK, lhs: int, rhs: int, operator: Literal['+', '*']) -> int:
        assert isinstance(lhs, int)
        assert isinstance(rhs, int)
        # assert operator in ('+', '*')  # we'll leave this out so we can demo raising exceptions from AHK
        args = [str(lhs), str(rhs), operator]  # all args must be strings
        result = ahk.function_call('SimpleMath', args, blocking=True)
        return result


After the extension is created, it can be used automatically!

.. code-block::

    # ... above code omitted for brevity
    ahk = AHK(extensions='auto')

    result = ahk.simple_math(2, 4, operator='+')
    print('2 + 4 =', result)
    assert result == 6

    result = ahk.simple_math(2, 4, operator='*')
    print('2 * 4 =', result)
    assert result == 8

    # this will raise our custom exception from our AHK code
    try:
        ahk.simple_math(0, 0, operator='invalid')
    except Exception as e:
        print('An exception was raised. Exception message was:', e)

If you use this example code, it should output something like this: ::

    2 + 4 = 6
    2 * 4 = 8
    An exception was raised. Exception message was: Invalid operator: %




Includes
^^^^^^^^

In addition to supplying AutoHotkey extension code via ``script_text``, you may also do this using includes.

.. code-block::

    from ahk.extensions import Extension
    my_extension = Extension(includes=['myscript.ahk']) # equivalent to "#Include myscript.ahk"

AsyncIO considerations
^^^^^^^^^^^^^^^^^^^^^^

When registering an extension function, if the decorated function is a coroutine function (``async def function_name(...):``)
then it will be made available only when the Async API (via ``AsyncAHK()``) is used. Conversely, normal non-async functions will only be available
when the sync API (via ``AHK()``).

To provide your extension functionality to both the Sync and Async APIs, you will need to provide both a synchronous and async version of your function.

.. code-block::


   @my_extension.register
   def my_function(ahk: AHK, foo, bar):
       ...

   @my_extension.register
   async def my_function(ahk: AsyncAHK, foo, bar):
       ...


AutoHotkey V1 vs V2 compatibility
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Because extensions involve the inclusion of AutoHotkey source code, it is often the case that extensions are sensitive
to the version of AutoHotkey being used. Extensions can specify their compatibility with different AutoHotkey versions
by providing the ``requires_autohotkey`` keyword argument with a value of ``v1`` or ``v2``. If an extension omits this
keyword argument, it is assumed that the extension is compatible with both V1 and V2.

When an AutoHotkey class is instantiated with ``extensions='auto'`` extensions are automatically filtered by version compatibility.

That is to say, you may need multiple ``Extension`` objects to fully support users of both versions of AutoHotkey. However, this
doesn't necessarily mean you need multiple Python functions -- you can register multiple extensions to the same Python function.

.. code-block::

   my_extension_v1 = Extension(..., requires_autohotkey='v1')
   my_extension_v2 = Extension(..., requires_autohotkey='v1')

   @my_extension_v1.register
   @my_extension_v2.register
   def my_extension_function(ahk: AHK, foo, bar, baz) -> Any:
      ...


Extension dependencies
^^^^^^^^^^^^^^^^^^^^^^

Extensions can declare explicit dependencies on other extensions. This allows extension authors to re-use other extensions
and end-users do not need to specify your extension's dependencies when explicitly providing the ``extensions`` keyword argument.

To specify dependencies, provide a list of ``Extension`` instance objects in the ``dependencies`` keyword argument.

.. code-block::

   from ahk_json import JXON  # pip install ahk-json
   my_extension_script = '''\
   MyAHKFunction(one, two) {
      val := Array(one, two)
      ret := Jxon_Dump(val) ; `Jxon_Dump` is provided by the dependent extension!
      return FormatResponse("ahk_json.message.JsonResponseMessage", ret) ; this message type is also part of the extension
   }
   '''
   MY_EXTENSION = Extension(script_text=my_extension_script, dependencies=[JXON], requires_autohotkey='v1')

   @MY_EXTENSION.register
   def my_function(ahk: AHK, one: str, two: str) -> list[str]:
       args = [one, two]
       return ahk.function_call('MyAHKFunction', args)

Then users may use such an extension simply as follows, and both ``JXON`` and ``MY_EXTENSION`` will be used.

.. code-block::

   from ahk import AHK
   from my_extension import MY_EXTENSION

   ahk = AHK(extensions=[MY_EXTENSION], version='v1')  # same effect as extensions=[JXON, MY_EXTENSION]

Best practices for extension authors
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Some conventions that authors are recommended to follow:

- Extension functions should use namespaced naming conventions to avoid collisions (both in AutoHotkey code and Python function names); avoid generic function names like "load" or similar that may collide with other extensions
- Do not start AutoHotkey function names with ``AHK`` -- as it may conflict with functions implemented by this package.
- Extension packages published on PyPI should be named with a convention like so: ``ahk-<ext name>``


Available Message Types
^^^^^^^^^^^^^^^^^^^^^^^

.. list-table::
   :header-rows: 1

   * - Message type
     - Python return type
     - Payload description
   * - :py:class:`ahk.message.TupleResponseMessage`
     - A ``tuple`` object containing any number of literal types (``Tuple[Any, ...]``)
     - A string representing a tuple literal (i.e. usable with ``ast.literal_eval``)
   * - :py:class:`ahk.message.CoordinateResponseMessage`
     - A tuple containing two integers (``Tuple[int, int]``)
     - A string representing the tuple literal
   * - :py:class:`ahk.message.IntegerResponseMessage`
     - An integer (``int``)
     - A string literal representing an integer
   * - :py:class:`ahk.message.BooleanResponseMessage`
     - A boolean (``bool``)
     - A string literal of either ``0`` or ``1``
   * - :py:class:`ahk.message.StringResponseMessage`
     - A string (``str``)
     - Any string
   * - :py:class:`ahk.message.WindowListResponseMessage`
     - A list of :py:class:`~ahk._sync.window.Window` (or :py:class:`~ahk._async.window.AsyncWindow`) objects
     - A string containing a comma-delimited list of window IDs
   * - :py:class:`ahk.message.NoValueResponseMessage`
     - NoneType (``None``)
     - A sentinel value (use ``FormatNoValueResponse()`` in AHK for returning this message)
   * - :py:class:`ahk.message.ExceptionResponseMessage`
     - raises an Exception.
     - A string with the exception message
   * - :py:class:`ahk.message.WindowControlListResponseMessage`
     - A list of :py:class:`~ahk._sync.window.Control` (or :py:class:`~ahk._async.window.AsyncControl`) objects
     - A string literal representing a tuple containing the window hwnd and a list of tuples each containing the control hwnd and class for each control
   * - :py:class:`ahk.message.WindowResponseMessage`
     - A :py:class:`~ahk._sync.Window` (or ``AsyncWindow``) object
     - A string containing the ID of the window
   * - :py:class:`ahk.message.PositionResponseMessage`
     - A ``Postion`` namedtuple object, consisting of 4 integers with named attributes ``x``, ``y``, ``width``, and ``height``
     - A string representing the tuple literal
   * - :py:class:`ahk.message.FloatResponseMessage`
     - ``float``
     - A string literal representation of a float
   * - :py:class:`ahk.message.TimeoutResponseMessage`
     - raises a ``TimeoutException``
     - A string containing the exception message
   * - :py:class:`ahk.message.B64BinaryResponseMessage`
     - ``bytes`` object
     - A string containing base64-encoded binary data


Returning custom types (make your own message type)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

You can design your extension functions to ultimately return different types by implementing your own message class.

To do this, subclass :py:class:`ahk.message.ResponseMessage` (or any of its other subclasses) and implement the ``unpack`` method.

For example, suppose you want your method to return a datetime object, you might do something like this:

.. code-block::

    import datetime
    from ahk.message import IntegerResponseMessage
    class DatetimeResponseMessage(IntegerResponseMessage):
        def unpack(self) -> datetime.datetime:
            val = super().unpack()  # get the integer timestamp
            return datetime.datetime.fromtimestamp(val)

In AHK code, you can reference custom response messages by the their fully qualified name, including the namespace.
(if you're not sure what this means, you can see this value by calling the ``fqn()`` method, e.g. ``DateTimeResponseMessage.fqn()``)

Notes
^^^^^

- AHK functions MUST always return a message. Failing to return a message will result in an exception being raised. If the function should return nothing, use ``return FormatNoValueResponse()`` which will translate to ``None`` in Python.
- You cannot define hotkeys, hotstrings, or write any AutoHotkey code that would cause the end of the `auto-execute section <https://www.autohotkey.com/docs/v1/Scripts.htm#auto>`_
- Extensions must be imported (anywhere, at least once) *before* instantiating the ``AHK`` instance
- Although extensions can be declared explicitly, using ``extensions='auto'`` can be used for convenience/portability.
