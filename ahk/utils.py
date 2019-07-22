import abc
import logging
import pathlib
import threading
import os
import win32file
import win32event
import win32con

ESCAPE_SEQUENCE_MAP = {
    '\n': '`n',
    '\t': '`t',
    '\r': '`r',
    '\a': '`a',
    '\b': '`b',
    '\f': '`f',
    '\v': '`v',
    ',': '`,',
    '%': '`%',
    '`': '``',
    ';': '`;',
    ':': '`:',
    '!': '{!}',
    '^': '{^}',
    '+': '{+}',
    '{': '{{}',
    '}': '{}}',
    '#': '{#}'
}

_TRANSLATION_TABLE = str.maketrans(ESCAPE_SEQUENCE_MAP)

def make_logger(name):
    logger = logging.getLogger(name)
    handler = logging.NullHandler()
    formatter = logging.Formatter(
            '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    return logger


def escape_sequence_replace(s):
    """
    Replace Python escape sequences with AHK equivalent escape sequences
    Additionally escapes some other characters for AHK escape sequences.
    Intended for use with AHK Send command functions.

    Note: This DOES NOT provide ANY assurances against accidental or malicious injection. Does NOT escape quotes.

    >>> escape_sequence_replace('Hello, World!')
    'Hello`, World{!}'
    """
    return s.translate(_TRANSLATION_TABLE)

class Abstract_Communicator(metaclass=abc.ABCMeta):

    def __init__(self, directory:str):

        if directory == None:
            self.path = pathlib.Path(os.path.abspath(".")) / "tmp"
        else:
            if type(directory) != str: 
                raise TypeError(f"Expected type str, but got type {type(directory)}")
            
            self.path = pathlib.Path(directory)
        if not self.path.exists():
            raise FileNotFoundError(f"The directory or file at {self.path} doesn't exist")
        
        self.stop_thread = False
        self.thread = threading.Thread(target=self.event_loop)
        self.thread.start()

    def __del__(self):
        self.stop_thread = True  

    @abc.abstractmethod
    def on_event(self):
        print("An event!!!")

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

        finally:
            win32file.FindCloseChangeNotification (change_handle)

class EventListener(Abstract_Communicator):

    code_dict={}    

    def on_event(self):
        return super().on_event()

    def _call_keycode(self, code):
        functions = self.code_dict[code]
        for i in functions:
            i[0]()

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

                
