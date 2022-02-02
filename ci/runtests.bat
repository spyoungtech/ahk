call venv\Scripts\activate.bat
mkdir reports
coverage run -m pytest .\tests\unittests --junitxml=reports\pytestresults.xml
coverage report
call deactivate
