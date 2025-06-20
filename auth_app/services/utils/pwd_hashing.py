from passlib.context import CryptContext

from auth_app.config import pwd_settings

pwd_context = CryptContext(
    schemes=[pwd_settings.HASHING_ALGORITHM.get_secret_value()],
    deprecated=[pwd_settings.HASHING_DEPRECATED.get_secret_value()],
)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)
