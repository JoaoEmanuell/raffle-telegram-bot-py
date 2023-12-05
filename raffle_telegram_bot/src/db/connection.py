from sqlalchemy import create_engine

from ..utils import database_path

db_engine = create_engine(f"sqlite:///{database_path}/telegram_bot.db")
