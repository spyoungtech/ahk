from __future__ import annotations

import asyncio
import itertools
import sys
import typing
import warnings
from collections import deque
from dataclasses import dataclass
from typing import Any
from typing import Callable
from typing import TypeVar

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
    from typing_extensions import Concatenate
else:
    from typing import ParamSpec
    from typing import Concatenate

from .directives import Include


@dataclass
class _ExtensionEntry:
    extension: Extension
    method: Callable[..., Any]


T = TypeVar('T')
P = ParamSpec('P')


if typing.TYPE_CHECKING:
    from ahk import AHK, AsyncAHK, Window, AsyncWindow

    TAHK = TypeVar('TAHK', bound=typing.Union[AHK[Any], AsyncAHK[Any]])
    TWindow = TypeVar('TWindow', bound=typing.Union[Window, AsyncWindow])


@dataclass
class _ExtensionMethodRegistry:
    sync_methods: dict[str, Callable[..., Any]]
    async_methods: dict[str, Callable[..., Any]]
    sync_window_methods: dict[str, Callable[..., Any]]
    async_window_methods: dict[str, Callable[..., Any]]

    def register(self, f: Callable[Concatenate[TAHK, P], T]) -> Callable[Concatenate[TAHK, P], T]:
        if asyncio.iscoroutinefunction(f):
            if f.__name__ in self.async_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.async_methods[f.__name__]!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.async_methods[f.__name__] = f
        else:
            if f.__name__ in self.sync_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.sync_methods[f.__name__]!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.sync_methods[f.__name__] = f
        return f

    def register_window_method(self, f: Callable[Concatenate[TWindow, P], T]) -> Callable[Concatenate[TWindow, P], T]:
        if asyncio.iscoroutinefunction(f):
            if f.__name__ in self.async_window_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.async_window_methods[f.__name__]!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.async_window_methods[f.__name__] = f
        else:
            if f.__name__ in self.sync_window_methods:
                warnings.warn(
                    f'Method of name {f.__name__!r} has already been registered. '
                    f'Previously registered method {self.sync_window_methods[f.__name__]!r} '
                    f'will be overridden by {f!r}',
                    stacklevel=2,
                )
            self.sync_window_methods[f.__name__] = f
        return f

    def merge(self, other: _ExtensionMethodRegistry) -> None:
        for name, method in other.methods:
            self.register(method)
        for name, method in other.window_methods:
            self.register_window_method(method)

    @property
    def methods(self) -> list[tuple[str, Callable[..., Any]]]:
        return list(itertools.chain(self.async_methods.items(), self.sync_methods.items()))

    @property
    def window_methods(self) -> list[tuple[str, Callable[..., Any]]]:
        return list(itertools.chain(self.async_window_methods.items(), self.sync_window_methods.items()))


_extension_registry: dict[Extension, _ExtensionMethodRegistry] = {}


class Extension:
    def __init__(
        self,
        script_text: str | None = None,
        includes: list[str] | None = None,
        dependencies: list[Extension] | None = None,
        requires_autohotkey: typing.Literal['v1', 'v2'] | None = None,
    ):
        self._requires = requires_autohotkey
        self._text: str = script_text or ''
        self._includes: list[str] = includes or []
        self.dependencies: list[Extension] = dependencies or []
        self._extension_method_registry: _ExtensionMethodRegistry = _ExtensionMethodRegistry(
            sync_methods={}, async_methods={}, sync_window_methods={}, async_window_methods={}
        )
        _extension_registry[self] = self._extension_method_registry

    @property
    def script_text(self) -> str:
        return self._text

    @script_text.setter
    def script_text(self, new_script: str) -> None:
        self._text = new_script

    @property
    def includes(self) -> list[Include]:
        return [Include(inc) for inc in self._includes]

    def register(self, f: Callable[Concatenate[TAHK, P], T]) -> Callable[Concatenate[TAHK, P], T]:
        self._extension_method_registry.register(f)
        return f

    register_method = register

    def register_window_method(self, f: Callable[Concatenate[TWindow, P], T]) -> Callable[Concatenate[TWindow, P], T]:
        self._extension_method_registry.register_window_method(f)
        return f

    def __hash__(self) -> int:
        return hash((self._text, tuple(self.includes), tuple(self.dependencies)))

    def __eq__(self, other: Any) -> bool:
        if isinstance(other, Extension):
            return hash(self) == hash(other)
        return NotImplemented


def _resolve_extension(extension: Extension, seen: set[Extension]) -> list[Extension]:
    ret: deque[Extension] = deque()
    todo = [extension]
    while todo:
        ext = todo.pop()
        if ext in seen:
            continue
        ret.appendleft(ext)
        seen.add(ext)
        todo.extend(ext.dependencies)
    return list(ret)


def _resolve_extensions(extensions: list[Extension]) -> list[Extension]:
    seen: set[Extension] = set()
    ret: list[Extension] = []
    for ext in extensions:
        ret.extend(_resolve_extension(ext, seen=seen))
    return ret


def _resolve_includes(extensions: list[Extension]) -> list[Include]:
    extensions = _resolve_extensions(extensions)
    ret = []
    seen: set[Include] = set()
    for ext in extensions:
        for include in ext.includes:
            if include in seen:
                continue
            ret.append(include)
    return ret
