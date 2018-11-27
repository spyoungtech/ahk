.venv\Scripts\activate.ps1
python setup.py sdist bdist_wheel
if ($LastExitCode -ne 0) { throw }