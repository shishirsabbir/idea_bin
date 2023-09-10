# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account, Idea
from typing import Annotated, Literal
from sqlalchemy.orm import Session
from .auth import get_current_user
from pydantic import BaseModel


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/idea"
)


# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# SETUP APP KEY FOR FRONTEND
APP_KEY = "b6655a6929beb2ad975ac68b8373db51"


# PYDANTIC CLASSES FOR CREATE IDEAS OR GET IDEAS

