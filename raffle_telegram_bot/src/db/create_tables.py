from .connection import db_engine
from .models import Base


def create_tables() -> None:
    Base.metadata.create_all(bind=db_engine)
