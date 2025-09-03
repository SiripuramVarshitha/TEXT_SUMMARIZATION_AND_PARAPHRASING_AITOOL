from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from database import get_db_connection, init_db
from auth import hash_password, verify_password, create_access_token
from jose import JWTError, jwt

app = FastAPI()

@app.on_event("startup")
def startup_event():
    init_db()

class SignupRequest(BaseModel):
    name: str
    email: str
    password: str
    role: str = "Student"
    language: str = "English"
    content_type: str = "Articles"

class LoginRequest(BaseModel):
    email: str
    password: str

@app.post("/signup")
def signup(user: SignupRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO users (name, email, password_hash, role, language, content_type)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user.name, user.email, hash_password(user.password), user.role, user.language, user.content_type))
        conn.commit()
    except Exception:
        raise HTTPException(status_code=400, detail="Email already registered")
    finally:
        conn.close()
    return {"message": "User created successfully"}

@app.post("/login")
def login(request: LoginRequest):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (request.email,))
    user = cur.fetchone()
    conn.close()

    if not user or not verify_password(request.password, user["password_hash"]):
        raise HTTPException(status_code=400, detail="Invalid email or password")

    token = create_access_token({"sub": user["email"]})
    return {"access_token": token, "token_type": "bearer"}

SECRET_KEY = "mysecretkey123"
ALGORITHM = "HS256"

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid authorization header")
    
    token = authorization.split(" ")[1]
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    
    # Fetch user from DB
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cur.fetchone()
    conn.close()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return dict(user)

@app.get("/users/me")
def get_profile(current_user: dict = Depends(get_current_user)):
    return current_user

class UpdateProfileRequest(BaseModel):
    name: str
    email: str
    language: str

@app.put("/users/me")
def update_profile(data: UpdateProfileRequest, current_user: dict = Depends(get_current_user)):
    conn = get_db_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            UPDATE users
            SET name = ?, email = ?, language = ?
            WHERE id = ?
        """, (data.name, data.email, data.language, current_user["id"]))
        conn.commit()
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        conn.close()
    return {"message": "Profile updated successfully"}