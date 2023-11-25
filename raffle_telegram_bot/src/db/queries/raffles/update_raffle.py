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
    data = sanitize_xss(
        name=new_name,
        username=new_username,
        publishers=new_publishers,
        numbers=new_numbers,
        marked_numbers=new_marked_numbers,
    )

    data["numbers"] = int(new_numbers)

    with Session(db_engine) as session:
        saved_raffle = session.query(RaffleModel).filter_by(name=name).first()

        if saved_raffle:
            # Validate if raffle belongs to chat
            if not saved_raffle.chat_id != chat_id:
                return {"status": False, "msg": "Rifa não pertence ao chat"}
            # Validate if raffle belong to user
            elif not saved_raffle.user_id != user_id:
                raise Exception(f"Error, raffle does not belong to ${data['username']}")

            for k, v in data.items():
                if str(v) == "None":  # value is empty
                    pass
                else:
                    saved_raffle.__setattr__(k, v)

        try:
            session.commit()
        except Exception as err:
            session.rollback()
            print(f"Erro to update raffle {err}")
        finally:
            session.close()
