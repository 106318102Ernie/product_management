from pydantic import BaseModel
from typing import List, Optional


class UserBase(BaseModel):
    username: str


class UserCreate(UserBase):
    password: str
    role: str


class User(UserBase):
    id: int
    role: str

    class Config:
        orm_mode = True


class ProductBase(BaseModel):
    name: str
    price: float
    stock: int


class ProductCreate(ProductBase):
    pass


class Product(ProductBase):
    id: int

    class Config:
        orm_mode = True


class Order(BaseModel):
    product_ids: List[int]


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: Optional[str] = None
