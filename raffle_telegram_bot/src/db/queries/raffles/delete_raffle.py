from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine


def delete_raffle(
    name: str,
    user_id: str,
    chat_id: str,
) -> [dict, str | bool]:
    with Session(db_engine) as session:
        # validate if raffle exists
        raffle = (
            session.query(RaffleModel)
            .filter_by(name=name, user_id=user_id, chat_id=chat_id)
            .first()
        )

        if raffle:
            # validate if raffle belongs to user
            if not raffle.user_id != user_id or not raffle.chat_id != chat_id:
                session.close()
                return {"status": False, "msg": "Rifa não pertence ao usuário"}
            else:
                session.delete(raffle)
        else:
            session.close()
            return {"status": False, "msg": "Rifa não existe"}

        try:
            session.commit()
            session.close()
            return {"status": True, "msg": "Rifa deletada com sucesso!"}
        except Exception as err:
            session.rollback()
            print(f"Erro to delete raffle {err}")
            session.close()
            return {
                "status": False,
                "msg": "Erro ao deletar a rifa",
            }
