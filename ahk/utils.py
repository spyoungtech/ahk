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


async def async_filter(async_pred, iterable):
    for item in iterable:
        should_yield = await async_pred(item)
        if should_yield:
            yield item