from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from utils.config import get_settings

engine = create_engine(get_settings().pg_url, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
