# Save resume details to DB
import streamlit as st
from db import get_db_connection

def save_resume_details_to_db(user_id, job_id, file_name, data):
    conn = get_db_connection()
    cursor = conn.cursor()

    # Check if same file is already uploaded
    cursor.execute("""
        SELECT resume_id FROM resumes 
        WHERE user_id = %s AND job_id = %s AND file_name = %s
    """, (user_id, job_id, file_name))
    exists = cursor.fetchone()

    save_data = {k: v for k, v in data.items() if k != 'debug'}

    if exists:
        st.warning(f"Resume '{file_name}' already uploaded. Skipping duplicate.")
    else:
        cursor.execute("""
            INSERT INTO resumes (user_id, job_id, file_name, resume_text, name, email, phone, skills, certifications, education, experience)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            user_id, job_id, file_name, save_data['full_text'], save_data['name'], save_data['email'], save_data['phone'],
            save_data['skills'], save_data['certifications'], save_data['education'], save_data['experience']
        ))
        conn.commit()
        st.success(f"Resume '{file_name}' saved successfully!")

    cursor.close()
    conn.close()


# Save job description to DB
def save_job_description_to_db(user_id, title, description, skills):
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO job_descriptions (user_id, title, description, skills)
        VALUES (%s, %s, %s, %s)
    """, (user_id, title, description, skills))
    conn.commit()
    conn.close()
    st.success("Job description saved successfully!")

# Fetch resumes (applicants)
def get_all_resumes():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM resumes")
    resumes = cursor.fetchall()
    conn.close()
    return resumes

# Fetch job descriptions uploaded by recruiter
def get_user_job_descriptions(user_id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM job_descriptions WHERE user_id = %s", (user_id,))
    jobs = cursor.fetchall()
    conn.close()
    return jobs



