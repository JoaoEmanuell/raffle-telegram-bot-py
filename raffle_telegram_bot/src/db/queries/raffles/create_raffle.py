from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine
from src.utils import sanitize_xss


def create_raffle(
    name: str,
    user_id: str,
    chat_id: str,
    username: str,
    publishers: str = None,
    numbers: int = None,
    marked_numbers: str = None,
) -> [dict, str | bool]:
    with Session(db_engine) as session:
        # validate if raffle exists
        exists_raffle = (
            session.query(RaffleModel)
            .filter_by(name=name, user_id=user_id, chat_id=chat_id)
            .first()
        )

        if exists_raffle:
            session.close()
            return {
                "status": False,
                "msg": "Erro ao criar a rifa, nome da rifa já foi usado!",
            }

        else:
            data = sanitize_xss(
                name=name,
                user_id=user_id,
                chat_id=chat_id,
                username=username,
                publishers=publishers,
                numbers=numbers,
                marked_numbers=marked_numbers,
            )

            data["numbers"] = int(numbers)

            raffle = RaffleModel(**data)
            session.add(raffle)

        try:
            session.commit()
            session.close()
            return {"status": True, "msg": "Rifa criada com sucesso!"}
        except Exception as err:
            session.rollback()
            print(f"Erro to create raffle {err}")
            session.close()
            return {
                "status": False,
                "msg": "Erro ao criar a rifa",
            }
