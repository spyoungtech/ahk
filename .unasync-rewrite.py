import os
import shutil
import subprocess
import sys

import black

GIT_EXECUTABLE = shutil.which('git')

changes = 0


def _copyfunc(src, dst, *, follow_symlinks=True):
    global changes
    with open(src, encoding='UTF-8') as f:
        contents = f.read()
    if os.path.exists(dst):
        with open(dst, encoding='UTF-8') as dst_f:
            dst_contents = dst_f.read()
        try:
            black.assert_equivalent(
                src=contents,
                dst=dst_contents,
            )
        except AssertionError:
            changes += 1
            print('MODIFIED', dst)
            shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
    else:
        changes += 1
        print('ADDED', dst)
        shutil.copy2(src, dst, follow_symlinks=follow_symlinks)
        if GIT_EXECUTABLE is None:
            print('WARNING could not find git!', file=sys.stderr)
        else:
            subprocess.run([GIT_EXECUTABLE, 'add', '--intent-to-add', dst])
    return dst


def main() -> int:
    if os.path.isdir('build'):
        shutil.rmtree('build')
    subprocess.run([sys.executable, 'setup.py', 'build_py'], check=True)
    subprocess.run([sys.executable, '_tests_setup.py', 'build_py'], check=True)
    shutil.copytree('build/lib/ahk/_sync', 'ahk/_sync', dirs_exist_ok=True, copy_function=_copyfunc)
    shutil.copytree('build/lib/tests/_sync', 'tests/_sync', dirs_exist_ok=True, copy_function=_copyfunc)

    return changes


if __name__ == '__main__':
    raise SystemExit(main())
