from types import SimpleNamespace
from typing import Any
from typing import NoReturn


class DirectiveMeta(type):
    """
    Overrides __str__ so directives with no arguments can be used without instantiation
    Overrides __hash__ to make objects 'unique' based upon a hash of the str representation
    """

    def __str__(cls) -> str:
        return f'#{cls.__name__}'

    def __hash__(self) -> int:
        return hash(str(self))

    def __eq__(cls, other: Any) -> bool:
        return bool(str(cls) == other)

    @property
    def apply_to_hotkeys_process(cls) -> bool:
        return False


class Directive(SimpleNamespace, metaclass=DirectiveMeta):
    """
    Simple directive class
    They are designed to be hashable and comparable with string equivalent of AHK directive.
    Directives that don't require arguments do not need to be instantiated.
    """

    def __init__(self, **kwargs: Any):
        apply_to_hotkeys = kwargs.pop('apply_to_hotkeys_process', False)
        super().__init__(name=self.name, apply_to_hotkeys_process=apply_to_hotkeys, **kwargs)
        self._kwargs = kwargs

    @property
    def name(self) -> str:
        return self.__class__.__name__

    def __str__(self) -> str:
        if self._kwargs:
            arguments = ' '.join(str(value) for key, value in self._kwargs.items())
        else:
            arguments = ''
        return f'#{self.name} {arguments}'.rstrip()

    def __eq__(self, other: Any) -> bool:
        return bool(str(self) == other)

    def __hash__(self) -> int:  # type: ignore[override]
        return hash(str(self))


class AllowSameLineComments(Directive):
    pass


class ClipboardTimeout(Directive):
    def __init__(self, milliseconds: int = 0, **kwargs: Any):
        kwargs['milliseconds'] = milliseconds
        super().__init__(**kwargs)


class ErrorStdOut(Directive):
    pass


class HotKeyInterval(ClipboardTimeout):
    pass


class HotKeyModifierTimeout(HotKeyInterval):
    pass


class Include(Directive):
    def __init__(self, include_name: str, **kwargs: Any):
        kwargs['include_name'] = include_name
        super().__init__(**kwargs)


class IncludeAgain(Include):
    pass


class InputLevel(Directive):
    def __init__(self, level: int, **kwargs: Any):
        kwargs['level'] = level
        super().__init__(**kwargs)


class InstallKeybdHook(Directive):
    pass


class InstallMouseHook(Directive):
    pass


class KeyHistory(Directive):
    def __init__(self, limit: int = 40, **kwargs: Any):
        kwargs['limit'] = limit
        super().__init__(**kwargs)


class MaxHotkeysPerInterval(Directive):
    def __init__(self, value: int, **kwargs: Any):
        kwargs['value'] = value
        super().__init__(**kwargs)


class MaxMem(Directive):
    def __init__(self, megabytes: int, **kwargs: Any):
        if megabytes < 1:
            raise ValueError('megabytes cannot be less than 1')
        if megabytes > 4095:
            raise ValueError('megabytes cannot exceed 4095')
        kwargs['megabytes'] = megabytes
        super().__init__(**kwargs)


class MaxThreads(Directive):
    def __init__(self) -> NoReturn:
        raise NotImplementedError()


class MaxThreadsBuffer(Directive):
    def __init__(self) -> NoReturn:
        raise NotImplementedError()


class MaxThreadsPerHotkey(Directive):
    def __init__(self) -> NoReturn:
        raise NotImplementedError()


class MenuMaskKey(Directive):
    def __init__(self) -> NoReturn:
        raise NotImplementedError()


class NoTrayIcon(Directive):
    pass


class UseHook(Directive):
    pass


class Warn(Directive):
    pass


class WinActivateForce(Directive):
    pass
