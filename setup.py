import setuptools
import unasync

setuptools.setup(
    name='ahk',
    version='0.0.1',
    author='Example Author',
    author_email='author@example.com',
    description='A package used to test customized unasync',
    url='https://github.com/pypa/sampleproject',
    packages=['ahk', 'ahk._async'],
    cmdclass={
        'build_py': unasync.cmdclass_build_py(
            rules=[
                unasync.Rule(
                    fromdir='/ahk/_async/',
                    todir='/ahk/_sync/',
                    additional_replacements={
                        'AsyncAHK': 'AHK',
                        'AsyncTransport': 'Transport',
                        'AsyncWindow': 'Window',
                        'AsyncDaemonProcessTransport': 'DaemonProcessTransport',
                        '_AIOP': '_SIOP',
                        'async_create_process': 'sync_create_process',
                        'adrain_stdin': 'drain_stdin',
                        # "__aenter__": "__aenter__",
                    },
                ),
                # unasync.Rule(
                #     fromdir="/ahip/tests/",
                #     todir="/hip/tests/",
                #     additional_replacements={"ahip": "hip"},
                # ),
            ]
        )
    },
    # package_dir={"": "src"},
)
