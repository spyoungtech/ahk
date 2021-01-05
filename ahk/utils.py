import logging
import functools
from asyncio import coroutine

ESCAPE_SEQUENCE_MAP = {
    '\n': '`n',
    '\t': '`t',
    '\r': '`r',
    '\a': '`a',
    '\b': '`b',
    '\f': '`f',
    '\v': '`v',
    ',': '`,',
    '%': '`%',
    '`': '``',
    ';': '`;',
    ':': '`:',
    '!': '{!}',
    '^': '{^}',
    '+': '{+}',
    '{': '{{}',
    '}': '{}}',
    '#': '{#}',
    '=': '{=}'
}

_TRANSLATION_TABLE = str.maketrans(ESCAPE_SEQUENCE_MAP)

def make_logger(name):
    logger = logging.getLogger(name)
    handler = logging.NullHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def escape_sequence_replace(s):
    """
    Replace Python escape sequences with AHK equivalent escape sequences
    Additionally escapes some other characters for AHK escape sequences.
    Intended for use with AHK Send command functions.

    Note: This DOES NOT provide ANY assurances against accidental or malicious injection. Does NOT escape quotes.

    >>> escape_sequence_replace('Hello, World!')
    'Hello`, World{!}'
    """
    return s.translate(_TRANSLATION_TABLE)

def asyncify(cls, sync_method):
    @functools.wraps(sync_method)
    async def async_method(self, *args, **kwargs):
        self_sync_method = getattr(super(cls, self), sync_method.__name__)
        coro = self_sync_method(*args, **kwargs)
        return await coro
    return async_method

class AsyncifyMeta(type):
    def __new__(cls, *args, **kwargs):
        asyncifyable = getattr(cls, '_asyncifyable', None)
        if not asyncifyable:
            return cls

        for name in asyncifyable:
            obj = getattr(cls, name)
            if not callable(obj) or isinstance(obj, type) or isinstance(obj, property):
                raise ValueError(f'{repr(obj)} object is not asyncifyable)')
            setattr(cls, f'{name}', asyncify(cls, obj))
        return super().__new__(cls, *args, **kwargs)

async def async_filter(async_pred, iterable):
    for item in iterable:
        should_yield = await async_pred(item)
        if should_yield:
            yield item