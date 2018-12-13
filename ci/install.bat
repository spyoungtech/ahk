py -3.7 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install --upgrade -r .\ci\ci_requirements.txt
call deactivate