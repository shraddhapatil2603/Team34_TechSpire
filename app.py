import streamlit as st
import pandas as pd
import io
import mysql.connector
import bcrypt
import re
from pdfminer.high_level import extract_text
import docx2txt
import os
from skills import SKILLS_DICTIONARY
from skills import CERTIFICATION_PATTERNS
from skills import STOP_WORDS
from auth import login_user, register_user
from db import get_db_connection
from extraction import extract_email, extract_resume_fields, extract_phone, extract_name, extract_section, extract_skills_and_certs
from skills_match import calculate_skill_match
from save_in_db import save_job_description_to_db, save_resume_details_to_db
from recruiter_resume_analyzer import save_recruiter_resume, get_ranked_resumes_for_job
from recruiter_dashboard import show_recruiter_dashboard
from applicant_dashboard import show_applicant_dashboard

# Custom CSS for styling
st.markdown("""
    <style>
        .main {
            background-color: #f8f9fa;
        }
        .sidebar .sidebar-content {
            background-color: #343a40;
            color: white;
        }
        .sidebar .sidebar-content .stSelectbox, 
        .sidebar .sidebar-content .stTextInput,
        .sidebar .sidebar-content .stButton button {
            color: #343a40;
        }
        .stButton button {
            background-color: #4CAF50;
            color: white;
            border-radius: 5px;
            padding: 0.5rem 1rem;
            border: none;
        }
        .stButton button:hover {
            background-color: #45a049;
        }
        .stTextInput input, .stSelectbox select {
            border-radius: 5px;
            border: 1px solid #ced4da;
        }
        .stMarkdown h1, .stMarkdown h2, .stMarkdown h3 {
            color: #2c3e50;
        }
        .success-box {
            background-color: #d4edda;
            color: #155724;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .error-box {
            background-color: #f8d7da;
            color: #721c24;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .info-box {
            background-color: #d1ecf1;
            color: #0c5460;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
        .warning-box {
            background-color: #fff3cd;
            color: #856404;
            padding: 1rem;
            border-radius: 5px;
            margin: 1rem 0;
        }
    </style>
""", unsafe_allow_html=True)

# Initialize session state keys safely
if 'user' not in st.session_state:
    st.session_state['user'] = None
if 'upload_new' not in st.session_state:
    st.session_state['upload_new'] = False

# Streamlit app UI starts here
st.title("🚀 ATS - Applicant Tracking System")
st.markdown("---")

# Sidebar with enhanced styling
with st.sidebar:
    st.markdown("<h2 style='color: white;'>Navigation</h2>", unsafe_allow_html=True)
    
    # If user is logged in, show user info at top
    if st.session_state['user']:
        st.markdown(f"""
            <div style='background-color: #495057; padding: 1rem; border-radius: 5px; margin-bottom: 1rem;'>
                <p style='color: white; margin: 0;'>Logged in as:</p>
                <p style='color: #4CAF50; font-weight: bold; margin: 0;'>{st.session_state['user']['username']}</p>
                <p style='color: #adb5bd; margin: 0;'>{st.session_state['user']['user_type'].capitalize()}</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.button("🚪 Logout", key='logout_button', help="Click to logout from current session"):
            st.session_state.clear()
            st.success("You have been logged out.")
            st.experimental_rerun()
            
        st.markdown("---")
    
    # Menu options
    menu_options = ['Home', 'Login', 'Register']
    if st.session_state['user']:
        menu_options = ['Home']  # Only show Home when logged in
        
    choice = st.selectbox(
        'Menu',
        menu_options,
        key='sidebar_menu_select',
        label_visibility="collapsed"
    )

# Home Page
if choice == 'Home':
    st.markdown("<h2 style='text-align: center;'>Welcome to the ATS Project</h2>", unsafe_allow_html=True)
    
    if st.session_state['user']:
        st.markdown(f"""
            <div class='info-box'>
                <p>Logged in as: <strong>{st.session_state['user']['username']}</strong> ({st.session_state['user']['user_type']})</p>
            </div>
        """, unsafe_allow_html=True)
        
        if st.session_state['user']['user_type'] == 'applicant':
            st.markdown("## 👤 Applicant Dashboard")
            show_applicant_dashboard(st.session_state['user'])
            
        elif st.session_state['user']['user_type'] == 'recruiter':
            st.markdown("## 👔 Recruiter Dashboard")
            show_recruiter_dashboard(st.session_state['user'])
    else:
        st.markdown("""
            <div class='warning-box'>
                <p>You are not logged in. Please login or register to access all features.</p>
            </div>
        """, unsafe_allow_html=True)
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown("### For Applicants")
            st.markdown("""
                - Upload and analyze your resume
                - Get job matching scores
                - Track your applications
            """)
            
        with col2:
            st.markdown("### For Recruiters")
            st.markdown("""
                - Post new job descriptions
                - Analyze applicant resumes
                - Rank candidates based on skills match
            """)

# Registration Page
elif choice == 'Register':
    st.markdown("<h2 style='text-align: center;'>Create New Account</h2>", unsafe_allow_html=True)
    
    with st.form("registration_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            username = st.text_input("👤 Username", placeholder="Enter your username")
            email = st.text_input("📧 Email", placeholder="Enter your email")
            
        with col2:
            password = st.text_input("🔑 Password", type='password', placeholder="Create a password")
            user_type = st.selectbox("👥 User Type", ["applicant", "recruiter"], help="Select 'applicant' if you're job seeking, 'recruiter' if you're hiring")
            
        submit_button = st.form_submit_button("Register Account")
        
        if submit_button:
            if username and email and password:
                register_user(username, email, password, user_type)
                st.markdown("""
                    <div class='success-box'>
                        <p>User registered successfully! You can now log in.</p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class='error-box'>
                        <p>Please fill in all fields.</p>
                    </div>
                """, unsafe_allow_html=True)

# Login Page
elif choice == 'Login':
    if st.session_state['user']:
        st.markdown(f"""
            <div class='success-box'>
                <p>Already logged in as <strong>{st.session_state['user']['username']}</strong> ({st.session_state['user']['user_type']}).</p>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center;'>Login to Your Account</h2>", unsafe_allow_html=True)
        
        with st.form("login_form"):
            email = st.text_input("📧 Email", placeholder="Enter your registered email")
            password = st.text_input("🔑 Password", type='password', placeholder="Enter your password")
            
            submit_button = st.form_submit_button("Login")
            
            if submit_button:
                user = login_user(email, password)
                if user:
                    st.session_state['user'] = user
                    st.markdown(f"""
                        <div class='success-box'>
                            <p>Welcome <strong>{user['username']}</strong>! You are logged in as {user['user_type']}.</p>
                        </div>
                    """, unsafe_allow_html=True)
                    st.session_state['upload_new'] = False
                    st.experimental_rerun()
                else:
                    st.markdown("""
                        <div class='error-box'>
                            <p>Invalid email or password.</p>
                        </div>
                    """, unsafe_allow_html=True)