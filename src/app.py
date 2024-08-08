from flask import Flask
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
db = SQLAlchemy()

SQLALCHEMY_DATABSE_URI = "sqlite:///storedb.db"


@app.route("/")
def index():
    return "<p>Hello, World!</p>"





if __name__ == "__main__":
    app.run()