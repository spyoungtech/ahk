.\venv\Scripts\activate.ps1
coverage run -m behave .\tests\features
if ($LastExitCode -ne 0) {
    $shouldExit = 1
} else {
    $shouldExit = 0
}
coverage run -a -m pytest .\tests\unittests
if ($LastExitCode -ne 0) { throw }
if ($shouldExit -ne 0) { throw }
coveralls