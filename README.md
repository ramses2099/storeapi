# storeapi
Project Flask. SqlAlchemy CI/CD Heroku

1. Create virtual env
    - python -m venv env
1. Active virtual env
    - .\env\Scripts\activate
1. Update pip
    - python.exe -m pip install --upgrade pip
1. Create folder for source code
    - mkdir src
1. Add dependency flask sqlalchemy pytest
    - pip install Flask Flask-SQLAlchemy pytest PYJWT
1. Create folder for test
    - mkdir tests
1. Create file app.py
1. Run for testing
    - flask run
1. Create file test_app.py
    - add all pytest code for test router in app
    - file __init__.py to the tests folder
1. Setting path for pytest in this link
    - https://pytest-with-eric.com/introduction/pytest-pythonpath/
1. Create requirements file
    - pip freeze > requirements.txt
