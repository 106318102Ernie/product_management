from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from models import models
from schemas import schemas
from .auth import get_password_hash
from .logger import logger


def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()


def create_user(db: Session, user: schemas.UserCreate):
    try:
        hashed_password = get_password_hash(user.password)
        db_user = models.User(username=user.username, hashed_password=hashed_password, role=user.role)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user
    except Exception as ex:
        logger.exception(ex)
        db.rollback()
        raise HTTPException(status_code=500, detail="database create user fail")


def get_products(db: Session, skip: int = 0, limit: int = 10, price_min: Optional[float] = None,
                 price_max: Optional[float] = None, stock_min: Optional[int] = None, stock_max: Optional[int] = None):
    query = db.query(models.Product)
    if price_min is not None:
        query = query.filter(models.Product.price >= price_min)
    if price_max is not None:
        query = query.filter(models.Product.price <= price_max)
    if stock_min is not None:
        query = query.filter(models.Product.stock >= stock_min)
    if stock_max is not None:
        query = query.filter(models.Product.stock <= stock_max)
    return query.offset(skip).limit(limit).all()


def create_product(db: Session, product: schemas.ProductCreate):
    try:
        db_product = models.Product(**product.dict())
        db.add(db_product)
        db.commit()
        db.refresh(db_product)
        return db_product
    except Exception as ex:
        logger.exception(ex)
        db.rollback()
        raise HTTPException(status_code=500, detail="database create product fail")


def get_product(db: Session, product_id: int):
    return db.query(models.Product).filter(models.Product.id == product_id).first()


def update_product(db: Session, product_id: int, product: schemas.ProductCreate):
    try:
        db_product = get_product(db, product_id)
        if db_product:
            for key, value in product.dict().items():
                setattr(db_product, key, value)
            db.commit()
            db.refresh(db_product)
        return db_product
    except Exception as ex:
        logger.exception(ex)
        db.rollback()
        raise HTTPException(status_code=500, detail="database update product fail")


def delete_product(db: Session, product_id: int):
    try:
        db_product = get_product(db, product_id)
        if db_product and not db_product.orders:
            db.delete(db_product)
            db.commit()
        return db_product
    except Exception as ex:
        logger.exception(ex)
        db.rollback()
        raise HTTPException(status_code=500, detail="database delete product fail")


def get_orders(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Order).offset(skip).limit(limit).all()


def get_orders_by_customer(db: Session, customer_id: int, skip: int = 0, limit: int = 10):
    return db.query(models.Order).filter(models.Order.customer_id == customer_id).offset(skip).limit(limit).all()


def create_order(db: Session, order: schemas.Order, customer_id: int):
    try:
        db_order = models.Order(customer_id=customer_id)
        product_dict = {}
        for product_id in order.product_ids:
            product = db.query(models.Product).filter(models.Product.id == product_id).first()
            if product and product.stock > 0:
                product.stock -= 1
                db_order.product.append(product)
                if product.name not in product_dict:
                    product_dict[product.name] = 1
                else:
                    product_dict[product.name] += 1
            else:
                raise HTTPException(status_code=400, detail="Product out of stock")
        db_order.products = product_dict
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        return {"order id": db_order.id}
    except Exception as ex:
        logger.exception(ex)
        db.rollback()
        raise HTTPException(status_code=500, detail="database create order fail")