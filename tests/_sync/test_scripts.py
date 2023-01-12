import pathlib
import time
import unittest.mock

from ahk import AHK
from ahk import Window


class TestScripts(unittest.TestCase):
    win: Window

    def setUp(self) -> None:
        self.ahk = AHK()

    def tearDown(self) -> None:
        try:
            self.ahk._transport._proc.kill()
        except:
            pass
        time.sleep(0.2)

    def test_script_missing_makes_tempfile(self):
        with unittest.mock.patch('os.path.exists', new=unittest.mock.Mock(return_value=False)):
            pos = self.ahk.get_mouse_position()
            path = pathlib.Path(self.ahk._transport._proc.runargs[-1])
            filename = path.name
            assert filename.startswith('python-ahk-')
            assert filename.endswith('.ahk')
            assert isinstance(pos, tuple) and isinstance(pos[0], int)
