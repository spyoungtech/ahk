class AHKBaseException(Exception):
    # TODO: make existing exceptions subclasses of this
    ...


class WindowNotFoundException(AHKBaseException): ...


class AHKProtocolError(AHKBaseException): ...


class AHKExecutionException(AHKBaseException):
    pass


class AhkExecutableNotFoundError(AHKBaseException, EnvironmentError):
    pass
