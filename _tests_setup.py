"""
Not a real setup package
This is just to unasync our tests files
"""
import setuptools
import unasync

setuptools.setup(
    name='ahk',
    version='0.0.1',
    author='Example Author',
    author_email='author@example.com',
    description='A package used to test customized unasync',
    url='https://github.com/pypa/sampleproject',
    packages=['tests', 'tests._async'],
    cmdclass={
        'build_py': unasync.cmdclass_build_py(
            rules=[
                unasync.Rule(
                    fromdir='/tests/_async/',
                    todir='/tests/_sync/',
                    additional_replacements={
                        'AsyncAHK': 'AHK',
                        'AsyncTransport': 'Transport',
                        'AsyncWindow': 'Window',
                        'AsyncDaemonProcessTransport': 'DaemonProcessTransport',
                        '_AIOP': '_SIOP',
                        'async_create_process': 'sync_create_process',
                        'adrain_stdin': 'drain_stdin',
                        'IsolatedAsyncioTestCase': 'TestCase',
                        'asyncSetUp': 'setUp',
                        'asyncTearDown': 'tearDown',
                        'async_sleep': 'sleep',
                        # "__aenter__": "__aenter__",
                    },
                ),
            ]
        )
    },
    # package_dir={"": "src"},
)
