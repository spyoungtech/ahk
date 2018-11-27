.\venv\Scripts\activate.ps1
coverage run -m behave .\tests\features
if ($LastExitCode -ne 0) { throw }
