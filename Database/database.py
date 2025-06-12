from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.engine.url import URL
from sqlalchemy.pool import NullPool
from sqlalchemy import create_engine
from contextlib import contextmanager
from dotenv import load_dotenv
import os
load_dotenv()

connect_url = URL.create(
    "mysql+pymysql",
    username=os.environ["MYSQL_USER"],
    password=os.environ["MYSQL_PASSWORD"],
    host=os.environ["MYSQL_HOST"],
    port=3306,
    database=os.environ["MYSQL_DB"],
)

engine = create_engine(connect_url, poolclass=NullPool)
Session = sessionmaker(
    autocommit=False, autoflush=False, bind=engine, expire_on_commit=False)
Base = declarative_base()


@contextmanager
def session_manager():
    session = Session()
    try:
        yield session
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
