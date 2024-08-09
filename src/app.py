from flask import Flask, request, make_response
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session
from werkzeug.security import generate_password_hash, check_password_hash
import jwt
from datetime import datetime, timedelta
from functools import wraps
from models import *

# create the app
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
SQLALCHEMY_DATABASE_URI = "sqlite:///src//db//storedb.db"

SECRET_KEY = "6Oxlw2MG27cx7mudewQTrkUM9CNqNgHp"
ALGORITHM = "HS256"

# create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

# create all table
Base.metadata.create_all(engine)

# routes
@app.route("/signup", methods=["POST"])
def signup():
    data = request.json
    username = data.get("username")
    password = data.get("password")
    email = data.get("email")
    firstname = data.get("firstname")
    lastname= data.get("lastname")
    
    if username and password and email and firstname and lastname:
        with Session(engine) as session:
            stmt = select(User).where(User.email == email)
            user = session.execute(statement=stmt).scalar_one_or_none()
            if user:
                return make_response(
                    {"message":"Please Sign In"},
                    200
                )
            create_user = User(
                username = username,
                password = generate_password_hash(password),
                email = email,
                firstname = firstname,
                lastname = lastname
            )
            session.add(create_user)
            session.commit()
            return make_response(
                    {"message":"User Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create User"},
                    500
                )        

@app.route("/login", methods=["POST"])
def login():
    auth = request.json
    username = auth.get("username")
    password = auth.get("password")
    
    if not auth or not username or not password:
        return make_response({"message":"Proper Credentials were not proviced"},
            401
        )
    
    with Session(engine) as session:
        stmt = select(User).where(User.username == username)
        user = session.execute(statement=stmt).scalar_one()
        if not user:
            return make_response({"message":"Please create an account"},
                401
            )
        if check_password_hash(user.password, password):
            token = jwt.encode({
                    'id':user.id,
                    'exp': datetime.now() + timedelta(minutes=60),                    
                },
                SECRET_KEY,
                ALGORITHM
                )
            return make_response({'token': token}
                                     ,201)
        return make_response({"message":"Please check your credentials"},401)

def token_required(f):    
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']            
        if not token:
            return make_response({"message":"Token is missing"},
                                 401)
        try:
            print(token)
            data = jwt.decode(token, key=SECRET_KEY, algorithms=ALGORITHM, verify=True, options={'verify_exp':False})
            print(data)
            current_user = data["id"]
            with Session(engine) as session:
                stmt = select(User).where(User.id == current_user)
                user = session.execute(statement=stmt).scalar_one()
                return f(user, *args, **kwargs)           
            
        except Exception as e:
            print(e)
            return make_response({"message":"Token is invalid"},
                                 401)

    return decorated

@app.route("/categories", methods=["GET"])
@token_required
def getcategories(user):
    with Session(engine) as session:
        stmt = select(Category)
        categories = session.execute(statement=stmt).all()
        if not categories:
            return make_response({"message":"not record in category table"},
                401
            )
        return make_response({"data":[cat[0].serialize for cat in categories]},
                200
            )

@app.route("/categories", methods=["POST"])
@token_required
def createcategorie(user):
    data = request.json
    user_id = user.id
    description= data.get("description")
    if description and user_id:
        cat = Category(description=description, user_id=user_id)
        with Session(engine) as session:
            session.add(cat)
            session.commit()
            return make_response(
                    {"message":"Category Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Category"},
                    500
                )   
     


if __name__ == "__main__":
    app.run()