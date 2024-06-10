from fastapi import FastAPI, HTTPException, status, Request
from fastapi.responses import JSONResponse
import uvicorn
from models import models
from db import db
from view.order import app as order
from view.product import app as product
from view.user import app as user
from handler.logger import logger

app = FastAPI(title="Order Management API",
              description="API for managing orders and products",
              version="1.0.0")
app.include_router(user)
app.include_router(order)
app.include_router(product)

models.Base.metadata.create_all(bind=db.engine)


@app.middleware("http")
async def log_requests(request: Request, call_next):
    try:
        response = await call_next(request)
        return response
    except Exception as e:
        logger.error(f"Error: {e}")
        return JSONResponse(status_code=500, content={"detail": "Internal Server Error"})


@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP Exception: {exc.detail}")
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
    )


@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled Exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Internal Server Error"},
    )


if __name__ == "__main__":
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
