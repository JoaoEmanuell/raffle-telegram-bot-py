from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine
from src.utils import sanitize_xss


def update_raffle(
    name: str,
    user_id: str,
    chat_id: str,
    new_name: str = None,
    new_username: str = None,
    new_publishers: str = None,
    new_numbers: int = None,
    new_marked_numbers: str = None,
):
    user_id = str(user_id)
    chat_id = str(chat_id)

    data = sanitize_xss(
        name=new_name,
        username=new_username,
        publishers=new_publishers,
        numbers=new_numbers,
        marked_numbers=new_marked_numbers,
    )

    print(data["numbers"])
    if data["numbers"] != "None":
        data["numbers"] = int(new_numbers)

    print(f"UPDATE DATA {data}")

    with Session(db_engine) as session:
        saved_raffle = (
            session.query(RaffleModel)
            .filter_by(name=name, chat_id=chat_id, user_id=user_id)
            .first()
        )

        if saved_raffle:
            saved_raffle_chat_id = str(saved_raffle.chat_id)
            saved_raffle_user_id = str(saved_raffle.user_id)

            # Validate if raffle belongs to chat
            if saved_raffle_chat_id != chat_id:
                return {"status": False, "msg": "Rifa não pertence ao chat"}
            # Validate if raffle belong to user
            elif saved_raffle_user_id != user_id:
                return {"status": False, "msg": f"Rifa não pertence ao usuário"}

            for k, v in data.items():
                if str(v) == "None":  # value is empty
                    pass
                else:
                    saved_raffle.__setattr__(k, v)
        else:
            return {"status": False, "msg": f"Rifa não existe"}

        try:
            session.commit()
        except Exception as err:
            session.rollback()
            print(f"Erro to update raffle {err}")
            return {"status": False, "msg": f"Erro no servidor ao atualizar a rifa!"}
        finally:
            session.close()
            return {"status": True, "msg": f"Rifa editada com sucesso!"}
