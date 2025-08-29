import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from db import get_db_connection

def show_analytics_for_job(job_id):
    st.markdown("## 📊 Resume Analytics")

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Fetch resumes for the selected job
    cursor.execute("""
        SELECT id, file_name, match_percent, extracted_skills, upload_time 
        FROM recruiter_resumes 
        WHERE job_id = %s
    """, (job_id,))
    resumes = cursor.fetchall()
    conn.close()

    if not resumes:
        st.info("No resumes uploaded yet for this job.")
        return

    # Create DataFrame
    df = pd.DataFrame(resumes)

    # ----- 1. Bar Chart: Resume Match Percentage -----
    st.subheader("📶 Resume Match Percentage")
    fig, ax = plt.subplots(figsize=(8, 4))
    ax.bar(df['file_name'], df['match_percent'], color='skyblue')
    ax.set_xlabel("Resume File")
    ax.set_ylabel("Match %")
    ax.set_title("Resume Match Percentage")
    ax.set_xticklabels(df['file_name'], rotation=45, ha='right')
    st.pyplot(fig)

    # ----- 2. Pie Chart: Top Extracted Skills Distribution -----
    st.subheader("🧠 Skill Distribution (Extracted)")
    skill_list = []
    for skills in df['extracted_skills']:
        if skills:
            skill_list.extend([s.strip().lower() for s in skills.split(",")])
    skill_counts = pd.Series(skill_list).value_counts().nlargest(5)

    if not skill_counts.empty:
        fig2, ax2 = plt.subplots()
        ax2.pie(skill_counts.values, labels=skill_counts.index, autopct='%1.1f%%', startangle=140)
        ax2.set_title("Top 5 Extracted Skills")
        st.pyplot(fig2)
    else:
        st.warning("No skill data found in resumes.")

    # ----- 3. Time Series: Resume Submission Over Time -----
    st.subheader("📆 Resume Submission Over Time")
    df['upload_time'] = pd.to_datetime(df['upload_time'])
    time_series = df.groupby(df['upload_time'].dt.date).size()

    fig3, ax3 = plt.subplots()
    ax3.plot(time_series.index, time_series.values, marker='o', color='green')
    ax3.set_title("Resume Uploads Over Time")
    ax3.set_xlabel("Date")
    ax3.set_ylabel("Number of Resumes")
    ax3.xaxis.set_major_formatter(mdates.DateFormatter('%b %d'))
    ax3.grid(True)
    st.pyplot(fig3)

