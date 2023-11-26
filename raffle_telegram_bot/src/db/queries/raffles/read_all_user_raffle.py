from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine


def read_all_user_raffle(
    user_id: str,
    chat_id: str,
) -> [dict, str | bool]:
    with Session(db_engine) as session:
        # validate if raffle exists
        raffles = session.query(RaffleModel).filter_by(user_id=user_id, chat_id=chat_id)

        if raffles:
            try:
                username = raffles[0].username
            except IndexError:
                session.close()
                return {"status": False, "msg": "Você não possui rifas!"}
            else:
                msg = f"*Rifas de @{username}*\n"
                for raffle in raffles:
                    publishers_list = str(raffle.publishers).split(" ")
                    publishers = [f"@{x} " for x in publishers_list]
                    marked_numbers_list = str(raffle.marked_numbers).split(" ")
                    marked_numbers = [f"{x} " for x in marked_numbers_list]
                    raffle_msg = f"\n\*\*\*\*\n*Rifa:* {raffle.name}\n*Editores:* {publishers}\n*Quantidade:* {raffle.numbers}\n*Números marcados:* {marked_numbers}\n"
                    msg = msg + raffle_msg

        else:
            session.close()
            return {"status": False, "msg": "Você não possui rifas!"}
        try:
            session.close()
            if msg != "":
                return {"status": True, "msg": msg}
            else:
                return {"status": False, "msg": "Você não possui rifas!"}
        except Exception as err:
            session.rollback()
            print(f"Erro to read raffles {err}")
            session.close()
            return {
                "status": False,
                "msg": "Erro ao listar as rifas",
            }
