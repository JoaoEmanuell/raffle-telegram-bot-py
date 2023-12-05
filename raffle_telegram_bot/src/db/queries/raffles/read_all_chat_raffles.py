from sqlalchemy.orm import Session

from ....db import RaffleModel
from src.db.connection import db_engine


def read_all_chat_raffles(
    chat_id: str,
) -> [dict, str | bool]:
    with Session(db_engine) as session:
        # validate if raffle exists
        raffles = session.query(RaffleModel).filter_by(chat_id=chat_id)

        if raffles:
            try:
                username = raffles[0].username
            except IndexError:
                session.close()
                return {"status": False, "msg": "Chat não possui rifas!"}
            else:
                msg = f"*Rifas do chat*\n"
                for raffle in raffles:
                    publishers_list = str(raffle.publishers).split(" ")
                    publishers = [f"@{x} " for x in publishers_list]
                    raffle_msg = f"\n\*\*\*\*\n*Rifa de:* @{raffle.username}\n*Nome:* {raffle.name}\n*Editores:* {publishers}\n*Quantidade:* {raffle.numbers}\n*Números marcados:* {raffle.marked_numbers}\n"
                    msg = msg + raffle_msg

        else:
            session.close()
            return {"status": False, "msg": "Chat não possui rifas!"}
        try:
            session.close()
            if msg != "":
                return {"status": True, "msg": msg}
            else:
                return {"status": False, "msg": "Chat não possui rifas!"}
        except Exception as err:
            session.rollback()
            print(f"Erro to read raffles {err}")
            session.close()
            return {
                "status": False,
                "msg": "Erro ao listar as rifas",
            }
