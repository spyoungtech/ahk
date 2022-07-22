import unasync

build_py = unasync.cmdclass_build_py(
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
                'a_send_nonblocking': 'send_nonblocking',
                'async_sleep': 'sleep',
                # "__aenter__": "__aenter__",
            },
        ),
    ]
)
