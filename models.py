from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


db = SQLAlchemy()


# =========================
# USER MODEL
# =========================

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.String(20),
        default="user",
        nullable=False
    )

# =========================
# PRODUCT MODEL
# =========================

class Product(db.Model):
    __tablename__ = "product"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(150),
        nullable=False
    )

    description = db.Column(
        db.Text,
        nullable=True
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    stock = db.Column(
        db.Integer,
        nullable=False,
        default=0
    )

    category = db.Column(
        db.String(100),
        nullable=True
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================
# CART ITEM MODEL
# =========================

class CartItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(db.Integer, nullable=False, default=1)
   


# =========================
# ORDER MODEL
# =========================

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    total_amount = db.Column(db.Float, nullable=False)

    status = db.Column(
        db.String(30),
        default="Pending"
    )
    
    payment_status = db.Column(
        db.String(20),
        default="pending",
        nullable=False
)
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )


# =========================
# ORDER ITEM MODEL
# =========================

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        db.ForeignKey("product.id"),
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )
