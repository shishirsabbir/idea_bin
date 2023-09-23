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
    # category: Literal["General", "Technology", "Marketing", "Business", "Application", "Tools"]
    subtitle: str

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "LinkedIn Web Crawler",
                    "content": "A LinkedIn scraper in Python is a script or program that extracts data from LinkedIn profiles or pages using web scraping techniques. It typically leverages libraries like BeautifulSoup and requests to access and retrieve information from LinkedIn's public web pages.",
                    "subtitle": "Dedicated web crawler for linkedin"
                }
            ]
        }
    }


class UpdateIdeaRequest(BaseModel):
    title: str
    content: str
    # category: Literal["General", "Technology", "Marketing", "Business", "Application", "Tools"]
    subtitle: str

    model_config= {
        "json_schema_extra": {
            "examples": [
                {
                    "title": "LinkedIn Web Crawler",
                    "content": "A LinkedIn scraper in Python is a script or program that extracts data from LinkedIn profiles or pages using web scraping techniques. It typically leverages libraries like BeautifulSoup and requests to access and retrieve information from LinkedIn's public web pages.",
                    "subtitle": "Application"
                }
            ]
        }
    }


class IdeaResponseModel(BaseModel):
    id: int
    title: str
    content: str
    category: str
    author: int


# CREATING A USER DEPENDENCY FOR JWT AUTHORIZATION
user_dependency = Annotated[dict, Depends(get_current_user)]


# CREATING ROUTES FOR IDEA
@router.get('/', status_code=status.HTTP_200_OK)
async def get_ideas(user: user_dependency, db: db_dependency) -> list[IdeaResponseModel]:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_list = db.query(Idea).all()
    idea_model_list = [IdeaResponseModel(id=idea.id, title=idea.title, content=idea.content, subtitle=idea.subtitle, author=idea.author) for idea in idea_list]
    
    return idea_model_list


@router.get('/{content_id}', status_code=status.HTTP_200_OK)
async def get_idea(user: user_dependency, db: db_dependency, content_id: int = Path(gt=0)) -> IdeaResponseModel:
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == content_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    idea_model_response = IdeaResponseModel(
        id = idea_model.id,
        title = idea_model.title,
        content = idea_model.content,
        subtitle = idea_model.subtitle,
        author = idea_model.author
    )
    
    return idea_model_response


@router.post('/', status_code=status.HTTP_204_NO_CONTENT)
async def create_idea(user: user_dependency, db: db_dependency, create_idea_request: CreateIdeaRequest):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = Idea(**create_idea_request.model_dump(), owner=user.get("user_id"))

    db.add(idea_model)
    db.commit()


# @router.put('/{content_id}', status_code=status.HTTP_204_NO_CONTENT)
# async def update_idea(user: user_dependency, db: db_dependency, update_idea_request: UpdateIdeaRequest, content_id: int = Path(gt=0)):
#     if user is None:
#         raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
#     idea_model = db.query(Idea).filter(Idea.id == content_id).first()
#     if idea_model is None:
#         raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
#     idea_model.title = update_idea_request.title
#     idea_model.content = update_idea_request.content
#     idea_model.subtitle = update_idea_request.subtitle

#     db.add(idea_model)
#     db.commit()


@router.delete('/{content_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_idea(user: user_dependency, db: db_dependency, content_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed")
    
    idea_model = db.query(Idea).filter(Idea.id == content_id).first()
    if idea_model is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Idea not found")
    
    db.query(Idea).filter(Idea.id == content_id).delete()
    db.commit()
    
