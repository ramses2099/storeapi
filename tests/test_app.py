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



# Test model
def test_new_category(new_category):
    assert new_category.description == 'new category'
    assert new_category.user_id == 1


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
        
