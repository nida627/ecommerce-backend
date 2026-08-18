# E-Commerce Backend API

A learning-based E-Commerce Backend API built using **Python Flask, SQLAlchemy, SQLite, JWT, and Bcrypt**.

## Features

* User Registration & Login
* JWT Authentication
* Role-based Authorization
* Admin Product Management
* Product CRUD Operations
* Shopping Cart
* Stock Validation
* Order Management
* Order Status Management
* Payment Simulation
* Order Cancellation
* Refund Simulation
* Database Migration with Flask-Migrate
* API Testing with Postman
* Automated Testing with Pytest

## Tech Stack

* Python
* Flask
* SQLAlchemy
* SQLite
* Flask-JWT-Extended
* Flask-Bcrypt
* Flask-Migrate
* Pytest
* Postman

## Project Structure

```text
Ecommerce Backend/
├── tests/
├── migrations/
├── instance/
├── ecommerce.py
├── models.py
├── routes.py
├── admin.py
├── requirements.txt
├── .env
└── README.md
```

## Main API Modules

```text
Authentication
    ├── Register
    └── Login

Products
    ├── Create
    ├── Read
    ├── Update
    └── Delete

Cart
    ├── Add
    ├── View
    ├── Update
    └── Remove

Orders
    ├── Place Order
    ├── View Orders
    ├── Cancel Order
    └── Update Status

Payment
    ├── Payment Simulation
    └── Refund Simulation
```

## Installation

```bash
git clone https://github.com/nida627/ecommerce-backend.git
cd ecommerce-backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

Create a `.env` file:

```env
JWT_SECRET_KEY=your-secret-key
```

Run the application:

```bash
python ecommerce.py
```

API will run at:

```text
http://127.0.0.1:5000
```

## Testing

### Postman

The APIs can be manually tested using Postman with JWT Bearer tokens.

### Pytest

Run automated tests:

```bash
pytest
```

## Note

This is a **learning project**. Payment and refund operations are simulated.

## Author

**Nida Ansari**

GitHub: https://github.com/nida627
