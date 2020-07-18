from pytest import fixture, raises

from ahk import AHK


class TestGuiMixin:
    @fixture(scope="class")
    def ahk(self) -> AHK:
        return AHK()

    def test_show_tooltip(self, ahk: AHK):
        ahk.show_tooltip("hello")
        ahk.show_tooltip("🚀 Hello unicode 🚀", second=2)
        ahk.show_tooltip("⽲ hello3", x=10, y=10)
        ahk.show_tooltip("hello4", second=2, x=10, y=10)

        with raises(ValueError):
            ahk.show_tooltip("hello", id=30)

    def test_show_traytip(self, ahk: AHK):
        ahk._show_traytip("⽲ Normal 🚀", "It's me")
        ahk._show_traytip("🐌 Slow 🐌", "It's you", second=2)
        ahk._show_traytip("Info", "It's info", type_id=ahk.TRAYTIP_INFO)
        ahk.show_info_traytip("Info", "It's also info")
        ahk.show_warning_traytip("Warning", "It's warning")
        ahk.show_error_traytip("Error", "It's error")
        ahk._show_traytip("Slient - Info", "It's info", type_id=ahk.TRAYTIP_INFO, slient=True)
        ahk.show_info_traytip("Unicode Threaded", "şüğı", blocking=False)  # Need help
