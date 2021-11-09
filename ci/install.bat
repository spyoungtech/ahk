py -3.8 -m venv venv
call venv\Scripts\activate.bat
python -m pip install --upgrade pip
python -m pip install --upgrade -r .\ci\ci_requirements.txt
python -m pip install --upgrade .
python -m pip install ".[binary]"
call deactivate
