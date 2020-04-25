"""
The :py:mod:`~ahk.script` module, most essentially, houses the :py:class:`~ahk.ScriptEngine` class.

The :py:class:`~ahk.ScriptEngine` is responsible for rendering autohotkey code from jinja templates and executing that
code. This is the heart of how this package works. Every other major component either inherits from this class
or utilizes an instance of this class.

The current implementation of how autohotkey code is executed is by calling the autohotkey
executable with ``subprocess``.


"""
import os
import subprocess
import warnings
from shutil import which
from ahk.utils import make_logger
from ahk.directives import Persistent
from jinja2 import Environment, FileSystemLoader

logger = make_logger(__name__)


class ExecutableNotFoundError(EnvironmentError):
    pass


DEFAULT_EXECUTABLE_PATH = r"C:\Program Files\AutoHotkey\AutoHotkey.exe"
"""The deafult path to look for AutoHotkey, if not specified some other way"""


def _resolve_executable_path(executable_path: str = ''):
    if not executable_path:
        executable_path = os.environ.get('AHK_PATH') or which(
            'AutoHotkey.exe') or which('AutoHotkeyA32.exe')

    if not executable_path:
        if os.path.exists(DEFAULT_EXECUTABLE_PATH):
            executable_path = DEFAULT_EXECUTABLE_PATH

    if not executable_path:
        raise ExecutableNotFoundError(
            'Could not find AutoHotkey.exe on PATH. '
            'Provide the absolute path with the `executable_path` keyword argument '
            'or in the AHK_PATH environment variable.'
        )

    if not os.path.exists(executable_path):
        raise ExecutableNotFoundError(
            f"executable_path does not seems to exist: '{executable_path}' not found")

    if os.path.isdir(executable_path):
        raise ExecutableNotFoundError(
            f"The path {executable_path} appears to be a directory, but should be a file."
            " Please specify the *full path* to the autohotkey.exe executable file"
        )

    if not executable_path.endswith('.exe'):
        warnings.warn(
            'executable_path does not appear to have a .exe extension. This may be the result of a misconfiguration.'
        )

    return executable_path


class ScriptEngine(object):

    def __init__(self, executable_path: str = "", **kwargs):
        """
        This class is typically not used directly. AHK components inherit from this class
        and the arguments for this class should usually be passed in to :py:class:`~ahk.AHK`.

        :param executable_path: the path to the AHK executable.
            If not provided explicitly in this argument, the path to the AHK executable is resolved in the following order:

              * The ``AHK_PATH`` environment variable, if present
              * :py:data:`~ahk.script.DEFAULT_EXECUTABLE_PATH` if the file exists

            If environment variable not present, tries to look for 'AutoHotkey.exe' or 'AutoHotkeyA32.exe' with shutil.which

        :raises ExecutableNotFound: if AHK executable cannot be found or the specified file does not exist
        """
        self.executable_path = _resolve_executable_path(executable_path)

        templates_path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'templates')
        self.env = Environment(loader=FileSystemLoader(templates_path),
                               autoescape=False, trim_blocks=True)

    def render_template(self, template_name, directives=None, blocking=True, **kwargs):
        """
        Renders a given jinja template and returns a string of script text

        :param template_name: the name of the jinja template to render
        :param directives: additional AHK directives to add to the resulting script
        :param blocking: whether the template should be rendered to block (use #Persistent directive)
        :param kwargs: keywords passed to template rendering
        :return: An AutoHotkey script as a string

        .. code-block:: python

            >>> from ahk import AHK
            >>> ahk = AHK()
            >>> ahk.render_template('keyboard/send_input.ahk', s='Hello')
            '#NoEnv\\n#Persistent\\n\\n\\nSendInput Hello\\n\\nExitApp\\n'
        """
        if directives is None:
            directives = set()
        else:
            directives = set(directives)
        if blocking:
            directives.add(Persistent)
        elif Persistent in directives:
            directives.remove(Persistent)

        kwargs['directives'] = directives
        template = self.env.get_template(template_name)
        return template.render(**kwargs)

    def _run_script(self, script_text, **kwargs):
        blocking = kwargs.pop('blocking', True)
        runargs = [self.executable_path, '/ErrorStdOut', '*']
        decode = kwargs.pop('decode', False)
        script_bytes = bytes(script_text, 'utf-8')
        if blocking:
            result = subprocess.run(runargs, input=script_bytes,
                                    stderr=subprocess.PIPE, stdout=subprocess.PIPE, **kwargs)
            if decode:
                logger.debug('Stdout: %s', repr(result.stdout))
                logger.debug('Stderr: %s', repr(result.stderr))
                return result.stdout.decode()
            else:
                return result
        else:
            proc = subprocess.Popen(runargs, stdin=subprocess.PIPE,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, **kwargs)
            try:
                proc.communicate(script_bytes, timeout=0)
            except subprocess.TimeoutExpired:
                pass  # for now, this seems needed to avoid blocking and use stdin
            return proc

    def run_script(self, script_text: str, decode=True, blocking=True, **runkwargs):
        """
        Given an AutoHotkey script as a string, execute it

        :param script_text: a string containing AutoHotkey code
        :param decode: If ``True``, attempt to decode the stdout of the completed process.
            If ``False``, returns the completed process. Only has effect when ``blocking=True``
        :param blocking: If ``True``, script must finish before returning.
            If ``False``, function returns a ``subprocess.Popen`` object immediately without blocking
        :param runkwargs: keyword arguments passed to ``subprocess.Popen`` or ``subprocess.run``
        :return: | A string of the decoded stdout if ``blocking`` and ``decode`` are True.
                 | ``subprocess.CompletedProcess`` if ``blocking`` is True and ``decode`` is False.
                 | ``subprocess.Popen`` object if ``blocking`` is False.

        >>> from ahk import AHK
        >>> ahk = AHK()
        >>> ahk.run_script('FileAppend, Hello World, *')
        'Hello World'
        >>> ahk.run_script('FileAppend, Hello World, *', decode=False)
        CompletedProcess(args=['C:\\\\pathto\\\\AutoHotkey.exe', '/ErrorStdOut', '*'], returncode=0, stdout=b'Hello World', stderr=b'')
        >>> ahk.run_script('FileAppend, Hello World, *', blocking=False)
        <subprocess.Popen at 0x18a599cde10>
        """
        logger.debug('Running script text: %s', script_text)
        try:
            result = self._run_script(script_text, decode=decode, blocking=blocking, **runkwargs)
        except Exception as e:
            logger.fatal('Error running temp script: %s', e)
            raise
        return result
