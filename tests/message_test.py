import pytest

from ahk.message import BooleanResponseMessage
from ahk.message import CoordinateResponseMessage
from ahk.message import ExceptionResponseMessage
from ahk.message import IntegerResponseMessage
from ahk.message import NoValueResponseMessage
from ahk.message import RequestMessage
from ahk.message import ResponseMessage
from ahk.message import StringResponseMessage
from ahk.message import TupleResponseMessage
from ahk.message import WindowIDListResponseMessage


def test_novalue_response_raises_exception_when_sentinel_not_present() -> None:
    msg = NoValueResponseMessage(raw_content=b'something else')
    with pytest.raises(AssertionError):
        msg.unpack()
    return None


def test_novalue_response_sentinel() -> None:
    msg = NoValueResponseMessage(raw_content=b'\xee\x80\x80')
    assert msg.unpack() is None
    return None
