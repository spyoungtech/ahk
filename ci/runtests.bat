call venv\Scripts\activate.bat
coverage run -m behave tests\features --format=progress2 --junit
coverage run -a -m pytest tests\unittests --junitxml=reports\pytestresults.xml
call deactivate