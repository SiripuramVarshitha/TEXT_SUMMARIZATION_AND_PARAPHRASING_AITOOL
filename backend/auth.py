from datetime import datetime, timedelta
from fastapi import HTTPException
from jose import JWTError, jwt
from dotenv import load_dotenv
import os

# Relative import for database connection
from database import create_connection

# ------------------- LOAD ENV -------------------
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ------------------- JWT FUNCTIONS -------------------
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def verify_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if not email:
            return None
        return email
    except JWTError:
        return None

# ------------------- USER FUNCTIONS -------------------
def get_user_by_email(email: str):
    conn = create_connection()
    if not conn:
        return None
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute(
            "SELECT id, username, email, language_preference FROM users WHERE email=%s",
            (email,)
        )
        user = cursor.fetchone()
        return user
    except Exception as e:
        print(f"❌ Error fetching user: {e}")
        return None
    finally:
        cursor.close()
        conn.close()
