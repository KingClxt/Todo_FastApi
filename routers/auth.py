from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from database import SessionLocal
from models import User
from starlette import status
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

router = APIRouter(
    prefix='/auth',
    tags=['auth']
)

SECRET_KEY = 'dd4232ad6c47bb89dfc0d97596126bd8ceca2e8557d8e1494ca89cdb05081e5e'
ALGORITHME = 'HS256'
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token')



def get_db():
    db = SessionLocal()
    try:
        yield db  # permet de faire une fonction qui une fois une valeur retourner ne s'arrete pas
    finally:
        db.close()

# Dependence pour cree une session a chaque requete
db_dependency = Annotated[Session, Depends(get_db)]

# Fonction pour verifier les informations fournis par l'utilisateur pour la connexion
def authenticate_user(username: str, password: str, db: Session):
    user: User = db.query(User).filter(User.username==username).first()
    if not user:
        return False
    if not bcrypt_context.verify(password, user.hashed_password):
        return False
    return user

#Fonction pour crée un token
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub':username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta
    encode.update({'exp':expires})
    return jwt.encode(encode, SECRET_KEY, ALGORITHME)

# Fonction pour verifier le jwt fournis par un utilisateur
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    try:
        payload = jwt.decode(token, SECRET_KEY, ALGORITHME)
        username = payload.get('sub')
        user_id = payload.get('id')
        role = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')
        return {"username":username, "user_id":user_id, 'role': role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Could not validate user.')

# Classe pour valider les données d'inscription d'un utilisateur
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    lastname: str
    password: str
    role: str

# Classe pour specifier le retoure de la fonction de connexion
class Token(BaseModel):
    access_token: str
    token_type: str

# Inscription d'un user
@router.post('/', status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, create_user: CreateUserRequest):

    create_user_model = User(
        email=create_user.email,
        username=create_user.username,
        first_name=create_user.first_name,
        last_name=create_user.lastname,
        hashed_password=bcrypt_context.hash(create_user.password),
        is_active=True,
        role=create_user.role
    )

    db.add(create_user_model)
    db.commit()

#Connexion d'un user
@router.post('/token', response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)

    if not user:
        return "Faild Authentification"
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=30))
    return {'access_token': token, 'token_type':'bearer'}