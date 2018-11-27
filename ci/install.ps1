py -3.7 -m venv venv
.\venv\Scripts\activate.ps1
python -m pip install -r .\ci\ci_requirements.txt
if ($LastExitCode -ne 0) { throw }