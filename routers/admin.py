from fastapi import APIRouter, Depends, Path, HTTPException
from starlette import status
from models import Todos
from sqlalchemy.orm import Session
from typing import Annotated
from .auth import get_current_user
from database import SessionLocal

router = APIRouter(
    prefix='/admin',
    tags=['admin']
)

# Fonction pour crée une session et la fermer si la requete se termine
def get_db():
    db = SessionLocal()
    try:
        yield db  # permet de faire une fonction qui une fois une valeur retourner ne s'arrete pas
    finally:
        db.close()

db_dependency = Annotated[Session, Depends(get_db)]
user_dependecy = Annotated[dict, Depends(get_current_user)]

@router.get('/todos', status_code=status.HTTP_200_OK)
async def read_all(user: user_dependecy, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentification Faild')
    return db.query(Todos).all()

@router.delete('/todo/{todo_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delte_todo(user: user_dependecy, db: db_dependency, todo_id: int):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=401, detail='Authentification Faild')
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    db.delete(todo_model)
    db.commit()