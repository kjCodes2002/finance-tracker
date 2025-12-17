from sqlalchemy import Column, String, DateTime, Numeric, func, ForeignKey, UniqueConstraint
from sqlalchemy.orm import declarative_base, relationship
from uuid import uuid4

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))
    email = Column(String(255), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    wallets = relationship('Wallet', back_populates='user', cascade='all, delete-orphan')
    categories = relationship('Category', back_populates='user', cascade='all, delete-orphan')
    transactions = relationship('Transaction', back_populates='user', cascade='all, delete-orphan')

class Wallet(Base):
    __tablename__ = 'wallets'

    id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='wallets')
    transactions = relationship('Transaction', back_populates='wallet', cascade='all, delete-orphan')

class Category(Base):
    __tablename__ = 'categories'
    __table_args__ = (
        UniqueConstraint('user_id', 'name', name='uq_user_category_name'),
    )

    id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), nullable=False, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='categories')
    transactions = relationship('Transaction', back_populates='category')

class Transaction(Base):
    __tablename__ = 'transactions'

    id = Column(String(36), primary_key=True, index=True, default = lambda: str(uuid4()))
    user_id = Column(String(36), ForeignKey('users.id', ondelete='CASCADE'), index=True, nullable=False)
    wallet_id = Column(String(36), ForeignKey('wallets.id', ondelete='CASCADE'), nullable=False, index=True)
    category_id = Column(String(36), ForeignKey('categories.id'), nullable=True)
    amount = Column(Numeric(12, 2), nullable=False)
    type = Column(String(10), nullable=False)  # 'income' | 'expense'
    description = Column(String(255), nullable=False)
    transaction_date = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    user = relationship('User', back_populates='transactions')
    wallet = relationship('Wallet', back_populates='transactions')
    category = relationship('Category', back_populates='transactions')
