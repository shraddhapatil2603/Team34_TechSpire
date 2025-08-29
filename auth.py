import streamlit as st
import mysql.connector
from db import get_db_connection
import bcrypt

def register_user(username, email, password, user_type):
    conn = get_db_connection()
    cursor = conn.cursor()
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    try:
        cursor.execute("INSERT INTO users (username, email, password, user_type) VALUES (%s, %s, %s, %s)",
                       (username, email, hashed_pw.decode('utf-8'), user_type))
        conn.commit()
    except mysql.connector.Error as err:
        st.error(f"Database error: {err}")
    finally:
        conn.close()

# Login existing user
def login_user(email, password):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()
    conn.close()
    if user:
        if bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
            return user
    return None