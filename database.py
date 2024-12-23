from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# Le lien de notre base de donnée
SQLALCHEMY_DATABASE_URL = 'postgresql://postgres:Fatou6802@localhost/TodoApplicationDatbase'

# Permet de crée le moteur qui etabliras la connexion avec la db
engine = create_engine(SQLALCHEMY_DATABASE_URL)

# Nous créons un objet de session qui seras utiliser pour interagir avec notre base de donnée
# autocommit a False pour dire que les operation effectuer ici ne serons pas directement appliquer la db reel
# engine pour recuperer la db a laaquel notre session sera connecter
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# permet de 
Base = declarative_base()

