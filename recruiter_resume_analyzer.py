import io
import logging
from pdfminer.high_level import extract_text
import docx2txt
from extraction import extract_resume_fields
from skills_match import calculate_skill_match
from db import get_db_connection

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def save_recruiter_resume(job_id, uploaded_file, job_skills):
    """
    This function is now maintained for backward compatibility only.
    Actual resume saving is handled in applicant_dashboard.py
    """
    return None  # Since applicants now upload through their dashboard

def get_ranked_resumes_for_job(job_id):
    """
    Get ranked resumes for a job with applicant information
    Returns: List of dictionaries with resume data including applicant info
    """
    conn = get_db_connection()
    try:
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                r.id,
                r.job_id,
                r.file_name,
                r.match_percent,
                r.extracted_text,
                r.extracted_skills,
                r.extracted_name,
                r.extracted_email,
                r.upload_time,
                u.username as applicant_username,
                u.user_id as applicant_id
            FROM recruiter_resumes r
            LEFT JOIN users u ON r.applicant_id = u.user_id
            WHERE r.job_id = %s
            ORDER BY r.match_percent DESC, r.upload_time DESC
        """, (job_id,))
        
        resumes = cursor.fetchall()
        
        # Convert datetime objects to strings for display
        for resume in resumes:
            if 'upload_time' in resume and resume['upload_time']:
                resume['upload_time'] = resume['upload_time'].strftime("%Y-%m-%d %H:%M")
        
        return resumes
    except Exception as e:
        logger.error(f"Error fetching resumes for job {job_id}: {str(e)}")
        return []
    finally:
        conn.close()