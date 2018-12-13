import sys
import os
import time
project_root = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..'))
sys.path.insert(0, project_root)
from ahk import AHK
import subprocess
ahk = AHK()

def test_get_calculator():
    with subprocess.Popen('calc') as p:
        time.sleep(2)  # give calculator some time to start up;  may replace this once WinWait is implemented
        win = ahk.win_get(title='Calculator')
        assert win
        assert win.position
