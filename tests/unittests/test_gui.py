from pytest import fixture, raises

from ahk import AHK


class TestGuiMixin:
    @fixture(scope="class")
    def ahk(self) -> AHK:
        return AHK()

    def test_show_tooltip(self, ahk: AHK):
        ahk.show_tooltip("hello")
        ahk.show_tooltip("hello2", second=2)
        ahk.show_tooltip("hello3", x=10, y=10)
        ahk.show_tooltip("hello4", second=2, x=10, y=10)

        with raises(ValueError):
            ahk.show_tooltip("hello", id=30)

    def test_show_traytip(self, ahk: AHK):
        ahk.show_traytip("Normal", "It's me")
        ahk.show_traytip("Slow", "It's you", second=2)
        ahk.show_traytip("Info", "It's info", type_id=ahk.TRAYTIP_INFO)
        ahk.show_traytip("Warning", "It's warning", type_id=ahk.TRAYTIP_WARNING_)
        ahk.show_traytip("Error", "It's error", type_id=ahk.TRAYTIP_ERROR)
        ahk.show_traytip("Slient - Info", "It's info", type_id=ahk.TRAYTIP_INFO, slient=True)
