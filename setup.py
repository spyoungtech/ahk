from setuptools import setup
from io import open

test_requirements = ['behave', 'behave-classy', 'pytest']
extras = {'test': test_requirements}

with open('docs/README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ahk',
    version='0.14.0',
    url='https://github.com/spyoungtech/ahk',
    description='A Python wrapper for AHK',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['ahk'],
    extras_require={
        'binary': ['ahk-binary==1.1.33.9'],
    },
    install_requires=['jinja2'],
    classifiers=[
        'Intended Audience :: Developers',
        'Topic :: Desktop Environment',
        'Programming Language :: Python',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    tests_require=test_requirements,
    include_package_data=True,
    zip_safe=False,
    keywords=['ahk', 'autohotkey', 'windows', 'mouse', 'keyboard', 'automation', 'pyautogui'],
)
