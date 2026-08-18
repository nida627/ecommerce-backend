from ecommerce import app
from models import db, User
from flask_bcrypt import Bcrypt

bcrypt = Bcrypt()

with app.app_context():

    name = input("Enter admin name: ")
    email = input("Enter admin email: ")
    password = input("Enter admin password: ")

    existing_admin = User.query.filter_by(email=email).first()

    if existing_admin:
        print("User with this email already exists.")
    else:
        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        admin = User(
            name=name,
            email=email,
            password=hashed_password,
            role="admin"
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created successfully!")