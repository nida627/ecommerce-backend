from flask import app, request, jsonify
from models import db, User, Product, CartItem, Order, OrderItem
from flask_bcrypt import Bcrypt
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    jwt_required,
    get_jwt_identity
)
from functools import wraps



bcrypt = Bcrypt()
jwt = JWTManager()


# =========================================================
# ADMIN REQUIRED DECORATOR
# =========================================================

def admin_required():

    def decorator(func):

        @wraps(func)
        @jwt_required()
        def wrapper(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(int(user_id))

            if not user:
                return jsonify({
                    "error": "User not found"
                }), 404

            if user.role != "admin":
                return jsonify({
                    "error": "Admin access required"
                }), 403

            return func(*args, **kwargs)

        return wrapper

    return decorator


# =========================================================
# REGISTER ROUTES
# =========================================================

def register_routes(app):

    jwt.init_app(app)

    # =====================================================
    # REGISTER
    # =====================================================

    @app.route("/api/register", methods=["POST"])
    def register():

        data = request.get_json()

        name = data.get("name")
        email = data.get("email")
        password = data.get("password")

        if not name or not email or not password:
            return jsonify({
                "error": "Name, email and password are required"
            }), 400

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            return jsonify({
                "error": "Email already registered"
            }), 409

        hashed_password = bcrypt.generate_password_hash(
            password
        ).decode("utf-8")

        user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.session.add(user)
        db.session.commit()

        return jsonify({
            "message": "User registered successfully",
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 201


    # =====================================================
    # LOGIN
    # =====================================================

    @app.route("/api/login", methods=["POST"])
    def login():

        data = request.get_json()

        email = data.get("email")
        password = data.get("password")

        if not email or not password:
            return jsonify({
                "error": "Email and password are required"
            }), 400

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        password_correct = bcrypt.check_password_hash(
            user.password,
            password
        )

        if not password_correct:
            return jsonify({
                "error": "Invalid email or password"
            }), 401

        access_token = create_access_token(
            identity=str(user.id)
        )

        return jsonify({
            "message": "Login successful",
            "access_token": access_token,
            "user": {
                "id": user.id,
                "name": user.name,
                "email": user.email,
                "role": user.role
            }
        }), 200


    # =====================================================
    # GET PROFILE
    # =====================================================

    @app.route("/api/profile", methods=["GET"])
    @jwt_required()
    def profile():

        user_id = get_jwt_identity()

        user = User.query.get(int(user_id))

        if not user:
            return jsonify({
                "error": "User not found"
            }), 404

        return jsonify({
            "id": user.id,
            "name": user.name,
            "email": user.email,
            "role": user.role
        }), 200


    # =====================================================
    # CREATE PRODUCT ADMIN ONLY
    # =====================================================

    @app.route("/api/products", methods=["POST"])
    @admin_required()
    def create_product():

        data = request.get_json()

        if not data:
            return jsonify({
                "error": "Request body cannot be empty"
            }), 400

        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        stock = data.get("stock")
        category = data.get("category")


        # =========================
        # NAME VALIDATION
        # =========================

        if not name or not name.strip():
            return jsonify({
                "error": "Product name is required"
            }), 400
            
        if not description or not description.strip():
            return jsonify({
                "error": "Description is required"
            }), 400

        if not category or not category.strip():
            return jsonify({
                "error": "Category is required"
            }), 400


        # =========================
        # PRICE VALIDATION
        # =========================

        if price is None:
            return jsonify({
                "error": "Price is required"
            }), 400

        if type(price) not in (int, float):
            return jsonify({
                "error": "Price must be a number"
            }), 400

        if price <= 0:
            return jsonify({
                "error": "Price must be greater than 0"
            }), 400


        # =========================
        # STOCK VALIDATION
        # =========================

        if stock is None:
            return jsonify({
                "error": "Stock is required"
            }), 400

        if type(stock) is not int:
            return jsonify({
                "error": "Stock must be an integer"
            }), 400

        if stock < 0:
            return jsonify({
                "error": "Stock cannot be negative"
            }), 400

        product = Product(
            name=name,
            description=description,
            price=price,
            stock=stock,
            category=category
        )

        db.session.add(product)
        db.session.commit()

        return jsonify({
            "message": "Product created successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock,
                "category":product.category
            }
        }), 201


    # =====================================================
    # GET ALL PRODUCTS
    # =====================================================

    @app.route("/api/products", methods=["GET"])
    @jwt_required()
    def get_products():

        products = Product.query.all()

        return jsonify({
            "products": [
                {
                    "id": product.id,
                    "name": product.name,
                    "description": product.description,
                    "price": product.price,
                    "stock": product.stock
                }
                for product in products
            ]
        }), 200


    # =====================================================
    # GET SINGLE PRODUCT
    # =====================================================

    @app.route("/api/products/<int:product_id>", methods=["GET"])
    @jwt_required()
    def get_product(product_id):

        product = Product.query.get(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        return jsonify({
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock
            }
        }), 200


    # =====================================================
    # UPDATE PRODUCT
    # ADMIN ONLY
    # =====================================================

    @app.route("/api/products/<int:product_id>", methods=["PUT"])
    @admin_required()
    def update_product(product_id):

        product = Product.query.get(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        data = request.get_json()

        name = data.get("name")
        description = data.get("description")
        price = data.get("price")
        stock = data.get("stock")

        if name is not None:
            product.name = name

        if description is not None:
            product.description = description

        if price is not None:
            product.price = price

        if stock is not None:
            product.stock = stock

        db.session.commit()

        return jsonify({
            "message": "Product updated successfully",
            "product": {
                "id": product.id,
                "name": product.name,
                "description": product.description,
                "price": product.price,
                "stock": product.stock
            }
        }), 200


    # =====================================================
    # DELETE PRODUCT
    # ADMIN ONLY
    # =====================================================

    @app.route("/api/products/<int:product_id>", methods=["DELETE"])
    @admin_required()
    def delete_product(product_id):

        product = Product.query.get(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        db.session.delete(product)
        db.session.commit()

        return jsonify({
            "message": "Product deleted successfully"
        }), 200


    # =====================================================
    # ADD TO CART
    # =====================================================

    @app.route("/api/cart", methods=["POST"])
    @jwt_required()
    def add_to_cart():

        user_id = get_jwt_identity()

        data = request.get_json()

        product_id = data.get("product_id")
        quantity = data.get("quantity", 1)

        if not product_id:
            return jsonify({
                "error": "Product ID is required"
            }), 400

        if quantity <= 0:
            return jsonify({
                "error": "Quantity must be greater than 0"
            }), 400

        product = Product.query.get(product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        if product.stock < quantity:
            return jsonify({
                "error": "Not enough stock available"
            }), 400

        existing_item = CartItem.query.filter_by(
            user_id=int(user_id),
            product_id=product.id
        ).first()

        if existing_item:

            new_quantity = (
                existing_item.quantity + quantity
            )

            if product.stock < new_quantity:
                return jsonify({
                    "error": "Not enough stock available"
                }), 400

            existing_item.quantity = new_quantity

        else:

            cart_item = CartItem(
                user_id=int(user_id),
                product_id=product.id,
                quantity=quantity
            )

            db.session.add(cart_item)

        db.session.commit()

        return jsonify({
            "message": "Product added to cart successfully"
        }), 201
        
    # =========================
    # GET MY CART
    # =========================

    @app.route("/api/cart", methods=["GET"])
    @jwt_required()
    def get_cart():

        user_id = get_jwt_identity()

        cart_items = CartItem.query.filter_by(
            user_id=int(user_id)
        ).all()

        cart = []
        total = 0

        for item in cart_items:

            product = Product.query.get(item.product_id)

            if not product:
                continue

            item_total = product.price * item.quantity
            total += item_total

            cart.append({
                "cart_item_id": item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": item.quantity,
                "item_total": item_total
            })

        return jsonify({
            "cart": cart,
            "total": total
        }), 200    
        
    # =========================
    # UPDATE CART QUANTITY
    # =========================

    @app.route("/api/cart/<int:cart_item_id>", methods=["PUT"])
    @jwt_required()
    def update_cart(cart_item_id):

        user_id = int(get_jwt_identity())

        # Find cart item by its own ID
        cart_item = CartItem.query.get(cart_item_id)

        if not cart_item:
            return jsonify({
                "error": "Cart item not found"
            }), 404

        # Make sure this cart item belongs to logged-in user
        if cart_item.user_id != user_id:
            return jsonify({
                "error": "You cannot modify this cart item"
            }), 403

        data = request.get_json()

        quantity = data.get("quantity")

        if quantity is None:
            return jsonify({
                "error": "Quantity is required"
            }), 400

        if quantity <= 0:
            return jsonify({
                "error": "Quantity must be greater than 0"
            }), 400

        product = Product.query.get(cart_item.product_id)

        if not product:
            return jsonify({
                "error": "Product not found"
            }), 404

        if quantity > product.stock:
            return jsonify({
                "error": "Not enough stock available"
            }), 400

        cart_item.quantity = quantity

        db.session.commit()

        return jsonify({
            "message": "Cart quantity updated successfully",
            "cart_item": {
                "cart_item_id": cart_item.id,
                "product_id": product.id,
                "name": product.name,
                "price": product.price,
                "quantity": cart_item.quantity,
                "item_total": product.price * cart_item.quantity
            }
        }), 200   
        
    # =========================
    # REMOVE FROM CART
    # =========================

    @app.route("/api/cart/<int:cart_item_id>", methods=["DELETE"])
    @jwt_required()
    def remove_from_cart(cart_item_id):

        user_id = int(get_jwt_identity())

        cart_item = CartItem.query.get(cart_item_id)

        if not cart_item:
            return jsonify({
                "error": "Cart item not found"
            }), 404

        if cart_item.user_id != user_id:
            return jsonify({
                "error": "You cannot remove this cart item"
            }), 403

        db.session.delete(cart_item)
        db.session.commit()

        return jsonify({
            "message": "Product removed from cart successfully"
        }), 200
        
    # =========================
    # PLACE ORDER
    # =========================

    @app.route("/api/orders", methods=["POST"])
    @jwt_required()
    def place_order():

        user_id = int(get_jwt_identity())

        cart_items = CartItem.query.filter_by(
            user_id=user_id
        ).all()

        if not cart_items:
            return jsonify({
                "error": "Cart is empty"
            }), 400

        total_amount = 0
        order_items_data = []

        # Check stock and calculate current prices
        for item in cart_items:

            product = Product.query.get(item.product_id)

            if not product:
                return jsonify({
                    "error": f"Product with ID {item.product_id} not found"
                }), 404

            if product.stock < item.quantity:
                return jsonify({
                    "error": f"Not enough stock for {product.name}"
                }), 400

            item_total = product.price * item.quantity

            total_amount += item_total

            order_items_data.append({
                "product": product,
                "quantity": item.quantity,
                "price": product.price
            })

        # Create order
        order = Order(
            user_id=user_id,
            total_amount=total_amount,
            status="pending",
            payment_status="pending"
        )
        db.session.add(order)
        db.session.flush()

        # Create order items
        for item_data in order_items_data:

            product = item_data["product"]

            order_item = OrderItem(
                order_id=order.id,
                product_id=product.id,
                quantity=item_data["quantity"],
                price=item_data["price"]
            )

            db.session.add(order_item)

            # Reduce stock
            product.stock -= item_data["quantity"]

        # Clear cart
        for item in cart_items:
            db.session.delete(item)

        db.session.commit()

        return jsonify({
            "message": "Order placed successfully",
            "order": {
                "id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
                "payment_status": order.payment_status
            }
        }), 201
        
    # =========================
    # GET MY ORDERS
    # =========================

    @app.route("/api/orders", methods=["GET"])
    @jwt_required()
    def get_my_orders():

        user_id = int(get_jwt_identity())

        orders = Order.query.filter_by(
            user_id=user_id
        ).order_by(Order.id.desc()).all()

        result = []

        for order in orders:

            order_items = OrderItem.query.filter_by(
                order_id=order.id
            ).all()

            items = []

            for item in order_items:

                product = Product.query.get(item.product_id)

                items.append({
                    "product_id": item.product_id,
                    "name": product.name if product else "Product unavailable",
                    "quantity": item.quantity,
                    "price": item.price,
                    "item_total": item.price * item.quantity
                })

            result.append ({
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
                "items": items,
                "payment_status": order.payment_status
            })

        return jsonify({
            "orders": result
        }), 200
        
    # =========================
    # GET SINGLE ORDER
    # =========================

    @app.route("/api/orders/<int:order_id>", methods=["GET"])
    @jwt_required()
    def get_single_order(order_id):

        user_id = int(get_jwt_identity())

        order = Order.query.filter_by(
            id=order_id,
            user_id=user_id
        ).first()

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        order_items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        items = []

        for item in order_items:

            product = Product.query.get(item.product_id)

            items.append({
                "product_id": item.product_id,
                "name": product.name if product else "Product unavailable",
                "quantity": item.quantity,
                "price": item.price,
                "item_total": item.price * item.quantity
            })

        return jsonify({
            "order": {
                "order_id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
                "items": items
            }
        }), 200
        
    # =========================
    # ADMIN - GET ALL ORDERS
    # =========================

    @app.route("/api/admin/orders", methods=["GET"])
    @admin_required()
    def admin_get_orders():

        orders = Order.query.order_by(
            Order.id.desc()
        ).all()

        result = []

        for order in orders:

            user = User.query.get(order.user_id)

            order_items = OrderItem.query.filter_by(
                order_id=order.id
            ).all()

            items = []

            for item in order_items:

                product = Product.query.get(item.product_id)

                items.append({
                    "product_id": item.product_id,
                    "name": product.name if product else "Product unavailable",
                    "quantity": item.quantity,
                    "price": item.price,
                    "item_total": item.price * item.quantity
                })

            result.append({
                "order_id": order.id,
                "user": {
                    "id": user.id,
                    "name": user.name,
                    "email": user.email
                } if user else None,
                "total_amount": order.total_amount,
                "status": order.status,
                "items": items
            })

        return jsonify({
            "orders": result
        }), 200
        
    # =========================
    # ADMIN - UPDATE ORDER STATUS
    # =========================

    @app.route("/api/admin/orders/<int:order_id>", methods=["PUT"])
    @admin_required()
    def admin_update_order_status(order_id):

        order = Order.query.get(order_id)

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        data = request.get_json()

        status = data.get("status")

        if not status:
            return jsonify({
                "error": "Status is required"
            }), 400

        # Current status
        current_status = order.status

        # Allowed status transitions
        allowed_transitions = {
        "pending": ["confirmed", "cancelled"],
        "confirmed": ["processing", "cancelled"],
        "processing": ["shipped"],
        "shipped": ["delivered"],
        "delivered": [],
        "cancelled": []
    }

        current_status = order.status.lower()
        new_status = data.get("status", "").lower()

        if new_status not in allowed_transitions.get(current_status, []):
            return jsonify({
                "error": f"Cannot change order status from {current_status} to {new_status}"
            }), 400
            
        order.status = new_status

        db.session.commit()

        return jsonify({
            "message": "Order status updated successfully",
            "order": {
                "id": order.id,
                "status": order.status
            }
        }), 200
        
    # =========================
    # CANCEL ORDER
    # =========================

    @app.route("/api/orders/<int:order_id>/cancel", methods=["PUT"])
    @jwt_required()
    def cancel_order(order_id):

        user_id = int(get_jwt_identity())

        # Make sure this order belongs to the logged-in user
        order = Order.query.filter_by(
            id=order_id,
            user_id=user_id
        ).first()

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        # Only pending/confirmed orders can be cancelled
        if order.status not in ["pending", "confirmed"]:
            return jsonify({
                "error": f"Order cannot be cancelled because its status is '{order.status}'"
            }), 400

        # Get order items
        order_items = OrderItem.query.filter_by(
            order_id=order.id
        ).all()

        # Restore stock
        for item in order_items:

            product = Product.query.get(item.product_id)

            if product:
                product.stock += item.quantity

        # Update order status
        order.status = "cancelled"

        db.session.commit()

        return jsonify({
            "message": "Order cancelled successfully",
            "order": {
                "id": order.id,
                "status": order.status
            }
        }), 200
        
    # =========================
    # MAKE PAYMENT
    # =========================

    @app.route("/api/orders/<int:order_id>/payment", methods=["POST"])
    @jwt_required()
    def make_payment(order_id):

        user_id = int(get_jwt_identity())

        order = Order.query.filter_by(
            id=order_id,
            user_id=user_id
        ).first()

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        if order.status == "cancelled":
            return jsonify({
                "error": "Cancelled order cannot be paid"
            }), 400

        if order.status == "delivered":
            return jsonify({
                "error": "Delivered order cannot be paid"
            }), 400

        if order.payment_status == "paid":
            return jsonify({
                "error": "Order is already paid"
            }), 400

        # Temporary payment simulation
        order.payment_status = "paid"

        db.session.commit()

        return jsonify({
            "message": "Payment successful",
            "order": {
                "id": order.id,
                "total_amount": order.total_amount,
                "payment_status": order.payment_status,
                "status": order.status
            }
        }), 200
        
    # =========================
    # ADMIN - REFUND ORDER
    # =========================

    @app.route("/api/admin/orders/<int:order_id>/refund", methods=["POST"])
    @admin_required()
    def admin_refund_order(order_id):

        order = Order.query.get(order_id)

        if not order:
            return jsonify({
                "error": "Order not found"
            }), 404

        if order.status != "cancelled":
            return jsonify({
                "error": "Order must be cancelled before refund"
            }), 400

        if order.payment_status == "pending":
            return jsonify({
                "error": "Order has not been paid"
            }), 400

        if order.payment_status == "refunded":
            return jsonify({
                "error": "Order is already refunded"
            }), 400

        order.payment_status = "refunded"

        db.session.commit()

        return jsonify({
            "message": "Refund processed successfully",
            "order": {
                "id": order.id,
                "total_amount": order.total_amount,
                "status": order.status,
                "payment_status": order.payment_status
            }
        }), 200