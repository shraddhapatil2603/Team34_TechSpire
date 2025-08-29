import streamlit as st
import os
import docx2txt
from pdfminer.high_level import extract_text
from db import get_db_connection
from extraction import extract_resume_fields
from skills_match import calculate_skill_match

def show_applicant_dashboard(user):
    st.markdown(f"""
        <div style='background-color: #f0f2f6; padding: 1.5rem; border-radius: 10px; margin-bottom: 2rem;'>
            <h2 style='color: #2c3e50; margin-bottom: 0.5rem;'>Welcome back, {user['username']}! 👋</h2>
            <p style='color: #7f8c8d; margin-bottom: 0;'>Ready to find your next opportunity?</p>
        </div>
    """, unsafe_allow_html=True)

    # Job search section
    st.markdown("## 🔍 Job Search")
    with st.container():
        col1, col2 = st.columns([3, 1])
        with col1:
            search_query = st.text_input(
                "Search by job title, skills, or company",
                placeholder="e.g. 'Python Developer' or 'Data Analysis'",
                key="job_search_input"
            )
        with col2:
            st.markdown("<div style='height: 30px;'></div>", unsafe_allow_html=True)
            search_button = st.button("Search", type="primary")

    # Database connection
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    # Search logic
    if search_query or search_button:
        cursor.execute("""
            SELECT jd.job_id, jd.title, jd.skills, jd.description, u.username AS recruiter_name
            FROM job_descriptions jd
            JOIN users u ON jd.user_id = u.user_id
            WHERE jd.title LIKE %s OR jd.skills LIKE %s
            ORDER BY jd.upload_date DESC
        """, (f"%{search_query}%", f"%{search_query}%"))
    else:
        cursor.execute("""
            SELECT jd.job_id, jd.title, jd.skills, jd.description, u.username AS recruiter_name
            FROM job_descriptions jd
            JOIN users u ON jd.user_id = u.user_id
            ORDER BY jd.upload_date DESC
            LIMIT 10
        """)
    
    jobs = cursor.fetchall()
    conn.close()

    if not jobs:
        st.markdown("""
            <div style='background-color: #fff3cd; color: #856404; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                No job listings found matching your criteria. Try different search terms.
            </div>
        """, unsafe_allow_html=True)
        return

    # Job selection dropdown with improved styling
    st.markdown("### 🎯 Select a Job to Analyze")
    job_labels = [f"{job['title']} | Posted by: {job['recruiter_name']}" for job in jobs]
    selected_label = st.selectbox(
        "Available job listings",
        job_labels,
        index=0,
        label_visibility="collapsed",
        key="job_select_box"
    )

    selected_job = next((job for job in jobs if 
                        f"{job['title']} | Posted by: {job['recruiter_name']}" == selected_label), None)

    if selected_job:
        # Job details card
        st.markdown(f"""
            <div style='background-color: #ffffff; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; box-shadow: 0 2px 8px rgba(0,0,0,0.1);'>
                <h3 style='color: #3498db; margin-top: 0;'>{selected_job['title']}</h3>
                <p style='color: #7f8c8d; margin-bottom: 0.5rem;'><strong>Recruiter:</strong> {selected_job['recruiter_name']}</p>
                <div style='margin: 1rem 0;'>
                    <h4 style='margin-bottom: 0.5rem;'>Job Description</h4>
                    <div style='background-color: #f8f9fa; padding: 1rem; border-radius: 8px;'>
                        {selected_job['description']}
                    </div>
                </div>
                <div style='margin: 1rem 0;'>
                    <h4 style='margin-bottom: 0.5rem;'>Required Skills</h4>
                    <div style='background-color: #e8f4fd; padding: 1rem; border-radius: 8px;'>
                        {selected_job['skills']}
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)

        # Resume analysis section
        st.markdown("---")
        st.markdown("## 📊 Resume Match Analysis")
        
        uploaded_file = st.file_uploader(
            "Upload your resume (PDF or DOCX) to check compatibility",
            type=['pdf', 'docx'],
            key=f'resume_uploader_{selected_job["job_id"]}'
        )

        if uploaded_file:
            # Processing animation
            with st.spinner("Analyzing your resume..."):
                # Save temp file
                temp_file_path = f"temp_resume_{user['user_id']}_{selected_job['job_id']}"
                with open(temp_file_path, "wb") as f:
                    f.write(uploaded_file.read())

                # Extract text based on file type
                if uploaded_file.type == 'application/pdf':
                    extracted_text = extract_text(temp_file_path)
                elif uploaded_file.type == 'application/vnd.openxmlformats-officedocument.wordprocessingml.document':
                    extracted_text = docx2txt.process(temp_file_path)
                else:
                    st.error("Unsupported file type.")
                    os.remove(temp_file_path)
                    return

                os.remove(temp_file_path)

                if extracted_text:
                    parsed_data = extract_resume_fields(extracted_text)
                    resume_skills = parsed_data.get('skills', '')
                    applicant_name = parsed_data.get('name', '')
                    applicant_email = parsed_data.get('email', '')

                    match_percent = calculate_skill_match(resume_skills, selected_job['skills'])
                    
                    # Save to database for recruiter view
                    conn = get_db_connection()
                    cursor = conn.cursor()
                    try:
                        cursor.execute("""
                            INSERT INTO recruiter_resumes 
                            (job_id, file_name, match_percent, extracted_text, 
                             extracted_skills, extracted_name, extracted_email, applicant_id)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                            ON DUPLICATE KEY UPDATE
                            match_percent = VALUES(match_percent),
                            extracted_text = VALUES(extracted_text),
                            extracted_skills = VALUES(extracted_skills),
                            extracted_name = VALUES(extracted_name),
                            extracted_email = VALUES(extracted_email)
                        """, (
                            selected_job['job_id'],
                            uploaded_file.name,
                            match_percent,
                            extracted_text,
                            resume_skills,
                            applicant_name,
                            applicant_email,
                            user['user_id']
                        ))
                        conn.commit()
                    except Exception as e:
                        st.error(f"Error saving resume: {str(e)}")
                    finally:
                        conn.close()

                    # Visual match percentage display
                    st.markdown(f"""
                        <div style='background-color: #e8f5e9; border-radius: 10px; padding: 1.5rem; margin: 1rem 0; text-align: center;'>
                            <h3 style='color: #2e7d32; margin-top: 0;'>Compatibility Score</h3>
                            <div style='font-size: 3rem; font-weight: bold; color: #388e3c;'>
                                {match_percent}%
                            </div>
                            <p style='color: #616161;'>
                                Your resume matches <strong>{selected_job['title']}</strong> requirements
                            </p>
                        </div>
                    """, unsafe_allow_html=True)

                    # Submission confirmation
                    st.success("Your resume has been successfully submitted to the recruiter!")
                    st.info("The recruiter will see your application ranked along with other applicants.")

                    # Detailed analysis expander
                    with st.expander("🔍 View detailed analysis"):
                        st.markdown("### Your Skills")
                        st.markdown(f"""
                            <div style='background-color: #e3f2fd; padding: 1rem; border-radius: 8px;'>
                                {resume_skills if resume_skills else "No skills detected"}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        st.markdown("### Required Skills")
                        st.markdown(f"""
                            <div style='background-color: #ffebee; padding: 1rem; border-radius: 8px;'>
                                {selected_job['skills']}
                            </div>
                        """, unsafe_allow_html=True)
                        
                        # Skill matching visualization
                        st.markdown("### Skill Matching Breakdown")
                        
                        # Normalize and deduplicate skills, handling plurals and spacing
                        def normalize_skill(skill):
                            return skill.lower().strip().rstrip('s')  # remove trailing 's' to handle plurals

                        resume_skills_list = list(set([normalize_skill(skill) for skill in resume_skills.split(',') if skill.strip()]))
                        job_skills_list = list(set([normalize_skill(skill) for skill in selected_job['skills'].split(',') if skill.strip()]))

                        matched_skills = []
                        missing_skills = []

                        for job_skill in job_skills_list:
                            # Exact match or substring match in resume skills
                            if job_skill in resume_skills_list or any(job_skill in resume_skill or resume_skill in job_skill for resume_skill in resume_skills_list):
                                matched_skills.append(job_skill)
                            else:
                                missing_skills.append(job_skill)

                        # Convert back to display format, capitalizing each word
                        matched_skills_display = [skill.title() for skill in matched_skills]
                        missing_skills_display = [skill.title() for skill in missing_skills]

                        col1, col2 = st.columns(2)
                        with col1:
                            st.markdown("✅ **Matched Skills**")
                            if matched_skills_display:
                                for skill in matched_skills_display:
                                    st.markdown(f"- {skill}")
                            else:
                                st.markdown("No matched skills found.")

                        with col2:
                            st.markdown("❌ **Missing Skills**")
                            if missing_skills_display:
                                for skill in missing_skills_display:
                                    st.markdown(f"- {skill}")
                            else:
                                st.markdown("No missing skills detected. Great match!")

                        st.markdown("### Suggestions for Improvement")
                        st.info("""
                            - Highlight more of the required skills in your resume
                            - Add specific examples of using these skills
                            - Consider obtaining certifications for missing skills
                        """)
                else:
                    st.error("Failed to extract text from the resume.")

