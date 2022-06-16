import psycopg2
from psycopg2.extras import RealDictCursor
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import time
from .config import settings

# To connect PostgreSQL
# SQLALCHEMY_DATABASE_URL = 'postgresql://<username>:<password>@<ip-address/hostname>/<database_name>'
SQLALCHEMY_DATABASE_URL = f'postgresql://{settings.database_username}:{settings.database_password}@{settings.database_hostname}:{settings.database_port}/{settings.database_name}'

# Engine：用來把sqlalchemy和postgresql做連接
engine = create_engine(SQLALCHEMY_DATABASE_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    # Create a session to our database for every request on endpoint
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# connect to PostgresSQL
while True:
    try:
        conn = psycopg2.connect(
            # Default:5432, but I used docker container, so change to port=8080
            host=settings.database_hostname, database=settings.database_name, user=settings.database_username, port=settings.database_port,
            password=settings.database_password, cursor_factory=RealDictCursor)
        cursor = conn.cursor()
        print("Database connection was successful!")
        break

    except Exception as error:
        print("Connecting to database failed")
        print("Error: ", error)
        time.sleep(2)
