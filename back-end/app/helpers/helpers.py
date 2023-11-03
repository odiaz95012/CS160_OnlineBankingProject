from models.automatic_payment import AutomaticPayments
from models.transaction import TransactionHistory
from models.customer import CustomerInformation
from models.account import AccountInformation
from models import db
from . import bcrypt


def create_transaction_history_entry(customer_id, account_id, action, amount):
    transaction = TransactionHistory(
        customer_id=customer_id,
        account_id=account_id,
        action=action,
        amount=amount
    )
    db.session.add(transaction)
    db.session.commit()


def create_automatic_payment_entry(customer_id, account_id, amount, date):
    autopayment = AutomaticPayments(
        customer_id=customer_id,
        account_id=account_id,
        amount=amount,
        date=date
    )
    db.session.add(autopayment)
    db.session.commit()


def delete_automatic_payment_entry(payment_id):
    AutomaticPayments.query.filter(AutomaticPayments.payment_id ==
                                   payment_id).delete()
    db.session.commit()


def create_bank_manager():
    admin = CustomerInformation.query.filter_by(
        username="bank_manager").first()
    if not admin:
        bank_manager = CustomerInformation(
            username='bank_manager',
            email='bank_manager@gmail.com',
            password=bcrypt.generate_password_hash(
                'Hoken-Admin1').decode('utf-8'),
            full_name='Bank Manager',
            age=150,
            gender='O',
            zip_code=10000,
            status='A'
        )
        db.session.add(bank_manager)
        db.session.commit()


def create_dummy_customers():
    customer_data = [
        {
            'username': 'test_user1',
            'email': 'testuser1@gmail.com',
            'password': '12345678',
            'full_name': 'Test User 1',
            'age': 22,
            'gender': 'F',
            'zip_code': 95116,
            'status': 'A'
        },
        {
            'username': 'test_user2',
            'email': 'testuser2@gmail.com',
            'password': '12345678',
            'full_name': 'Test User 2',
            'age': 22,
            'gender': 'M',
            'zip_code': 95116,
            'status': 'A'
        },
        {
            'username': 'test_user3',
            'email': 'testuser3@gmail.com',
            'password': '12345678',
            'full_name': 'Test User 3',
            'age': 24,
            'gender': 'F',
            'zip_code': 95012,
            'status': 'I'
        }
    ]
    for cus in customer_data:
        customer = CustomerInformation(
            username=cus['username'],
            email=cus['email'],
            password=bcrypt.generate_password_hash(
                cus['password']).decode('utf-8'),
            full_name=cus['full_name'],
            age=cus['age'],
            gender=cus['gender'],
            zip_code=cus['zip_code'],
            status=cus['status']
        )
        db.session.add(customer)

    db.session.commit()


def create_dummy_accounts():
    account_data = [
        {
            'customer_id': 2,
            'account_type': 'Checking',
            'balance': 1111.11,
            'status': 'A'
        },
        {
            'customer_id': 3,
            'account_type': 'Savings',
            'balance': 2222.22,
            'status': 'A'
        },
        {
            'customer_id': 4,
            'account_type': 'Checking',
            'balance': 0,
            'status': 'I'
        }
    ]
    for acc in account_data:
        account = AccountInformation(
            customer_id=acc['customer_id'],
            account_type=acc['account_type'],
            balance=acc['balance'],
            status=acc['status']
        )
        db.session.add(account)

    db.session.commit()
