from flask import Flask
from sqlalchemy import create_engine
from models import *

# create the app
app = Flask(__name__)

# configure the SQLite database, relative to the app instance folder
SQLALCHEMY_DATABASE_URI = "sqlite:///src//db//storedb.db"

# create engine
engine = create_engine(SQLALCHEMY_DATABASE_URI, echo=True)

# create all table
Base.metadata.create_all(engine)


@app.route("/")
def index():
    return "<p>Hello, World!</p>"


if __name__ == "__main__":
    app.run()