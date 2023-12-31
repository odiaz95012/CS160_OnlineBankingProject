from datetime import datetime
from . import db


class TransactionHistory(db.Model):
    __tablename__ = 'TransactionHistory'
    transaction_id = db.Column('transaction_id', db.Integer,
                               primary_key=True, autoincrement=True)
    customer_id = db.Column(db.Integer, db.ForeignKey(
        'CustomerInformation.customer_id'), nullable=False)
    account_id = db.Column(db.Integer, db.ForeignKey(
        'AccountInformation.account_id'), nullable=False)
    action = db.Column(db.String(20), nullable=False)
    amount = db.Column(db.Numeric(scale=2), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    __table_args__ = (
        db.CheckConstraint("action IN ('Deposit', 'Withdraw','Transfer', "
                           "'Normal Payment',  'Automatic Payment')",
                           name='check_action'),
        {})

    def __init__(self, customer_id: int, account_id: int, action: str,
                 amount: float):
        self.customer_id = customer_id
        self.account_id = account_id
        self.action = action
        self.amount = amount

    def serialize(self):
        return {
            'transaction_id': self.transaction_id,
            'customer_id': self.customer_id,
            'account_id': self.account_id,
            'action': self.action,
            'amount': self.amount,
            'date': self.date
        }
