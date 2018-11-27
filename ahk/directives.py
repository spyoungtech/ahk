from types import SimpleNamespace


class DirectiveMeta(type):
    """
    Overrides __str__ so directives with no arguments can be used without instantiation
    Overrides __hash__ to make objects 'unique' based upon a hash of the str representation
    """
    def __str__(cls):
        return f"#{cls.__name__}"

    def __hash__(self):
        return hash(str(self))

    def __eq__(cls, other):
        return str(cls) == other


class Directive(SimpleNamespace, metaclass=DirectiveMeta):
    """
    Simple directive class
    They are designed to be hashable and comparable with string equivalent of AHK directive.
    Directives that don't require arguments do not need to be instantiated.
    """
    def __init__(self, **kwargs):
        super().__init__(name=self.name, **kwargs)
        self._kwargs = kwargs

    @property
    def name(self):
        return self.__class__.__name__

    def __str__(self):
        if self._kwargs:
            arguments = ' '.join(str(value) for key, value in self._kwargs.items())
        else:
            arguments = ''
        return f"#{self.name} {arguments}".rstrip()

    def __eq__(self, other):
        return str(self) == other

    def __hash__(self):
        return hash(str(self))


class AllowSameLineComments(Directive):
    pass


class ClipboardTimeout(Directive):
    def __init__(self, milliseconds=0, **kwargs):
        kwargs['milliseconds'] = milliseconds
        super().__init__(**kwargs)


class ErrorStdOut(Directive):
    pass


class HotKeyInterval(ClipboardTimeout):
    pass


class HotKeyModifierTimeout(HotKeyInterval):
    pass


class Include(Directive):
    def __init__(self, include_name, **kwargs):
        kwargs['include_name'] = include_name
        super().__init__(**kwargs)


class IncludeAgain(Include):
    pass


class InputLevel(Directive):
    def __init__(self, level, **kwargs):
        kwargs['level'] = level
        super().__init__(**kwargs)


class InstallKeybdHook(Directive):
    pass


class InstallMouseHook(Directive):
    pass


class KeyHistory(Directive):
    def __init__(self, limit=40, **kwargs):
        kwargs['limit'] = limit
        super().__init__(**kwargs)


class MaxHotkeysPerInterval(Directive):
    def __init__(self, value, **kwargs):
        kwargs['value'] = value
        super().__init__(**kwargs)


class MaxMem(Directive):
    def __init__(self, megabytes: int, **kwargs):
        if megabytes < 1:
            raise ValueError('megabytes cannot be less than 1')
        if megabytes > 4095:
            raise ValueError('megabytes cannot exceed 4095')
        kwargs['megabytes'] = megabytes
        super().__init__(**kwargs)


class MaxThreads(Directive):
    def __init__(self):
        raise NotImplemented


class MaxThreadsBuffer(Directive):
    def __init__(self):
        raise NotImplemented


class MaxThreadsPerHotkey(Directive):
    def __init__(self):
        raise NotImplemented


class MenuMaskKey(Directive):
    def __init__(self):
        raise NotImplemented


class NoEnv(Directive):
    pass


class NoTrayIcon(Directive):
    pass


class Persistent(Directive):
    pass


class SingleInstance(Directive):
    pass


class UseHook(Directive):
    pass


class Warn(Directive):
    pass


class WinActivateForce(Directive):
    pass
