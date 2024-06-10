from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from schemas import schemas
from handler import handler, auth
from db import db
from handler.logger import logger

app = APIRouter(tags=["Orders"])


@app.post("/orders/")
def create_order(order: schemas.Order, db: Session = Depends(db.get_db),
                 current_user: schemas.User = Depends(auth.get_current_user)):
    logger.info("create order: {}".format(order))
    if current_user.role != 'Customer':
        logger.exception("Only Customer can create orders")
        raise HTTPException(status_code=400, detail="Managers cannot create orders")
    response = handler.create_order(db=db, order=order, customer_id=current_user.id)
    return response


@app.get("/orders/")
def read_orders(skip: int = 0, limit: int = 10, db: Session = Depends(db.get_db),
                current_user: schemas.User = Depends(auth.get_current_user)):
    if current_user.role != 'Customer':
        orders = handler.get_orders(db, skip=skip, limit=limit)
    else:
        orders = handler.get_orders_by_customer(db, customer_id=current_user.id, skip=skip, limit=limit)
    return orders
