from flask import Blueprint, request, jsonify
from models.customer import CustomerInformation
from models.account import AccountInformation
import jwt
from models import db
from helpers.middleware import is_authenticated, is_admin
from decimal import Decimal
from sqlalchemy import or_
from . import bcrypt

customer = Blueprint('customer', __name__)

SECRET_KEY = "secret"


@customer.route('/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        if not data:
            return "Bad Request", 400

        username = data["username"]
        password = data["password"]

        if not (username or password):
            return "Bad Request", 400

        customer = CustomerInformation.query.filter_by(
            username=username).first()
        if not customer:
            return (f'No account exists with the username {username}.\nPlease '
                    f'enter a valid username.'), 404
        if customer.status == 'I':
            return (f'Customer account with username {username} has been '
                    f'deactivated.\nPlease enter a valid username.'), 406

        if not bcrypt.check_password_hash(customer.password, password):
            return "Invalid Password", 401

        token = jwt.encode({"customer_id": customer.customer_id}, SECRET_KEY)

        return jsonify({"token": token}), 200
    except Exception as e:
        # Log the exception to help diagnose the issue
        print(f"Exception: {str(e)}")
        return 'Unexpected error occurred.', 500


@customer.route('/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        if not data:
            return "Bad Request", 400

        existing_user_username = CustomerInformation.query.filter_by(
            username=data["username"]).first()
        existing_user_email = CustomerInformation.query.filter_by(
            email=data["email"]).first()

        if existing_user_username:
            return (
                f"An account with the username {existing_user_username.username} "
                f"already exists.\nPlease choose a different one."), 400
        elif existing_user_email:
            return (
                f"An account with the email {existing_user_email.email} "
                f"already exists.\nPlease choose a different one."), 400
        else:
            # Hash password
            hashed_pw = bcrypt.generate_password_hash(data["password"]).decode(
                'utf-8')

            customer = CustomerInformation(
                username=data["username"],
                email=data["email"],
                password=hashed_pw,
                full_name=data["full_name"],
                age=data["age"],
                gender=data["gender"],
                zip_code=data["zip_code"],
                status=data["status"]
            )
            db.session.add(customer)
            db.session.commit()

            return jsonify(customer.serialize()), 200
    except Exception as e:
        # Log the exception to help diagnose the issue
        print(f"Exception: {str(e)}")
        db.session.rollback()  # revert changes if any error occurs
        return 'Unexpected error occurred.', 500



# Deactivate Customer Account
@customer.route('/deactivateCustomer', methods=['PATCH'])
@is_authenticated
def deactivate_customer():
    customer_id = request.currentUser
    customer = CustomerInformation.query.get(customer_id)
    password = request.get_json().get('password')
    hashed_password = CustomerInformation.query.get(customer_id).password
    if not bcrypt.check_password_hash(hashed_password, password):
        return 'Incorrect password', 401
    if not customer:
        return (f'Customer Account with customer_id {customer_id} not found',
                404)
    if customer.status == 'I':
        return (f'Customer Account with customer_id {customer_id} is '
                f'inactive', 404)
    try:
        customer_id = request.currentUser
        customer = CustomerInformation.query.get(customer_id)
        if not customer:
            return (
            f'Customer Account with customer_id {customer_id} not found',
            404)
        if customer.status == 'I':
            return (f'Customer Account with customer_id {customer_id} is '
                    f'inactive', 406)
        # only deactivate customer if all bank accounts are inactive
        account = db.session.query(AccountInformation).filter(
            AccountInformation.customer_id == customer.customer_id,
            AccountInformation.status == 'A').first()
        if account:
            return ('Please close all active bank accounts before attempting '
                    'to deactivate your user account.'), 400
        customer.status = 'I'
        db.session.commit()
        return (f'Customer Account with customer_id {customer_id} '
                f'deactivated successfully'), 200
    except Exception as e:
        # Log the exception to help diagnose the issue
        print(f"Exception: {str(e)}")
        db.session.rollback()  # revert changes if any error occurs
        return 'Unexpected error occurred.', 500


# Retrieve customer info by customer_id
@customer.route('/getCustomer', methods=['GET'])
@is_authenticated
def get_customer_by_id():
    try:
        customer_id = request.currentUser
        customer = CustomerInformation.query.get(customer_id)
        if not customer:
            return jsonify({'error': f'Customer Account with customer_id '
                                     f'{customer_id} not found'}), 404
        # add additional check for 'I' status?
        return jsonify(customer.serialize()), 200
    except Exception as e:
        # Log the exception to help diagnose the issue
        print(f"Exception: {str(e)}")
        return 'Unexpected error occurred.', 500


# Get all customers
@customer.route('/getCustomers', methods=['GET'])
@is_authenticated
@is_admin
def get_customers():
    try:
        customers = CustomerInformation.query.all()
        customer_list = []
        for customer in customers:
            customer_data = {
                'customer_id': customer.customer_id,
                'username': customer.username,
                'email': customer.email,
                'password': customer.password,
                'full_name': customer.full_name,
                'age': customer.age,
                'gender': customer.gender,
                'zip_code': customer.zip_code,
                'status': customer.status
            }
            customer_list.append(customer_data)

        return jsonify(customer_list), 200
    except Exception as e:
        # Log the exception to help diagnose the issue
        print(f"Exception: {str(e)}")
        return 'Unexpected error occurred.', 500
    
@customer.route('/updateCustomer', methods=['PATCH'])
@is_authenticated
def update_customer():
    try:
        customer_id = request.currentUser
        customer = CustomerInformation.query.get(customer_id)

        if not customer:
            return jsonify({'error': 'Customer not found'}), 404

        if customer.status == 'I':
            return jsonify({'error': 'Inactive customer account'}), 406

        data = request.get_json()

        if not data:
            return jsonify({'error': 'Bad request'}), 400
        
        # check if the request contains any of the expected attributes
        expected_attributes = {'new_username', 'new_email', 'new_password', 'new_name', 'new_zipcode'}
        if not expected_attributes.intersection(data.keys()):
            return jsonify({'error': 'No new information was provided'}), 400
        
        # Check if the new_username is provided, it's different from the current username
        if 'new_username' in data and data['new_username'] != customer.username:
            # Check if the new_username already exists in the database
            existing_user = CustomerInformation.query.filter_by(username=data['new_username']).first()
            if existing_user:
                return jsonify({'error': 'Username is already taken'}), 400
            else:  # update the username
                customer.username = data['new_username']

        if 'new_email' in data:
            existing_user = CustomerInformation.query.filter_by(email=data['new_email']).first()
            if existing_user:
                return jsonify({'error': 'Email is already in use.'}), 400
            customer.email = data['new_email']

        if 'new_password' in data:
            customer.password = bcrypt.generate_password_hash(data['new_password']).decode('utf-8')

        if 'new_name' in data:
            customer.full_name = data['new_name']

        if 'new_zipcode' in data:
            customer.zip_code = data['new_zipcode']

        db.session.commit()

        update_customer = CustomerInformation.query.get(customer_id)

        return jsonify({'updated_customer': update_customer.serialize()}), 200

    except Exception as e:
        print(f"Exception: {str(e)}")
        db.session.rollback()  # revert changes if any error occurs
        return jsonify({'error': 'Unexpected error occurred'}), 500
