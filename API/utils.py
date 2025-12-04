from passlib.context import CryptContext
import hashlib

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    passh=hashlib.sha256(password.encode('utf-8')).hexdigest()
    return pwd_context.hash(passh)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    passh=hashlib.sha256(plain_password.encode('utf-8')).hexdigest()
    return pwd_context.verify(passh, hashed_password)