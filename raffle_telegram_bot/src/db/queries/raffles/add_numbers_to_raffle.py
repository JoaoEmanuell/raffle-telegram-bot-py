from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine
from src.utils import sanitize_xss


def add_numbers_to_raffle(
    name: str,
    username: str,
    chat_id: str,
    publisher: str,
    new_marked_numbers: str = None,
):
    chat_id = str(chat_id)

    with Session(db_engine) as session:
        saved_raffle = (
            session.query(RaffleModel)
            .filter_by(name=name, chat_id=chat_id, username=username)
            .first()
        )

        if saved_raffle:
            saved_raffle_chat_id = str(saved_raffle.chat_id)
            saved_raffle_publishers = str(saved_raffle.publishers).split(" ")
            saved_raffle_publishers.append(
                saved_raffle.username
            )  # add the owner of raffle

            # Validate if raffle belongs to chat
            if saved_raffle_chat_id != chat_id:
                return {"status": False, "msg": "Rifa não pertence ao chat"}
            # Validate if publisher have permission to add numbers to raffle
            elif publisher not in saved_raffle_publishers:
                return {
                    "status": False,
                    "msg": f"Você não pode adicionar números a essa rifa!",
                }

            # add
            saved_raffle.marked_numbers = new_marked_numbers.strip()

        else:
            return {"status": False, "msg": f"Rifa não existe"}

        try:
            session.commit()
        except Exception as err:
            session.rollback()
            print(f"Erro to add number to raffle {err}")
            return {"status": False, "msg": f"Erro no servidor ao atualizar a rifa!"}
        finally:
            session.close()
            return {"status": True, "msg": f"Rifa editada com sucesso!"}
