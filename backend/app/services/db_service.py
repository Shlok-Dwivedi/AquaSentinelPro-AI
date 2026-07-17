from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models.db_models import Base

# Determine if we're using SQLite
is_sqlite = settings.DATABASE_URL.startswith("sqlite")

# Configure database engine
connect_args = {"check_same_thread": False} if is_sqlite else {}
engine = create_engine(settings.DATABASE_URL, connect_args=connect_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    """Initializes the database by creating tables if they do not exist."""
    Base.metadata.create_key_map = {}
    Base.metadata.create_all(bind=engine)

def get_db():
    """FastAPI database session dependency."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
