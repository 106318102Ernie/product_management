from sqlalchemy import Column, Integer, String, Float, Boolean, ForeignKey, Table, JSON
from sqlalchemy.orm import relationship
from db.db import Base

association_table = Table(
    'order_products', Base.metadata,
    Column('order_id', Integer, ForeignKey('orders.id')),
    Column('product_id', Integer, ForeignKey('products.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(String)


class Product(Base):
    __tablename__ = 'products'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    price = Column(Float)
    stock = Column(Integer)
    orders = relationship('Order', secondary=association_table, back_populates='product')


class Order(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey('users.id'))
    products = Column(JSON)
    customer = relationship('User')
    product = relationship('Product', secondary=association_table, back_populates='orders')
