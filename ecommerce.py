from flask import Flask
from models import db
from routes import register_routes
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)

app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY")

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///ecommerce.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

register_routes(app)


@app.route("/")
def home():
    return {
        "message": "E-Commerce Backend is running!"
    }


if __name__ == "__main__":
    with app.app_context():
        db.create_all()

    app.run(debug=True)