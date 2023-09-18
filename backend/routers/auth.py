# IMPORTING MODULES
from fastapi import APIRouter, Depends, HTTPException, status, Path
from database import SessionLocal, Account
from typing import Annotated, Literal
from sqlalchemy.orm import Session
from pydantic import BaseModel
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from datetime import datetime, timedelta
from jose import jwt, JWTError


# DECLARING THE ROUTER APP
router = APIRouter(
    prefix="/auth"
)

# FUNCTION FOR DATABASE CONNECTION AND DEPENDENCY INJECTION
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]


# PYDANTIC CLASSES FOR JWT TOKEN, CREATE ACCOUNT, PASSWORD CHANGE REQUEST
class Token(BaseModel):
    access_token: str
    token_type: str


class CreateAccountRequest(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    password: str
    role: Literal["developer", "user"] # can not create a admin account

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "first_name": "John",
                    "last_name": "Doe",
                    "username": "john_doe",
                    "email": "johndoe@mail.com",
                    "password": "test123",
                    "role": "developer"
                }
            ]
        }
    }


class ChangePasswordRequest(BaseModel):
    password: str
    new_password: str

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "password": "test123",
                    "new_password": "test1234"
                }
            ]
        }
    }


class AccountInfoRespone(BaseModel):
    first_name: str
    last_name: str
    username: str
    email: str
    role: str


#  AUTHENTICATION AND AUTHORIZATION CONFIGURATION
bcrypt_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "6d01e7361f92143981fe10d92716f0d84596d803eeda1dcf6d2ee19f1f1d656b"
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")


# FUNCTION FOR AUTHENTICATE USER
def authenticate_user(username: str, password: str, db_session):
    user = db_session.query(Account).filter(Account.username == username).first()

    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    
    return user


# FUNCTION FOR JWT TOKEN GENERATE
def create_access_token(username: str, user_id: int, user_role: str, expires_delta: timedelta):
    to_encode = {"sub": username, "id": user_id, "role": user_role}
    expires = datetime.utcnow() + expires_delta
    to_encode.update({"exp": expires})

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# FUNCTION FOR GET CURRENT USER
async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        user_id = payload.get("id")
        user_role = payload.get("role")

        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't authorize the user")
        
        return {"username": username, "user_id": user_id, "user_role": user_role}
    
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't authorize the user")    


# CREATING ROUTES FOR LOGIN AND CREATE ACCOUNT
# FORM DEPENDENCY FOR OAUTH2PASSWORDREQUESTFORM
form_dependency = Annotated[OAuth2PasswordRequestForm, Depends()]


@router.post('/login', response_model=Token)
async def login_for_access_token(db: db_dependency, form_data: form_dependency):
    account_model = authenticate_user(form_data.username, form_data.password, db)
    if not account_model:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Couldn't validate the credentials")
    
    token = create_access_token(username = account_model.username, user_id = account_model.id, user_role = account_model.role, expires_delta=timedelta(minutes=60))
    return {"access_token": token, "token_type": "bearer"}


@router.post('/register', status_code=status.HTTP_201_CREATED)
async def create_account(db: db_dependency, create_account_request: CreateAccountRequest):
    account_model = Account(
        first_name = create_account_request.first_name.casefold(),
        last_name = create_account_request.last_name.casefold(),
        username = create_account_request.username.casefold(),
        email = create_account_request.email,
        hashed_password = bcrypt_context.hash(create_account_request.password),
        role = create_account_request.role.casefold()
    )

    db.add(account_model)
    db.commit()


# CREATING A USER DEPENDENCY
user_dependency = Annotated[dict, Depends(get_current_user)]

@router.put('/password', status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependency, db: db_dependency, change_password_requst: ChangePasswordRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    user_model = db.query(Account).filter(Account.username == user.get("username")).first()
    if not bcrypt_context.verify(change_password_requst.password, user_model.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Password doesn't match")
    
    user_model.hashed_password = bcrypt_context.hash(change_password_requst.new_password)

    db.add(user_model)
    db.commit()


@router.get('/account', status_code=status.HTTP_200_OK)
async def get_account_info(user: user_dependency, db: db_dependency) -> AccountInfoRespone:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    user_model = db.query(Account).filter(Account.id == user.get("user_id")).first()
    user_info = AccountInfoRespone(
        first_name=user_model.first_name,
        last_name=user_model.last_name,
        username=user_model.username,
        email=user_model.email,
        role=user_model.role
    )

    return user_info

