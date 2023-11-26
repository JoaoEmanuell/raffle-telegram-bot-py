from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine


def read_raffle(
    name: str,
    user_id: str,
    chat_id: str,
) -> [dict, str | bool]:
    with Session(db_engine) as session:
        raffle = (
            session.query(RaffleModel)
            .filter_by(name=name, user_id=user_id, chat_id=chat_id)
            .first()
        )

        if raffle:
            session.close()
            return {
                "status": True,
                "msg": {
                    "name": raffle.name,
                    "publishers": raffle.publishers,
                    "numbers": raffle.numbers,
                    "marked_numbers": raffle.marked_numbers,
                },
            }
        else:
            session.close()
            return {"status": False, "msg": "Erro, rifa não existe!"}
