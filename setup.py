from setuptools import setup

test_requirements = ['pyautogui', 'behave', 'behave-classy', 'coverage']
extras = {'test': test_requirements}


setup(
    name='ahk',
    version='0.2.1',
    url='https://github.com/spyoungtech/ahk',
    description='A Python wrapper for AHK',
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['ahk'],
    install_requires=[],
    tests_require=test_requirements,
)
