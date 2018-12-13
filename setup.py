from setuptools import setup
from io import open
test_requirements = ['pyautogui', 'behave', 'behave-classy', 'coverage']
extras = {'test': test_requirements}

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ahk',
    version='0.2.2',
    url='https://github.com/spyoungtech/ahk',
    description='A Python wrapper for AHK',
    long_description=long_description,
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['ahk'],
    install_requires=[],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Desktop Environment',
        'Programming Language :: Python',
        'Environment :: Win32 (MS Windows)',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    tests_require=test_requirements,
)
