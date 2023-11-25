from pathlib import Path

from sqlalchemy import create_engine

BASE_DIR = Path(__file__).resolve().parent.parent.parent

db_engine = create_engine(f"sqlite:///{BASE_DIR}/database/telegram_bot.db", echo=True)
