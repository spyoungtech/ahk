from ahk import AHK


def test_mouse_move():
    ahk = AHK()
    ahk.mouse_move(100, 100)
    assert ahk.get_mouse_position() == (100, 100)
