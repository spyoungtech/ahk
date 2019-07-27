import abc
import atexit
import pathlib
import os
import threading
import win32file
import win32event
import win32con

from ahk.utils import make_logger

logger = make_logger(__name__)

class Abstract_Communicator(metaclass=abc.ABCMeta):

    last_pass_dict = {}
    this_pass_dict = {}

    def __init__(self, directory):
        if type(directory) == str:
            self.path = pathlib.Path(directory)     
        self.path = pathlib.Path(directory)
        
        # "Cover your ass in assert statements" - Unremembered Author.
        if not type(self.path) == pathlib.Path and not type(self.path) == pathlib.WindowsPath:
            raise TypeError("Expected pathlib.path or pathlib.WindowsPath but got"+ 
                f" type {type(self.path)}")

        assert self.path.exists() == True, f"The given path doesn't exist: {str(self.path)}"
        assert self.path.is_dir() == True, ("The given path must"+
            f" be a directory: {str(self.path)}")
        
        self.stop_thread = False
        self.thread = threading.Thread(target=self.event_loop)
        self.thread.daemon = True
        self.thread.start()

    def stop_loop(self):
        self.stop_thread = True

    def get_changed_file(self)->set:
        # Some fancy pants dictionary comprehension that uses the path to cycle through
        # all of the files in the path, make the file path the key, and set the value
        # to the last time it was modified
        self.this_pass_dict={self.path/i:os.path.getmtime(str(self.path/i))
             for i in os.listdir(str(self.path))}

        # Compares the two dicts and copies the ones that are the same to a variable
        matching = self.last_pass_dict.items() & self.this_pass_dict.items()
        # Reconstruct a dictionary out of the returned set from above
        matching = {e[0]:e[1] for e in matching}
        # Removes the matching keys, returning only that files that have changed
        different = self.this_pass_dict.keys() - matching.keys()
        # Update the last_pass dictionary to the latest files
        self.last_pass_dict = self.this_pass_dict.copy()
        # If there are any files that have changed, return them
        if different != set():
            return different
        
    @abc.abstractmethod
    def on_event(self):
        pass

    def event_loop(self):
        change_handle = win32file.FindFirstChangeNotification (
        str(self.path),
        0,
        win32con.FILE_NOTIFY_CHANGE_LAST_WRITE
        )

        try:
            while self.stop_thread == False:
                result = win32event.WaitForSingleObject (change_handle, 500)

                #
                # If the WaitFor... returned because of a notification (as
                #  opposed to timing out or some error) then look for the
                #  changes in the directory contents.
                #
                if result == win32con.WAIT_OBJECT_0:
                    self.on_event()
                win32file.FindNextChangeNotification (change_handle)
        except KeyboardInterrupt:
            self.stop_thread = True
        finally:
            win32file.FindCloseChangeNotification (change_handle)
            logger.debug("stopping notification loop")

class EventListener(Abstract_Communicator):

    code_dict={}    

    def __init__(self):
        atexit.register(self.cleanup)
        super().__init__(pathlib.Path(
            os.path.abspath(os.path.dirname(__file__))).parents[0]/"tmp")

    def on_event(self):
        changed_files = self.get_changed_file()
        for i in changed_files:
            self._call_keycode(os.path.basename(i))

    def cleanup(self):
        self.stop_loop()
        for i in os.listdir(str(self.path)):
            print(os.path.join(self.path, i))
            os.remove(os.path.join(self.path, i))

    def _call_keycode(self, code):
        try:
            functions = self.code_dict[code]
            for i in functions:
                i()
        except KeyError:
            logger.info("not my keycode!")

    def add(self, keycode, function_to_bind):
        try:
            existing = self.code_dict[keycode]
            existing.append(function_to_bind)
            self.code_dict[keycode] = existing
        except KeyError:
            self.code_dict[keycode] = [function_to_bind]

    def remove(self, keycode, function_to_bind):
        try:
            existing = self.code_dict[keycode]
        except KeyError:
            return False
        for i in range(0, len(existing)-1):
            if existing[i] == function_to_bind:
                del existing[i]