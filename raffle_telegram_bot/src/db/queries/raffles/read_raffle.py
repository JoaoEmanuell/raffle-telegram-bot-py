from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine


def read_raffle(**args_to_query) -> dict[str | bool]:
    with Session(db_engine) as session:
        raffle = session.query(RaffleModel).filter_by(**args_to_query).first()

        if raffle:
            session.close()
            return {
                "status": True,
                "msg": {
                    "name": raffle.name,
                    "publishers": raffle.publishers,
                    "numbers": raffle.numbers,
                    "marked_numbers": raffle.marked_numbers,
                    "image_base": raffle.image_base,
                    "image_base_rectangle_positions": raffle.image_base_rectangle_positions,
                },
            }
        else:
            session.close()
            return {"status": False, "msg": "Erro, rifa não existe!"}
