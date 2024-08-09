from sqlalchemy import Integer, Float, String, DateTime, Table, Column, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.orm import DeclarativeBase
from typing import List
from typing import Optional
from datetime import datetime

# class base for model
class Base(DeclarativeBase):
    pass

# vendors products Many to May
associate_table = Table(
    "Products_Vendors",
    Base.metadata,
    Column("product_id", ForeignKey("Products.id"), primary_key=True),
    Column("vendor_id", ForeignKey("Vendors.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "Users"
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    username: Mapped[str] = mapped_column(String(150), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(200), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False, unique=True)
    firstname: Mapped[str] = mapped_column(String(250), nullable=False)
    lastname: Mapped[str] = mapped_column(String(250), nullable=False)
    
    # relationship here
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    
    def __repr__(self) -> str:
        return f"User {self.id} {self.username!r} {self.firstname!r} {self.lastname!r}"
    

class Customer(Base):
    __tablename__ = "Customers"    
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    
    firstname: Mapped[str] = mapped_column(String(250), nullable=False)
    lastname: Mapped[str] = mapped_column(String(250), nullable=False)
    streetaddress: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False)
    state: Mapped[str] = mapped_column(String(150), nullable=False)
    zipcode: Mapped[str] = mapped_column(String(50), nullable=False)
    phonenumber: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    
    # relationship here
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    orders: Mapped[List["Order"]] = relationship(back_populates="customer") 
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Customer {self.id} {self.firstname!r} {self.lastname!r}"

    

class Order(Base):
    __tablename__ = "Orders"    
    
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    orderdate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    shipdate: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ordertotal: Mapped[float] = mapped_column(Float, nullable=False)
    
    # relationship here
    customer_id: Mapped[int] = mapped_column(Integer, ForeignKey("Customers.id"))
    employee_id: Mapped[int] = mapped_column(Integer, ForeignKey("Employees.id"))  
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id")) 
    
    # order and order details
    ordersdetails: Mapped[List["Order_Detail"]] = relationship(back_populates="order")
    employee: Mapped["Employee"] = relationship(back_populates="orders")
    customer: Mapped["Customer"] = relationship(back_populates="orders")  
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Order {self.id!r}"
    
    
class Order_Detail(Base):
    __tablename__ = "Order_Detatils"    
    
    id: Mapped[int] = mapped_column(primary_key=True)
    price: Mapped[float] = mapped_column(Float, nullable=False)
    quantity: Mapped[int] = mapped_column(Integer, nullable=False)
    
    # relationship here
    order_id: Mapped[int] = mapped_column(Integer, ForeignKey("Orders.id"))
    product_id: Mapped[int] = mapped_column(Integer, ForeignKey("Products.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    order: Mapped["Order"] = relationship(back_populates="ordersdetails")
    product: Mapped["Product"] = relationship(back_populates="ordersdetails")
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Order_Detail {self.id!r}"
    
    
  
class Product(Base):
    __tablename__ = "Products"    
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    priceperunit: Mapped[float] = mapped_column(Float, nullable=False)
    quantityonhand: Mapped[int] = mapped_column(Integer, nullable=False)
   
    # relationship here
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey("Categories.id"))
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    ordersdetails: Mapped[List["Order_Detail"]] = relationship(back_populates="product")
    
    vendors: Mapped[List["Vendor"]] = relationship(
        secondary=associate_table, back_populates="products"
    )
   
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Product {self.id} {self.name!r} {self.description!r}"
    
    

class Employee(Base):
    __tablename__ = "Employees"    
    
    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(String(250), nullable=False)
    lastname: Mapped[str] = mapped_column(String(250), nullable=False)
    streetaddress: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False)
    state: Mapped[str] = mapped_column(String(150), nullable=False)
    zipcode: Mapped[str] = mapped_column(String(50), nullable=False)
    phonenumber: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    dob: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    
    # relationship here
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    orders: Mapped[List["Order"]] = relationship(back_populates="employee")  
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Employee {self.id!r} {self.username!r} {self.firstname!r} {self.lastname!r}"
    
    
class Category(Base):
    __tablename__ = "Categories"    
    
    id: Mapped[int] = mapped_column(primary_key=True)
    description: Mapped[str] = mapped_column(String(250), nullable=False)
    
    # relationship here
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Category {self.id!r} {self.description!r}"
    
    @property
    def serialize(self):
        return {
            "id": self.id,
            "description": self.description,
            "user_id": self.user_id,
            "updated": self.updated,
            "created": self.created
        }
    
class Vendor(Base):
    __tablename__ = "Vendors"    
    
    id: Mapped[int] = mapped_column(primary_key=True)
    firstname: Mapped[str] = mapped_column(String(250), nullable=False)
    lastname: Mapped[str] = mapped_column(String(250), nullable=False)
    streetaddress: Mapped[str] = mapped_column(String(250), nullable=False)
    city: Mapped[str] = mapped_column(String(250), nullable=False)
    state: Mapped[str] = mapped_column(String(150), nullable=False)
    zipcode: Mapped[str] = mapped_column(String(50), nullable=False)
    phonenumber: Mapped[str] = mapped_column(String(50), nullable=False)
    email: Mapped[str] = mapped_column(String(250), nullable=False)
    
    # relationship here
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey("Users.id"))
    
    products: Mapped[List[Product]] = relationship(
        secondary=associate_table, back_populates="vendors"
    )
    
    updated:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=None)
    created:Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True, default=datetime.now())
    
    def __repr__(self) -> str:
        return f"Vendor {self.id!r} {self.firstname!r} {self.lastname!r}"
    
