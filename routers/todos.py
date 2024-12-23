from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from sqlalchemy.orm import Session
from database import SessionLocal
from typing import Annotated
from pydantic import BaseModel, Field
from models import Todos
from .auth import get_current_user
router = APIRouter()

# Fonction pour crée une session et la fermer si la requete se termine
def get_db():
    db = SessionLocal()
    try:
        yield db  # permet de faire une fonction qui une fois une valeur retourner ne s'arrete pas
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependecy = Annotated[dict, Depends(get_current_user)]

class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=1, max_length=100)
    priority: int = Field(gt=0, lt=6)
    complete: bool

# BreakPoint pour retourner l'ensemble des todos
@router.get('/', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependecy, db: db_dependency):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification error')
    # Recupère tous les éléments de la base de donnée associer a un user
    return db.query(Todos).filter(Todos.owner_id == user.get('user_id')).all()

# Recuperer un todo precise
@router.get('/todo/{todo_id}', status_code=status.HTTP_200_OK)
def get_todo(user:user_dependecy, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification error')

    todo_model = (db.query(Todos).filter(Todos.id == todo_id)\
                  .filter(Todos.owner_id == user.get('user_id')).first())

    if todo_model is not None:
        return todo_model
    raise HTTPException(status_code=404, detail="Todo not found")


# Ajouter un todo
@router.post('/todo', status_code=status.HTTP_201_CREATED)
def create_todo(user: user_dependecy,db: db_dependency, todo_request: TodoRequest):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification error')
    todo_model = Todos(**todo_request.model_dump(), owner_id = user.get('user_id'))
    db.add(todo_model)
    db.commit()


# Modifier un todo
@router.put('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def todo_update(user: user_dependecy, db: db_dependency, todo_id: int, todo_request: TodoRequest):

    if user is None:
        raise HTTPException(status_code=401, detail='Authentification error')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                                .filter(Todos.owner_id == user.get('user_id')).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')

    updatedTodo = Todos(**todo_request.model_dump())

    todo_model.title = updatedTodo.title
    todo_model.description = updatedTodo.description
    todo_model.complete = updatedTodo.complete
    todo_model.priority = updatedTodo.priority
    db.commit()

# Supprimer un todo
@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
def delete_todo(user: user_dependecy, db: db_dependency, todo_id: int):
    if user is None:
        raise HTTPException(status_code=401, detail='Authentification error')

    todo_model = db.query(Todos).filter(Todos.id == todo_id)\
                                .filter(Todos.owner_id == user.get('user_id')).first()
    if todo_model is None:
        raise HTTPException(status_code=404, detail='Todo not found')
    db.delete(todo_model)
    db.commit()