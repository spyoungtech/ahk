import ast
import os
import shutil
import subprocess
import sys

import black
from black import check_stability_and_equivalence
from tokenize_rt import reversed_enumerate
from tokenize_rt import src_to_tokens
from tokenize_rt import tokens_to_src

changes = 0


def _rewrite_file(filename: str) -> int:
    with open(filename, encoding='UTF-8') as f:
        contents = f.read()
    tree = ast.parse(contents, filename=filename)
    tokens = src_to_tokens(contents)
    nodes_on_lines_to_remove = []
    for tok in tokens:
        if tok.name == 'COMMENT' and 'unasync: remove' in tok.src:
            nodes_on_lines_to_remove.append(tok.line)
    lines_to_remove = set()
    for node in ast.walk(tree):
        if hasattr(node, 'lineno') and node.lineno in nodes_on_lines_to_remove:
            for lineno in range(node.lineno, node.end_lineno + 1):
                lines_to_remove.add(lineno)
    for i, tok in reversed_enumerate(tokens):
        if tok.line in lines_to_remove:
            tokens.pop(i)
    new_contents = tokens_to_src(tokens)
    if new_contents != contents:
        with open(filename, 'w') as f:
            f.write(new_contents)
    return new_contents != contents


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

    return dst


def main() -> int:
    if os.path.isdir('build'):
        shutil.rmtree('build')
    subprocess.run([sys.executable, 'setup.py', 'build_py'], check=True)
    for root, dirs, files in os.walk('build/lib/ahk/_sync'):
        for fname in files:
            if fname.endswith('.py'):
                fp = os.path.join(root, fname)
                _rewrite_file(fp)
    subprocess.run([sys.executable, '_tests_setup.py', 'build_py'], check=True)
    for root, dirs, files in os.walk('build/lib/tests/_sync'):
        for fname in files:
            if fname.endswith('.py'):
                fp = os.path.join(root, fname)
                _rewrite_file(fp)
    shutil.copytree('build/lib/ahk/_sync', 'ahk/_sync', dirs_exist_ok=True, copy_function=_copyfunc)
    shutil.copytree('build/lib/tests/_sync', 'tests/_sync', dirs_exist_ok=True, copy_function=_copyfunc)

    return changes


if __name__ == '__main__':
    raise SystemExit(main())
