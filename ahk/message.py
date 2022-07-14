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
from typing import TypeVar
from typing import Union


class OutOfMessageTypes(Exception):
    ...


@runtime_checkable
class BytesLineReadable(Protocol):
    def readline(self) -> bytes:
        ...


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
    def _tom_lookup(tom: bytes) -> Type['ResponseMessage']:
        klass = _message_registry.get(tom)
        if not klass:
            raise ValueError(f'No such TOM {tom!r}')
        return klass

    @classmethod
    def from_bytes(cls: Type[T_ResponseMessageType], b: bytes) -> T_ResponseMessageType:
        tom, _, message_bytes = b.split(b'\n', 2)
        klass = cls._tom_lookup(tom)
        return klass(raw_content=message_bytes)  # type: ignore[return-value]

    @classmethod
    def from_stream(cls: Type[T_ResponseMessageType], stream: BytesLineReadable) -> T_ResponseMessageType:
        content_buffer = io.BytesIO()
        tom = stream.readline().strip()
        content_lines = stream.readline().strip()
        for _ in range(int(content_lines) + 1):
            part = stream.readline()
            content_buffer.write(part)
        contents = content_buffer.getvalue()
        message_bytes = tom + b'\n' + content_lines + b'\n' + contents
        return cls.from_bytes(message_bytes)

    def to_bytes(self) -> bytes:
        content_lines = self._raw_content.count(b'\n')
        return self._type_order_mark + b'\n' + bytes(str(content_lines), 'ascii') + b'\n' + self._raw_content

    @abstractmethod
    def unpack(self) -> Any:
        return NotImplemented


_message_registry: dict[bytes, Type[ResponseMessage]]
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


T_RequestMessageType = TypeVar('T_RequestMessageType', bound='RequestMessage')


class RequestMessage:
    def __init__(self, function_name: str, args: Optional[list[str]] = None):
        self.function_name: str = function_name
        self.args: list[str] = args or []
