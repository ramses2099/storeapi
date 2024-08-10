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

def string_to_datetime(value):
    if type(value) is str:
        return datetime.strptime(value, '%Y-%m-%d')
    return value

# Category

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

@app.route("/categories/<id>", methods=["GET"])
@token_required
def getcategorybyid(user, id):
    with Session(engine) as session:
        statement = select(Category).filter_by(id = id)
        cat = session.execute(statement=statement).scalar_one_or_none()
        if cat == None:
            return make_response({"message": f"category with {id} not found"},
                                 404)
        
        return make_response({"data":cat.serialize},
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
     
@app.route("/categories/<id>", methods=["PUT"])
@token_required
def updatecategorie(user, id):
    try:
        with Session(engine) as session:
            statement = select(Category).filter_by(id = id)
            cat = session.execute(statement=statement).scalar_one()
            if cat == None:
                return make_response({"message":"enable to update category"},
                                 409)
            data = request.json
            description = data.get("description")
            if description:
                cat.description = description
                cat.updated = datetime.now()
                session.commit()
                return make_response({"message": cat.serialize},200)
            return make_response({"message":"decription property is required for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)
        
@app.route("/categories/<id>", methods=["DELETE"])
@token_required
def deletecategorie(user, id):
    try:
        with Session(engine) as session:
            statement = select(Category).filter_by(id = id)
            cat = session.execute(statement=statement).scalar_one()
            if cat == None:
                return make_response({"message": f"category with {id} not found"},
                                 404)
            session.delete(cat)
            session.commit()
            return make_response({"message": "category was delete"},202)
            
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)

# Customer

@app.route("/customers", methods=["GET"])
@token_required
def getcustomers(user):
    with Session(engine) as session:
        stmt = select(Customer)
        customers = session.execute(statement=stmt).all()
        if not customers:
            return make_response({"message":"not record in customers table"},
                401
            )
        return make_response({"data":[cust[0].serialize for cust in customers]},
                200
            )

@app.route("/customers/<id>", methods=["GET"])
@token_required
def getcustomerbyid(user, id):
    with Session(engine) as session:
        statement = select(Customer).filter_by(id = id)
        cust = session.execute(statement=statement).scalar_one_or_none()
        if cust == None:
            return make_response({"message": f"customer with {id} not found"},
                                 404)
        
        return make_response({"data":cust.serialize},
                200
            )

@app.route("/customers", methods=["POST"])
@token_required
def createcustomers(user):
    data = request.json
    user_id = user.id    
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    streetaddress = data.get("streetaddress")
    city = data.get("city")
    state = data.get("state")
    zipcode = data.get("zipcode")
    phonenumber = data.get("phonenumber")
    email = data.get("email")
        
    if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email:
        cust = Customer(firstname=firstname, lastname=lastname, streetaddress=streetaddress, city=city,
                        state=state, zipcode=zipcode, phonenumber=phonenumber, email=email, user_id=user_id)
        with Session(engine) as session:
            session.add(cust)
            session.commit()
            return make_response(
                    {"message":"Customer Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Customer"},
                    500
                )   
     
@app.route("/customers/<id>", methods=["PUT"])
@token_required
def updatecustomers(user, id):
    try:
        with Session(engine) as session:
            statement = select(Customer).filter_by(id = id)
            cust = session.execute(statement=statement).scalar_one()
            if cust == None:
                return make_response({"message":"enable to update customer"},
                                 409)
            data = request.json
            firstname = data.get("firstname")
            lastname = data.get("lastname")
            streetaddress = data.get("streetaddress")
            city = data.get("city")
            state = data.get("state")
            zipcode = data.get("zipcode")
            phonenumber = data.get("phonenumber")
            email = data.get("email")
                      
            
            if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email:   
                cust.firstname = firstname
                cust.lastname = lastname
                cust.streetaddress = streetaddress
                cust.city = city
                cust.state = state
                cust.zipcode = zipcode
                cust.phonenumber = phonenumber
                cust.email = email                
                cust.updated = datetime.now()
                session.commit()
                return make_response({"message": cust.serialize},200)
            
            return make_response({"message":"property is missing for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)
        
@app.route("/customers/<id>", methods=["DELETE"])
@token_required
def deletecustomers(user, id):
    try:
        with Session(engine) as session:
            statement = select(Customer).filter_by(id = id)
            cust = session.execute(statement=statement).scalar_one()
            if cust == None:
                return make_response({"message": f"customer with {id} not found"},
                                 404)
            session.delete(cust)
            session.commit()
            return make_response({"message": "customer was delete"},202)
            
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)

# Order

@app.route("/orders", methods=["GET"])
@token_required
def getorders(user):
    with Session(engine) as session:
        stmt = select(Order)
        orders = session.execute(statement=stmt).all()
        if not orders:
            return make_response({"message":"not record in orders table"},
                401
            )
        return make_response({"data":[ords[0].serialize for ords in orders]},
                200
            )

@app.route("/orders/<id>", methods=["GET"])
@token_required
def getordersbyid(user, id):
    with Session(engine) as session:
        statement = select(Order).filter_by(id = id)
        order = session.execute(statement=statement).scalar_one_or_none()
        if order == None:
            return make_response({"message": f"order with {id} not found"},
                                 404)
               
        order_rs = {
            "order_header": order.serialize,
            "order_deatils":[det.serialize for det in order.ordersdetails]
        }
        
        return make_response({"data": order_rs},
                200
            )

@app.route("/orders", methods=["POST"])
@token_required
def createorders(user):
    data = request.json
    user_id = user.id    
    orderdate = string_to_datetime(data.get("orderdate"))
    shipdate = string_to_datetime(data.get("shipdate"))
    ordertotal = data.get("ordertotal")
    customer_id = data.get("customer_id")
    employee_id = data.get("employee_id")
      
    if orderdate and shipdate and ordertotal and customer_id and employee_id:
        oder = Order(orderdate=orderdate, shipdate=shipdate, ordertotal=ordertotal, customer_id=customer_id,
                        employee_id=employee_id, user_id=user_id)
        with Session(engine) as session:
            session.add(oder)
            session.commit()
            return make_response(
                    {"message":"Order Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Order"},
                    500
                )   
     
@app.route("/orders/<id>", methods=["PUT"])
@token_required
def updateorders(user, id):
    try:
        with Session(engine) as session:
            statement = select(Order).filter_by(id = id)
            order = session.execute(statement=statement).scalar_one_or_none()
            if order == None:
                return make_response({"message": f"order with {id} not found"},
                                 404)
            data = request.json
            user_id = user.id                                          
            shipdate = data.get("shipdate")
            ordertotal = data.get("ordertotal")
            customer_id = data.get("customer_id")
            employee_id = data.get("employee_id")  
            
            if ordertotal and shipdate and customer_id and employee_id and user_id:   
                order.shipdate = shipdate
                order.ordertotal = ordertotal
                order.customer_id = customer_id
                order.employee_id = employee_id
                order.user_id = user_id
                order.updated = datetime.now()
                session.commit()
                return make_response({"message": order.serialize},200)
            
            return make_response({"message":"property is missing for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)

# Order_Detail

@app.route("/orderdetatils", methods=["POST"])
@token_required
def createorderdetatils(user):
    data = request.json
    user_id = user.id
    price = data.get("price")
    quantity = data.get("quantity")
    order_id = data.get("order_id")
    product_id = data.get("product_id")
    
    
    if price and quantity and order_id and product_id and user_id:
        details = Order_Detail(price=price, quantity= quantity, order_id=order_id, product_id=product_id, user_id=user_id)
        with Session(engine) as session:
            session.add(details)
            session.commit()
            return make_response(
                    {"message":"Order Detail Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Order Details"},
                    500
                )   

# Products
        
@app.route("/products", methods=["GET"])
@token_required
def getproducts(user):
    with Session(engine) as session:
        stmt = select(Product)
        products = session.execute(statement=stmt).all()
        if not products:
            return make_response({"message":"not record in products table"},
                401
            )
        return make_response({"data":[prod[0].serialize for prod in products]},
                200
            )

@app.route("/products/<id>", methods=["GET"])
@token_required
def getproductsbyid(user, id):
    with Session(engine) as session:
        statement = select(Product).filter_by(id = id)
        product = session.execute(statement=statement).scalar_one_or_none()
        if product == None:
            return make_response({"message": f"product with {id} not found"},
                                 404)
        
        return make_response({"data": product.serialize},
                200
            )

@app.route("/products", methods=["POST"])
@token_required
def createproducts(user):
    data = request.json
    user_id = user.id   
    name = data.get("name")
    description = data.get("description")
    priceperunit = data.get("priceperunit")
    quantityonhand = data.get("quantityonhand")
    category_id = data.get("category_id") 
       
    if name and description and priceperunit and quantityonhand and category_id and user_id:
        product = Product(name=name, description=description, priceperunit=priceperunit, quantityonhand=quantityonhand,
                          category_id=category_id, user_id=user_id)
        with Session(engine) as session:
            session.add(product)
            session.commit()
            return make_response(
                    {"message":"Product Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Category"},
                    500
                )   
     
@app.route("/products/<id>", methods=["PUT"])
@token_required
def updateproducts(user, id):
    try:
        with Session(engine) as session:
            statement = select(Product).filter_by(id = id)
            product = session.execute(statement=statement).scalar_one()
            if product == None:
                return make_response({"message":"enable to update product"},
                                 409)
            data = request.json
            user_id = user_id
            name = data.get("name")
            description = data.get("description")
            priceperunit = data.get("priceperunit")
            quantityonhand = data.get("quantityonhand")
            category_id = data.get("category_id")
            
            if name and description and priceperunit and quantityonhand and category_id and user_id:               
                product.name = name
                product.description = description
                product.priceperunit = priceperunit
                product.quantityonhand = quantityonhand
                product.category_id = category_id
                product.updated = datetime.now()
                session.commit()
                return make_response({"message": product.serialize},200)
            return make_response({"message":"some property is missing for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)

# Employee

@app.route("/employees", methods=["GET"])
@token_required
def getemployees(user):
    with Session(engine) as session:
        stmt = select(Employee)
        employees = session.execute(statement=stmt).all()
        if not employees:
            return make_response({"message":"not record in employees table"},
                401
            )
        return make_response({"data":[emp[0].serialize for emp in employees]},
                200
            )

@app.route("/employees/<id>", methods=["GET"])
@token_required
def getemployeebyid(user, id):
    with Session(engine) as session:
        statement = select(Employee).filter_by(id = id)
        emp = session.execute(statement=statement).scalar_one_or_none()
        if emp == None:
            return make_response({"message": f"employee with {id} not found"},
                                 404)
        
        return make_response({"data":emp.serialize},
                200
            )

@app.route("/employees", methods=["POST"])
@token_required
def createemployees(user):
    data = request.json
    user_id = user.id    
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    streetaddress = data.get("streetaddress")
    city = data.get("city")
    state = data.get("state")
    zipcode = data.get("zipcode")
    phonenumber = data.get("phonenumber")
    email = data.get("email")
    dob = data.get("dob")
        
    if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email:
        emp = Employee(firstname=firstname, lastname=lastname, streetaddress=streetaddress, city=city,
                        state=state, zipcode=zipcode, phonenumber=phonenumber, email=email, dob=dob, user_id=user_id)
        with Session(engine) as session:
            session.add(emp)
            session.commit()
            return make_response(
                    {"message":"Employee Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Employee"},
                    500
                )   
     
@app.route("/employees/<id>", methods=["PUT"])
@token_required
def updateemployees(user, id):
    try:
        with Session(engine) as session:
            statement = select(Employee).filter_by(id = id)
            emp = session.execute(statement=statement).scalar_one_or_none()
            if emp == None:
                return make_response({"message": f"employee with {id} not found"},
                                 404)
            data = request.json
            user_id = user.id
            firstname = data.get("firstname")
            lastname = data.get("lastname")
            streetaddress = data.get("streetaddress")
            city = data.get("city")
            state = data.get("state")
            zipcode = data.get("zipcode")
            phonenumber = data.get("phonenumber")
            email = data.get("email")
            dob = data.get("dob")
                      
            
            if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email and dob and user_id:   
                emp.firstname = firstname
                emp.lastname = lastname
                emp.streetaddress = streetaddress
                emp.city = city
                emp.state = state
                emp.zipcode = zipcode
                emp.phonenumber = phonenumber
                emp.email = email
                emp.user_id = user_id                
                emp.updated = datetime.now()
                session.commit()
                return make_response({"message": emp.serialize},200)
            
            return make_response({"message":"property is missing for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)
   

# Vendor

@app.route("/vendors", methods=["GET"])
@token_required
def getvendors(user):
    with Session(engine) as session:
        stmt = select(Vendor)
        vendors = session.execute(statement=stmt).all()
        if not vendors:
            return make_response({"message":"not record in vendors table"},
                401
            )
        return make_response({"data":[vend[0].serialize for vend in vendors]},
                200
            )

@app.route("/vendors/<id>", methods=["GET"])
@token_required
def getvendorbyid(user, id):
    with Session(engine) as session:
        statement = select(Vendor).filter_by(id = id)
        vend = session.execute(statement=statement).scalar_one_or_none()
        if vend == None:
            return make_response({"message": f"vendor with {id} not found"},
                                 404)
        
        return make_response({"data":vend.serialize},
                200
            )

@app.route("/vendors", methods=["POST"])
@token_required
def createvendors(user):
    data = request.json
    user_id = user.id    
    firstname = data.get("firstname")
    lastname = data.get("lastname")
    streetaddress = data.get("streetaddress")
    city = data.get("city")
    state = data.get("state")
    zipcode = data.get("zipcode")
    phonenumber = data.get("phonenumber")
    email = data.get("email")
    
        
    if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email:
        vend = Vendor(firstname=firstname, lastname=lastname, streetaddress=streetaddress, city=city,
                        state=state, zipcode=zipcode, phonenumber=phonenumber, email=email, user_id=user_id)
        with Session(engine) as session:
            session.add(vend)
            session.commit()
            return make_response(
                    {"message":"Vendor Created"},
                    201
                )
    return make_response(
                    {"message":"Unable to create Vendor"},
                    500
                )   
     
@app.route("/vendors/<id>", methods=["PUT"])
@token_required
def updatevendors(user, id):
    try:
        with Session(engine) as session:
            statement = select(Vendor).filter_by(id = id)
            vend = session.execute(statement=statement).scalar_one_or_none()
            if vend == None:
                return make_response({"message": f"vendor with {id} not found"},
                                 404)
            data = request.json
            user_id = user.id
            firstname = data.get("firstname")
            lastname = data.get("lastname")
            streetaddress = data.get("streetaddress")
            city = data.get("city")
            state = data.get("state")
            zipcode = data.get("zipcode")
            phonenumber = data.get("phonenumber")
            email = data.get("email")
                               
            
            if firstname and lastname and streetaddress and city and state and zipcode and phonenumber and email and user_id:   
                vend.firstname = firstname
                vend.lastname = lastname
                vend.streetaddress = streetaddress
                vend.city = city
                vend.state = state
                vend.zipcode = zipcode
                vend.phonenumber = phonenumber
                vend.email = email
                vend.user_id = user_id                
                vend.updated = datetime.now()
                session.commit()
                return make_response({"message": vend.serialize},200)
            
            return make_response({"message":"property is missing for update"},
                                 401)
        
    except Exception as e:
        print(e)
        return make_response({"message":"unable to process"},
                                 409)
   

if __name__ == "__main__":
    app.run()