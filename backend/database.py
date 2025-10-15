# import os
# import logging
# from dotenv import load_dotenv
# import mysql.connector
# from mysql.connector import Error, pooling

# # ------------------- SETUP LOGGING -------------------
# logging.basicConfig(level=logging.INFO)

# # ------------------- LOAD ENV -------------------
# load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

# DB_HOST = os.getenv("DB_HOST", "localhost")
# DB_USER = os.getenv("DB_USER", "root")
# DB_PASSWORD = os.getenv("DB_PASSWORD", "")
# DB_NAME = os.getenv("DB_NAME", "textmorph")

# # ------------------- CONNECTION POOL -------------------
# try:
#     connection_pool = mysql.connector.pooling.MySQLConnectionPool(
#         pool_name="mypool",
#         pool_size=5,
#         pool_reset_session=True,
#         host=DB_HOST,
#         user=DB_USER,
#         password=DB_PASSWORD,
#         database=DB_NAME
#     )
#     logging.info("✅ MySQL connection pool created successfully")
# except Error as e:
#     logging.error(f"❌ Error creating connection pool: {e}")
#     connection_pool = None

# # ------------------- CONNECTION UTILITY -------------------
# def create_connection():
#     if connection_pool is None:
#         logging.error("❌ Connection pool is not initialized")
#         return None
#     try:
#         conn = connection_pool.get_connection()
#         return conn
#     except Error as e:
#         logging.error(f"❌ Error getting connection from pool: {e}")
#         return None

# # ------------------- USER FUNCTIONS -------------------
# def fetch_all_users():
#     conn = create_connection()
#     if not conn:
#         return []
#     try:
#         cursor = conn.cursor(dictionary=True)
#         cursor.execute("SELECT * FROM users")
#         return cursor.fetchall()
#     except Error as e:
#         logging.error(f"❌ Error fetching users: {e}")
#         return []
#     finally:
#         cursor.close()
#         conn.close()

# def delete_user(user_id: int):
#     conn = create_connection()
#     if not conn:
#         return False
#     try:
#         cursor = conn.cursor()
#         cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
#         conn.commit()
#         return cursor.rowcount > 0
#     except Error as e:
#         logging.error(f"❌ Error deleting user: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()

# # ------------------- PASSWORD FUNCTIONS -------------------
# def update_user_password(email: str, hashed_password: str):
#     conn = create_connection()
#     if not conn:
#         return False
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "UPDATE users SET hashed_password=%s WHERE email=%s",
#             (hashed_password, email)
#         )
#         conn.commit()
#         return cursor.rowcount > 0
#     except Error as e:
#         logging.error(f"❌ Error updating password: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()

# # ------------------- TEXT FUNCTIONS -------------------
# def save_generated_text(user_id: int, content_text: str, content_type: str):
#     conn = create_connection()
#     if not conn:
#         return False
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO user_texts (user_id, content_text, content_type) VALUES (%s,%s,%s)",
#             (user_id, content_text, content_type)
#         )
#         conn.commit()
#         return True
#     except Error as e:
#         logging.error(f"❌ Error saving generated text: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()

# # ------------------- FEEDBACK FUNCTIONS -------------------
# def save_user_feedback(user_id: int, feedback_text: str):
#     conn = create_connection()
#     if not conn:
#         return False
#     try:
#         cursor = conn.cursor()
#         cursor.execute(
#             "INSERT INTO user_feedback (user_id, feedback_text) VALUES (%s,%s)",
#             (user_id, feedback_text)
#         )
#         conn.commit()
#         return True
#     except Error as e:
#         logging.error(f"❌ Error saving feedback: {e}")
#         return False
#     finally:
#         cursor.close()
#         conn.close()



import mysql.connector
from mysql.connector import Error
from dotenv import load_dotenv
import os
load_dotenv()  # load .env variables

def create_connection():
    try:
        connection = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASSWORD"),
            database=os.getenv("DB_NAME")
        )
        if connection.is_connected():
            return connection
    except Error as e:
        print(f"Error connecting to MySQL: {e}")
    return None

# --------------------- USERS ---------------------
def fetch_all_users():
    conn = create_connection()
    if conn:
        cursor = conn.cursor(dictionary=True)
        try:
            cursor.execute("SELECT * FROM users")
            return cursor.fetchall()
        except Error as e:
            print(f"Error fetching users: {e}")
            return []
        finally:
            cursor.close()
            conn.close()
    return []

def delete_user(user_id: int):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM users WHERE id=%s", (user_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting user: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --------------------- USER TEXTS ---------------------
def create_user_texts_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_texts (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    content_text TEXT NOT NULL,
                    content_type VARCHAR(20) NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.commit()
        except Error as e:
            print(f"Error creating user_texts table: {e}")
        finally:
            cursor.close()
            conn.close()

def save_generated_text(user_id: int, content_text: str, content_type: str):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_texts (user_id, content_text, content_type) VALUES (%s,%s,%s)",
            (user_id, content_text, content_type)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error saving generated text: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_user_texts():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT ut.id, ut.user_id, u.username, ut.content_text, ut.content_type, ut.created_at
            FROM user_texts ut
            JOIN users u ON u.id = ut.user_id
            ORDER BY ut.created_at DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching user texts: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_user_text(text_id: int):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_texts WHERE id=%s", (text_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting user text: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_user_text_counts():
    conn = create_connection()
    if not conn:
        return {}
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT COUNT(*) as total_users FROM users")
        total_users = cursor.fetchone()["total_users"]

        # for simplicity, assume all users are active
        active_users = total_users

        cursor.execute("SELECT COUNT(*) as total_summaries FROM user_texts WHERE content_type='summary'")
        total_summaries = cursor.fetchone()["total_summaries"]

        cursor.execute("SELECT COUNT(*) as total_paraphrases FROM user_texts WHERE content_type='paraphrase'")
        total_paraphrases = cursor.fetchone()["total_paraphrases"]

        return {
            "total_users": total_users,
            "active_users": active_users,
            "total_summaries": total_summaries,
            "total_paraphrases": total_paraphrases
        }
    except Error as e:
        print(f"Error fetching counts: {e}")
        return {}
    finally:
        cursor.close()
        conn.close()

# --------------------- PASSWORD ---------------------
def update_user_password(email: str, hashed_password: str):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET hashed_password=%s WHERE email=%s", (hashed_password, email))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"MySQL error: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

# --------------------- USER FEEDBACK ---------------------
def create_user_feedback_table():
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    user_id INT NOT NULL,
                    feedback_text TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                )
            """)
            conn.commit()
        except Error as e:
            print(f"Error creating user_feedback table: {e}")
        finally:
            cursor.close()
            conn.close()

def save_user_feedback(user_id: int, feedback_text: str):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user_feedback (user_id, feedback_text) VALUES (%s,%s)",
            (user_id, feedback_text)
        )
        conn.commit()
        return True
    except Error as e:
        print(f"Error saving feedback: {e}")
        return False
    finally:
        cursor.close()
        conn.close()

def fetch_all_feedback():
    conn = create_connection()
    if not conn:
        return []
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT uf.id, uf.feedback_text, uf.created_at, u.username, u.email
            FROM user_feedback uf
            JOIN users u ON uf.user_id = u.id
            ORDER BY uf.created_at DESC
        """)
        return cursor.fetchall()
    except Error as e:
        print(f"Error fetching feedback: {e}")
        return []
    finally:
        cursor.close()
        conn.close()

def delete_feedback(feedback_id: int):
    conn = create_connection()
    if not conn:
        return False
    try:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user_feedback WHERE id=%s", (feedback_id,))
        conn.commit()
        return cursor.rowcount > 0
    except Error as e:
        print(f"Error deleting feedback: {e}")
        return False
    finally:
        cursor.close()
        conn.close()