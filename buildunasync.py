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
                'AsyncControl': 'Control',
                'AsyncDaemonProcessTransport': 'DaemonProcessTransport',
                '_AIOP': '_SIOP',
                'async_create_process': 'sync_create_process',
                'adrain_stdin': 'drain_stdin',
                'a_send_nonblocking': 'send_nonblocking',
                'async_sleep': 'sleep',
                'AsyncFutureResult': 'FutureResult',
                '_async_run_nonblocking': '_sync_run_nonblocking',
                'acommunicate': 'communicate',
                # "__aenter__": "__aenter__",
            },
        ),
    ]
)
