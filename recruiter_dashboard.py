import streamlit as st
import pandas as pd
from db import get_db_connection
from recruiter_resume_analyzer import get_ranked_resumes_for_job
from analytics import show_analytics_for_job
import smtplib

def send_email(to_email, subject, message):
    try:
        sender_email = "chobhetushar27@gmail.com"
        sender_password = "zvfo jdum vdlx dhks"
        smtp_server = "smtp.gmail.com"
        smtp_port = 587

        email_message = f"Subject: {subject}\n\n{message}"

        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls()
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, to_email, email_message)

        return True
    except Exception as e:
        print(f"Error sending email: {e}")
        return False

def show_recruiter_dashboard(user):
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #2c3e50; margin-bottom: 0.5rem;'>Welcome, Recruiter {user['username']} 👔</h2>
            <p style='color: #7f8c8d; margin-bottom: 0;'>Manage your job postings and analyze candidate resumes</p>
        </div>
    """, unsafe_allow_html=True)

    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    
    # Top toggle for creating new job
    top_left, top_right = st.columns([4, 1])
    with top_left:
        if st.button("➕ Create New Job Posting", key="toggle_post_form"):
            st.session_state["show_job_form"] = not st.session_state.get("show_job_form", False)

    # Show form if toggle is enabled
    if st.session_state.get("show_job_form", False):
        st.markdown("### 📝 Job Details")
        with st.form("new_job_form", clear_on_submit=True):
            job_title = st.text_input("Position Title*", placeholder="e.g. Senior Python Developer")
            job_description = st.text_area(
                "Job Description*", 
                placeholder="Describe the role, responsibilities, and requirements...",
                height=200
            )
            job_skills = st.text_area(
                "Required Skills*", 
                placeholder="List key skills separated by commas (e.g. Python, SQL, Machine Learning)",
                help="Be specific about technologies and experience levels required"
            )

            submit_col, _ = st.columns([1, 3])
            with submit_col:
                if st.form_submit_button("📤 Post Job", use_container_width=True):
                    if not (job_title and job_description and job_skills):
                        st.error("Please fill all required fields!")
                    else:
                        cursor.execute("""
                            INSERT INTO job_descriptions (user_id, title, description, skills)
                            VALUES (%s, %s, %s, %s)
                        """, (user['user_id'], job_title, job_description, job_skills))
                        conn.commit()
                        st.success("✅ Job posted successfully!")
                        st.experimental_rerun()

    # Fetch jobs first
    cursor.execute("""
        SELECT job_id, title, description, skills, upload_date 
        FROM job_descriptions 
        WHERE user_id = %s
        ORDER BY upload_date DESC
    """, (user['user_id'],))
    jobs = cursor.fetchall()

    if not jobs:
        st.info("You have not posted any jobs yet.")
        conn.close()
        return

    # Prepare dropdown for job selection
    job_titles = [job['title'] for job in jobs]
    job_map = {job['title']: job for job in jobs}

    # Select job
    selected_job_title = st.selectbox("Select a job to view/edit applicants", job_titles)
    selected_job = job_map[selected_job_title]

    # Place button in top-right using columns
    top_left, top_right = st.columns([4, 1])
    with top_right:
        if st.button("📊 Show Analytics", key="show_analytics_btn"):
            st.session_state["show_analytics"] = not st.session_state.get("show_analytics", False)

    # Show analytics only if toggled
    if st.session_state.get("show_analytics", False):
        show_analytics_for_job(selected_job['job_id'])

    # Editable Job Info
    col1, col2 = st.columns([3, 1])
    with col1:
        new_title = st.text_input("Job Title", value=selected_job['title'], key=f"title_{selected_job['job_id']}")
        new_description = st.text_area("Job Description", value=selected_job['description'], key=f"desc_{selected_job['job_id']}", height=150)
        new_skills = st.text_area("Required Skills", value=selected_job['skills'], key=f"skills_{selected_job['job_id']}")
    with col2:
        st.markdown("### Job Metadata")
        upload_date_str = selected_job['upload_date'].strftime("%Y-%m-%d %H:%M") if selected_job['upload_date'] else 'N/A'
        st.markdown(f"**Posted:** {upload_date_str}")
        st.markdown(f"**Job ID:** {selected_job['job_id']}")

        if st.button("💾 Save", key=f"save_{selected_job['job_id']}", use_container_width=True):
            cursor.execute("UPDATE job_descriptions SET title = %s, description = %s, skills = %s WHERE job_id = %s AND user_id = %s",
                            (new_title, new_description, new_skills, selected_job['job_id'], user['user_id']))
            conn.commit()
            st.success("Job updated successfully!")
            st.experimental_rerun()

        if st.button("❌ Delete", key=f"delete_{selected_job['job_id']}", use_container_width=True):
            cursor.execute("DELETE FROM job_descriptions WHERE job_id = %s AND user_id = %s", (selected_job['job_id'], user['user_id']))
            conn.commit()
            st.warning("Job deleted successfully!")
            st.experimental_rerun()

    st.markdown("---")
    st.markdown(f"### 📄 Applicants for {selected_job_title}")
    
    # Get ranked resumes
    ranked_resumes = get_ranked_resumes_for_job(selected_job['job_id'])
    
    # CSV export
    if st.button("📥 Export to CSV", key=f"export_{selected_job['job_id']}", use_container_width=True):
            df = pd.DataFrame(ranked_resumes)
            df = df.drop(columns=["resume_id", "extracted_text"], errors="ignore")
            csv = df.to_csv(index=False)
            st.download_button(
                label="Download CSV",
                data=csv,
                file_name=f"applicants_{selected_job['job_id']}.csv",
                mime="text/csv",
                use_container_width=True
            )
            
    if ranked_resumes:
        top_match = max(res['match_percent'] for res in ranked_resumes)
        avg_match = sum(res['match_percent'] for res in ranked_resumes) / len(ranked_resumes)

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Applicants", len(ranked_resumes))
        col2.metric("Top Match", f"{top_match}%")
        col3.metric("Average Match", f"{avg_match:.1f}%")

        for idx, res in enumerate(ranked_resumes):
            with st.container():
                # Create a card-like container
                st.markdown(f"""
                    <div style='background-color: #ffffff; border-radius: 10px; padding: 1rem; margin: 0.5rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                        <div style='display: flex; justify-content: space-between; align-items: center;'>
                            <h4 style='margin: 0;'>#{idx + 1} {res['file_name']}</h4>
                        </div>
                        <div style='margin: 0.5rem 0;'>
                            <p style='margin: 0.2rem 0;'><strong>Applicant:</strong> {res.get('extracted_name', 'N/A')}</p>
                            <p style='margin: 0.2rem 0;'><strong>Email:</strong> {res.get('extracted_email', 'N/A')}</p>
                            <p style='margin: 0.2rem 0;'><strong>Applied On:</strong> {res['upload_time']}</p>
                        </div>
                        <div style='background-color: #f5f5f5; padding: 0.5rem; border-radius: 5px; margin-top: 0.5rem;'>
                            <p style='margin: 0;'><strong>Skills:</strong> {res.get('extracted_skills', 'N/A')}</p>
                        </div>
                    </div>
                """, unsafe_allow_html=True)

                # Right-aligned section for match percentage and buttons
                color = '#4CAF50' if res['match_percent'] > 75 else '#FFC107' if res['match_percent'] > 50 else '#F44336'
                st.markdown(f"""
                    <div style='font-size: 1.5rem; font-weight: bold; color: {color}; text-align: center; margin: 0.5rem 0;'>
                        {res['match_percent']}% Match
                    </div>
                """, unsafe_allow_html=True)

                # Action buttons in a single row below the match percentage
                btn_col1, btn_col2 = st.columns(2)
                with btn_col1:
                    if st.button(f"📧 Contact", key=f"contact_{res.get('resume_id', idx)}", use_container_width=True):
                        st.session_state['contact_applicant'] = res
                        st.session_state['contact_applicant_id'] = res.get('resume_id', idx)
                        st.experimental_rerun()
                with btn_col2:
                    if st.button(f"🗑️ Remove", key=f"delete_{res.get('resume_id', idx)}", use_container_width=True):
                        cursor.execute("DELETE FROM recruiter_resumes WHERE id = %s", (res['id'],))
                        conn.commit()
                        st.success(f"Deleted resume: {res['file_name']}")
                        st.experimental_rerun()

                # Show contact form only for this candidate if clicked
                if 'contact_applicant_id' in st.session_state and st.session_state['contact_applicant_id'] == res.get('resume_id', idx):
                    st.markdown("---")
                    st.markdown("#### ✉️ Contact Form")
                    with st.form(f"contact_form_{res.get('resume_id', idx)}"):
                        subject = st.text_input("Subject", value=f"Regarding your application for {selected_job_title}")
                        message = st.text_area("Message", height=100)
                        
                        if st.form_submit_button("Send Message"):
                            to_email = res.get('extracted_email')
                            if to_email:
                                success = send_email(to_email, subject, message)
                                if success:
                                    st.success(f"✅ Message sent to {to_email}")
                                    del st.session_state['contact_applicant']
                                    del st.session_state['contact_applicant_id']
                                    st.experimental_rerun()
                                else:
                                    st.error("❌ Failed to send email.")
                            else:
                                st.error("No email address found for this applicant.")
                        
                        if st.form_submit_button("Cancel"):
                            del st.session_state['contact_applicant']
                            del st.session_state['contact_applicant_id']
                            st.experimental_rerun()

                st.markdown("---")
    else:
        st.info("No applicants yet for this position.")

    conn.close()