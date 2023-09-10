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


# PYDANTIC CLASSES FOR CREATE IDEAS OR GET IDEAS
class CreateIdeaRequest(BaseModel):
    title: str
    content: str
    category: Literal["General", "Technology", "Marketing", "Business", "Application", "Tools"]


class IdeaResponseModel(BaseModel):
    id: int
    title: str
    content: str
    category: str


# CREATING A USER DEPENDENCY FOR JWT AUTHORIZATION
user_dependency = Annotated[dict, Depends(get_current_user)]


# CREATING ROUTES FOR IDEA
@router.get('/', status_code=status.HTTP_200_OK)
async def get_ideas(user: user_dependency, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    return db.query(Idea).all()


@router.get('/{content_id}', status_code=status.HTTP_200_OK)
async def get_idea(user: user_dependency, db: db_dependency, content_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == content_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    return idea_model


@router.post('/', status_code=status.HTTP_204_NO_CONTENT)
async def create_idea(user: user_dependency, db: db_dependency, create_idea_request: CreateIdeaRequest, content_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = Idea(**create_idea_request.model_dump(), owner=user.get("user_id"))

    db.add(idea_model)
    db.commit()


@router.delete('/{content_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(user: user_dependency, db: db_dependency, content_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == content_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    db.query(Idea).filter(Idea.id == content_id).delete()
