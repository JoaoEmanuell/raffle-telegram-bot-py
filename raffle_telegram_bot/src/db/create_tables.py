from .connection import db_engine
from .models import Base


def create_tables() -> None:
    # metadata = MetaData()
    # metadata.create_all(bind=db_engine, tables=[RaffleModel])
    Base.metadata.create_all(bind=db_engine)
