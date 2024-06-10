from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordRequestForm
from datetime import timedelta
from schemas import schemas
from handler import handler, auth
from db import db
from handler.logger import logger
from handler.config import DevConfig
app = APIRouter(tags=["User"])


@app.post("/token", response_model=schemas.Token)
def login_for_access_token(db: Session = Depends(db.get_db), form_data: OAuth2PasswordRequestForm = Depends()):
    user = auth.authenticate_user(db, form_data.username, form_data.password)
    if not user:
        logger.exception("Incorrect username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(db.get_db)):
    logger.info("create user: {}".format(user))
    db_user = handler.get_user_by_username(db, username=user.username)
    if db_user:
        logger.exception("Username already registered")
        raise HTTPException(status_code=400, detail="Username already registered")
    if user.role not in DevConfig.Role_list:
        logger.exception("This role {} is not exist, please input {}".format(user.role, DevConfig.Role_list))
        raise HTTPException(status_code=400, detail="This role {} is not exist, please input {}".format(user.role, DevConfig.Role_list))
    create_user_response = handler.create_user(db=db, user=user)
    return create_user_response
