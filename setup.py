from setuptools import setup
from io import open
test_requirements = ['behave', 'behave-classy', 'pytest']
extras = {'test': test_requirements}

with open('README.md', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='ahk',
    version='0.4.0',
    url='https://github.com/spyoungtech/ahk',
    description='A Python wrapper for AHK',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    packages=['ahk'],
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
    ],
    tests_require=test_requirements,
    include_package_data=True,
    zip_safe=False
)
