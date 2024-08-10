import pytest
from src.app import create_app
from src.models import *

headers = {'Content-Type':'application/json', 'Authorization':''}


@pytest.fixture()
def app():
    app = create_app()
    yield app


# Test a model level
@pytest.fixture(scope='module')
def new_category():
    cat = Category(description = "new category", user_id = 1)
    return cat

@pytest.fixture(scope='module')
def new_user():
    user = User(username = "admin",
                password = "123456",
                email = "admin@gmail.com",
                firstname = "ramses",
                lastname = "perez")
    return user

# Test model
def test_new_category(new_category):
    assert new_category.description == 'new category'
    assert new_category.user_id == 1

def test_new_user(new_user):
    assert new_user.username == "admin"
    assert new_user.password == "123456"
    assert new_user.email == "admin@gmail.com"
    assert new_user.firstname == "ramses"
    assert new_user.lastname == "perez"

# Test Router

def test_login(app):
    with app.test_client() as test_client:
        data:dict = {
            "username": "admin",
            "password": "123456"
        }
        response = test_client.post('/login', json=data, headers = {
                    'Content-type':'application/json', 
                    'Accept':'application/json'
                })
        
        assert response.status_code == 201
        
        rs_data = response.json["token"]
        assert rs_data != None
        
