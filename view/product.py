from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas import schemas
from handler import handler, auth
from db import db
from handler.logger import logger

app = APIRouter(tags=["Product"])


@app.post("/products/", response_model=schemas.Product)
def create_product(product: schemas.ProductCreate, db: Session = Depends(db.get_db),
                   current_user: schemas.User = Depends(auth.get_current_user)):
    logger.info("create product: {}".format(product))
    if current_user.role != 'Manager':
        logger.exception("Not enough permissions")
        raise HTTPException(status_code=400, detail="Not enough permissions")
    create_product_response = handler.create_product(db=db, product=product)
    return create_product_response


@app.get("/products/", response_model=List[schemas.Product])
def read_products(skip: int = 0, limit: int = 10, price_min: Optional[float] = None, price_max: Optional[float] = None,
                  stock_min: Optional[int] = None, stock_max: Optional[int] = None,
                  db: Session = Depends(db.get_db)):
    get_products = handler.get_products(db, skip=skip, limit=limit, price_min=price_min, price_max=price_max,
                                        stock_min=stock_min, stock_max=stock_max)
    return get_products


@app.put("/products/{product_id}", response_model=schemas.Product)
def update_product(product_id: int, product: schemas.ProductCreate, db: Session = Depends(db.get_db),
                   current_user: schemas.User = Depends(auth.get_current_user)):
    logger.info("product id: {}, update product: {}".format(product_id, product))
    if current_user.role != 'Manager':
        logger.exception("Not enough permissions")
        raise HTTPException(status_code=400, detail="Not enough permissions")
    update_product_response = handler.update_product(db=db, product_id=product_id, product=product)
    return update_product_response


@app.delete("/products/{product_id}", response_model=schemas.Product)
def delete_product(product_id: int, db: Session = Depends(db.get_db),
                   current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role != 'Manager':
        logger.exception("Not enough permissions")
        raise HTTPException(status_code=400, detail="Not enough permissions")
    product = handler.get_product(db=db, product_id=product_id)
    if product.orders:
        logger.exception("Product cannot be deleted, it has associated orders")
        raise HTTPException(status_code=400, detail="Product cannot be deleted, it has associated orders")
    delete_product_response = handler.delete_product(db=db, product_id=product_id)
    return delete_product_response
