from sqlalchemy import String, Integer, Column

from .base import Base


class RaffleModel(Base):
    __tablename__ = "raffle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(200))  # raffle name
    user_id = Column(String(30))  # creator user id
    chat_id = Column(String(20))  # chat id
    username = Column(String(35))  # creator username
    publishers = Column(String())  # separate with spaces
    numbers = Column(Integer)  # value of the max number
    marked_numbers = Column(String())  # separate with spaces
