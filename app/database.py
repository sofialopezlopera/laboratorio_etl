from pymongo import MongoClient
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.config import settings

# Conexión MongoDB
mongo_client = MongoClient(settings.mongo_uri)
mongo_database = mongo_client[settings.mongo_database]
mongo_collection = mongo_database[settings.mongo_collection]

# Configuración MySQL
mysql_engine = create_engine(settings.database_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=mysql_engine)
Base = declarative_base()

def get_mongo_collection():
    return mongo_collection

def create_sql_tables():
    Base.metadata.create_all(bind=mysql_engine)

def get_mysql_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()
        