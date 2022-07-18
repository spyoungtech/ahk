import ast
import io
import itertools
import string
import typing
from abc import ABC
from abc import abstractmethod
from typing import Any
from typing import cast
from typing import Generator
from typing import Generic
from typing import Literal
from typing import NoReturn
from typing import Optional
from typing import Protocol
from typing import runtime_checkable
from typing import Tuple
from typing import Type
from typing import TypedDict
from typing import TypeGuard
from typing import TypeVar
from typing import Union


class OutOfMessageTypes(Exception):
    ...


@runtime_checkable
class BytesLineReadable(Protocol):
    def readline(self) -> bytes:
        ...


def is_window_control_list_response(resp_obj: object) -> TypeGuard[Tuple[str, Tuple[str, ...]]]:
    if not isinstance(resp_obj, tuple):
        return False
    if len(resp_obj) != 2:
        return False
    if not isinstance(resp_obj[0], str):
        return False
    expected_win_list = resp_obj[1]
    if not isinstance(expected_win_list, tuple):
        return False
    for obj in expected_win_list:
        if not isinstance(obj, str):
            return False
    return True


def is_winget_response_type(
    obj: object,
) -> TypeGuard[
    Union[
        'StringResponseMessage',
        'IntegerResponseMessage',
        'WindowIDListResponseMessage',
        'WindowControlListResponseMessage',
    ]
]:
    if isinstance(obj, StringResponseMessage):
        return True
    elif isinstance(obj, IntegerResponseMessage):
        return True
    elif isinstance(obj, WindowIDListResponseMessage):
        return True
    elif isinstance(obj, WindowControlListResponseMessage):
        return True
    else:
        return False


T_ResponseMessageType = TypeVar('T_ResponseMessageType', bound='ResponseMessage')


def tom_generator() -> Generator[bytes, None, None]:
    characters = string.digits + string.ascii_letters
    for a, b, c in itertools.product(characters, characters, characters):
        yield bytes(f'{a}{b}{c}', encoding='ascii')
    raise OutOfMessageTypes('Out of TOMS')


TOMS = tom_generator()


class ResponseMessage:
    type: Optional[str] = None
    _type_order_mark = next(TOMS)

    @classmethod
    def __init_subclass__(cls: Type[T_ResponseMessageType], **kwargs: Any) -> None:
        tom = next(TOMS)
        cls._type_order_mark = tom
        assert tom not in _message_registry, f'cannot register class {cls!r} with TOM {tom!r} which is already in use'
        _message_registry[tom] = cls
        assert cls.type is not None, f'must assign a type for class {cls!r}'
        super().__init_subclass__(**kwargs)

    def __init__(self, raw_content: bytes):
        self._raw_content: bytes
        self._raw_content = raw_content

    def __repr__(self) -> str:
        return f'ResponseMessage<type={self.type!r}>'

    @staticmethod
    def _tom_lookup(tom: bytes) -> 'ResponseMessageClassTypes':
        klass = _message_registry.get(tom)
        if klass is None:
            raise ValueError(f'No such TOM {tom!r}')
        return klass

    @classmethod
    def from_bytes(cls: Type[T_ResponseMessageType], b: bytes) -> 'ResponseMessageTypes':
        tom, _, message_bytes = b.split(b'\n', 2)
        klass = cls._tom_lookup(tom)
        return klass(raw_content=message_bytes)

    def to_bytes(self) -> bytes:
        content_lines = self._raw_content.count(b'\n')
        return self._type_order_mark + b'\n' + bytes(str(content_lines), 'ascii') + b'\n' + self._raw_content

    @abstractmethod
    def unpack(self) -> Any:
        return NotImplemented


_message_registry: dict[bytes, 'ResponseMessageClassTypes']
_message_registry = {ResponseMessage._type_order_mark: ResponseMessage}


class TupleResponseMessage(ResponseMessage):
    type = 'tuple'

    def unpack(self) -> Tuple[Any, ...]:
        s = self._raw_content.decode(encoding='utf-8')
        val = ast.literal_eval(s)
        assert isinstance(val, tuple)
        return val


class CoordinateResponseMessage(ResponseMessage):
    type = 'coordinate'

    def unpack(self) -> Tuple[int, int]:
        s = self._raw_content.decode(encoding='utf-8')
        val = ast.literal_eval(s)
        assert isinstance(val, tuple)
        x, y = cast(Tuple[int, int], val)
        return x, y


class IntegerResponseMessage(ResponseMessage):
    type = 'integer'

    def unpack(self) -> int:
        s = self._raw_content.decode(encoding='utf-8')
        val = ast.literal_eval(s)
        assert isinstance(val, int)
        return val


class BooleanResponseMessage(IntegerResponseMessage):
    type = 'boolean'

    def unpack(self) -> bool:
        val = super().unpack()
        assert val in (1, 0)
        return bool(val)


class StringResponseMessage(ResponseMessage):
    type = 'string'

    def unpack(self) -> str:
        return self._raw_content.decode('utf-8')


class WindowIDListResponseMessage(ResponseMessage):
    type = 'windowidlist'

    def unpack(self) -> list[str]:
        s = self._raw_content.decode(encoding='utf-8')
        return s.split(',')


class NoValueResponseMessage(ResponseMessage):
    type = 'novalue'

    def unpack(self) -> None:
        assert self._raw_content == b'\xee\x80\x80', f'Unexpected or Malformed response: {self._raw_content!r}'
        return None


class AHKExecutionException(Exception):
    pass


class ExceptionResponseMessage(ResponseMessage):
    type = 'exception'

    def unpack(self) -> NoReturn:
        s = self._raw_content.decode(encoding='utf-8')
        raise AHKExecutionException(s)


class WindowControlListResponseMessage(ResponseMessage):
    type = 'windowcontrollist'

    def unpack(self) -> Tuple[str, Tuple[str, ...]]:
        s = self._raw_content.decode(encoding='utf-8')
        val = ast.literal_eval(s)
        assert is_window_control_list_response(val)
        return val


T_RequestMessageType = TypeVar('T_RequestMessageType', bound='RequestMessage')


class RequestMessage:
    def __init__(self, function_name: str, args: Optional[list[str]] = None):
        self.function_name: str = function_name
        self.args: list[str] = args or []


ResponseMessageTypes = Union[
    ResponseMessage,
    TupleResponseMessage,
    CoordinateResponseMessage,
    IntegerResponseMessage,
    BooleanResponseMessage,
    StringResponseMessage,
    WindowIDListResponseMessage,
    NoValueResponseMessage,
    WindowControlListResponseMessage,
    ExceptionResponseMessage,
]
ResponseMessageClassTypes = Union[
    Type[TupleResponseMessage],
    Type[CoordinateResponseMessage],
    Type[IntegerResponseMessage],
    Type[BooleanResponseMessage],
    Type[StringResponseMessage],
    Type[WindowIDListResponseMessage],
    Type[NoValueResponseMessage],
    Type[WindowControlListResponseMessage],
    Type[ExceptionResponseMessage],
    Type[ResponseMessage],
]
