from sqlalchemy.orm import Session

from src import RaffleModel
from src.db.connection import db_engine
from src.utils import sanitize_xss


def create_raffle(
    name: str,
    user_id: str,
    username: str,
    publishers: str,
    numbers: int,
    marked_numbers: str,
):
    data = sanitize_xss(
        {
            name: name,
            user_id: user_id,
            username: username,
            publishers: publishers,
            numbers: numbers,
            marked_numbers: marked_numbers,
        }
    )
    with Session(db_engine) as session:
        raffle = RaffleModel(**data)
        session.add(raffle)
        session.commit()
