from textwrap import dedent
import logging

logger = logging.getLogger('ahk')


def make_script(body, directives=None, persistent=True):
    """
    Convenience function to dedent script body as well as add #Persistent directive and Exit/ExitApp
    :param body: body of the script
    :param directives: an iterable of directives to add to the script.
    :type directives: str or ahk.directives.Directive
    :param persistent: if the #Persistent directive should be added (causes script to be blocking)
    :return:
    """
    exit_ = 'ExitApp'
    if directives is None:
        directives = set()
    else:
        directives = set(directives)

    if persistent:
        directives.add('#Persistent')

    dirs = '\n'.join(str(directive) for directive in directives)

    script = dedent(f'''\
        {dirs}
        {body}
        {exit_}
        ''')
    return script
