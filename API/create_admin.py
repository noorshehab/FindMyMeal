import sys
import os
import hashlib
from passlib.context import CryptContext
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

sys.path.append(project_root)

from sqlmodel import Session, select
from DB.db_setup import engine
from DB.models import User

import uuid

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_password(password: str) -> str:
    print(f"DEBUG: Pre-hashing '{password}'...")
    # Step A: SHA-256 (Turns any length into 64 chars)
    safe_password = hashlib.sha256(password.encode('utf-8')).hexdigest()
    print(f"DEBUG: SHA-256 digest is {len(safe_password)} chars long.")
    
    # Step B: Bcrypt (Safe now because input is always 64 chars)
    return pwd_context.hash(safe_password)

def create_super_admin(username, password):
    with Session(engine) as session:
        statement = select(User).where(User.username == username)
        existing_user = session.exec(statement).first()
        
        if existing_user:
            print(f"User {username} already exists. Updating role to Admin...")
            existing_user.role = "admin"
            session.add(existing_user)
            session.commit()
            print("Success!")
            return

        # Create new Admin
        print(f"Creating new Admin: {username}")
        new_admin = User(
            id=str(uuid.uuid4())[:8],
            username=username,
            hashed_password=hash_password(password),
            role="admin" 
        )
        session.add(new_admin)
        session.commit()
        print("Admin created successfully!")

if __name__ == "__main__":
    # Usage: python scripts/create_admin.py <username> <password>
    if len(sys.argv) != 3:
        print("Usage: python scripts/create_admin.py <username> <password>")
    else:
        create_super_admin(sys.argv[1], sys.argv[2])