import os

from dotenv import load_dotenv
from sqlalchemy.engine import URL


load_dotenv()


class Settings:
    mongo_uri: str = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    mongo_database: str = os.getenv("MONGO_DATABASE", "laboratorio_etl")
    mongo_collection: str = os.getenv("MONGO_COLLECTION", "productos_raw")

    database_url: str = os.getenv(
        "DATABASE_URL",
        "mysql+mysqlconnector://root:@localhost:3306/laboratorio_etl"
    )

    dummyjson_products_url: str = os.getenv(
        "DUMMYJSON_PRODUCTS_URL",
        "https://dummyjson.com/products"
    )

    dummyjson_timeout_seconds: int = int(
        os.getenv("DUMMYJSON_TIMEOUT_SECONDS", "20")
    )

settings = Settings()