from os import getenv
from base64 import b64encode

from sqlalchemy import Integer, Column
from sqlalchemy_utils import EncryptedType
from sqlalchemy_utils.types.encrypted.encrypted_type import AesEngine
from sqlalchemy import Unicode
from dotenv import load_dotenv

load_dotenv()

aes_key_str = getenv("AES_KEY")
AES_KEY = b64encode(aes_key_str.encode("ascii"))

from .base import Base


class RaffleModel(Base):
    __tablename__ = "raffle"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5"))  # raffle name
    user_id = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # creator user id
    chat_id = Column(EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5"))  # chat id
    username = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # creator username
    publishers = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # separate with spaces
    numbers = Column(Integer)  # value of the max number
    marked_numbers = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # separate with spaces
    image_base = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # image base with red rectangle to replace with generated image
    image_base_rectangle_positions = Column(
        EncryptedType(Unicode, AES_KEY, AesEngine, "pkcs5")
    )  # positions with rectangle, separate with spaces [x y height width]
