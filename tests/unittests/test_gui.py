from pytest import fixture, raises

from ahk import AHK


class TestGuiMixin:
    @fixture(scope="class")
    def ahk(self) -> AHK:
        return AHK()

    def test_show_tooltip(self, ahk: AHK):
        ahk.show_tooltip("hello")

        with raises(ValueError):
            ahk.show_tooltip("hello", id=30)
