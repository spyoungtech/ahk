from __future__ import annotations

import asyncio
import sys
import warnings
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

from .directives import Include


@dataclass
class _ExtensionEntry:
    extension: Extension
    method: Callable[..., Any]


T = TypeVar('T')
P = ParamSpec('P')


@dataclass
class _ExtensionMethodRegistry:
    sync_methods: dict[str, _ExtensionEntry]
    async_methods: dict[str, _ExtensionEntry]

    def register(self, ext: Extension, f: Callable[P, T]) -> Callable[P, T]:
        if asyncio.iscoroutinefunction(f):
            if f.__name__ in self.async_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.async_methods[f.__name__].method!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.async_methods[f.__name__] = _ExtensionEntry(extension=ext, method=f)
        else:
            if f.__name__ in self.sync_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.sync_methods[f.__name__].method!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.sync_methods[f.__name__] = _ExtensionEntry(extension=ext, method=f)
        return f

    def merge(self, other: _ExtensionMethodRegistry) -> None:
        for fname, entry in other.async_methods.items():
            async_method = entry.method
            if async_method.__name__ in self.async_methods:
                warnings.warn(
                    f'Method of name {async_method.__name__!r} has already been registered. '
                    f'Previously registered method {self.async_methods[async_method.__name__].method!r} '
                    f'will be overridden by {async_method!r}'
                )
            self.async_methods[async_method.__name__] = entry
        for fname, entry in other.sync_methods.items():
            method = entry.method
            if method.__name__ in self.sync_methods:
                warnings.warn(
                    f'Method of name {method.__name__!r} has already been registered. '
                    f'Previously registered method {self.sync_methods[method.__name__].method!r} '
                    f'will be overridden by {method!r}'
                )
            self.sync_methods[method.__name__] = entry


_extension_method_registry = _ExtensionMethodRegistry(sync_methods={}, async_methods={})


class Extension:
    def __init__(
        self,
        includes: list[str] | None = None,
        script_text: str | None = None,
        # template: str | Template | None = None
    ):
        self._text: str = script_text or ''
        # self._template: str | Template | None = template
        self._includes: list[str] = includes or []
        self._extension_method_registry = _ExtensionMethodRegistry(sync_methods={}, async_methods={})

    @property
    def script_text(self) -> str:
        return self._text

    @script_text.setter
    def script_text(self, new_script: str) -> None:
        self._text = new_script

    @property
    def includes(self) -> list[Include]:
        return [Include(inc) for inc in self._includes]

    def register(self, f: Callable[P, T]) -> Callable[P, T]:
        self._extension_method_registry.register(self, f)
        _extension_method_registry.register(self, f)
        return f
