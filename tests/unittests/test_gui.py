from pytest import fixture, raises

from ahk import AHK


class TestGuiMixin:
    @fixture(scope="class")
    def ahk(self) -> AHK:
        return AHK()

    def test_show_tooltip(self, ahk: AHK):
        ahk.show_tooltip("hello")
        ahk.show_tooltip("hello2", ms=2000)
        ahk.show_tooltip("hello3", x=10, y=10)
        ahk.show_tooltip("hello4", ms=2000, x=10, y=10)

        with raises(ValueError):
            ahk.show_tooltip("hello", id=30)
