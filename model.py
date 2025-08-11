from datetime import datetime
from extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True)
    password_hash = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(20), nullable=False)  # 'admin', 'bidder', 'ppra'

    bids = db.relationship('Bid', back_populates='user', cascade="all, delete-orphan")
    queries = db.relationship('Query', back_populates='user', cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


class Tender(db.Model):
    __tablename__ = 'tenders'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    description = db.Column(db.Text, nullable=False)
    document = db.Column(db.String(255), nullable=False)
    contract_address = db.Column(db.String(100), nullable=True)
    status = db.Column(db.String(20), default='active')  # active, closed, PO Awarded
    po_awarded = db.Column(db.Boolean, default=False)

    bids = db.relationship('Bid', back_populates='tender', cascade="all, delete-orphan")
    queries = db.relationship('Query', back_populates='tender', cascade="all, delete-orphan")


class Bid(db.Model):
    __tablename__ = 'bids'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    tender_id = db.Column(db.Integer, db.ForeignKey('tenders.id'), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
    tx_hash = db.Column(db.String(66), nullable=True)  # blockchain tx hash

    user = db.relationship('User', back_populates='bids')
    tender = db.relationship('Tender', back_populates='bids')


class Query(db.Model):
    __tablename__ = 'queries'

    id = db.Column(db.Integer, primary_key=True)
    tender_id = db.Column(db.Integer, db.ForeignKey('tenders.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    message = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=True)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)

    tender = db.relationship('Tender', back_populates='queries')
    user = db.relationship('User', back_populates='queries')
