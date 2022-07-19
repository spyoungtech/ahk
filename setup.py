import setuptools
import unasync

setuptools.setup(
    python_requires='>=3.7.0',
    name='ahk',
    version='0.0.1',
    author_email='spencer.young@spyoung.com',
    author='Spencer Young',
    description='A package used to test customized unasync',
    url='https://github.com/spyoungtech/ahk',
    packages=['ahk', 'ahk._async', 'ahk._sync'],
    install_requires=['typing_extensions; python_version < "3.10"'],
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
            ]
        )
    },
)
