import streamlit as st
import re
from skills import SKILLS_DICTIONARY
from skills import CERTIFICATION_PATTERNS
from skills import STOP_WORDS, SHORT_SKILLS

def calculate_skill_match(applicant_skills, job_skills):
    if not applicant_skills or not job_skills:
        return 0.0

    def normalize_skills(skill_str):
        skills = set()
        for skill in re.split(r',|\n|;|/|\(|\)', skill_str):
            skill = re.sub(r'[^\w\s]', '', skill).lower().strip()
            if skill and (len(skill) > 1 or skill in {'r', 'c', 'c++'}) and skill not in STOP_WORDS:
                skills.add(skill)
        return skills

    def score_matches(applicant_set, job_set):
        used_app_skills = set()
        used_job_skills = set()
        match_details = []
        total_score = 0

        ALLOWED_SHORT_SKILLS = {"r", "c", "c++", "go"}

        # 1. Exact matches
        for job_skill in job_set:
            if job_skill in applicant_set and job_skill not in used_job_skills:
                total_score += 1.0
                match_details.append({
                    "job_skill": job_skill,
                    "match": f"Exact match: {job_skill}",
                    "score": 1.0
                })
                used_job_skills.add(job_skill)
                used_app_skills.add(job_skill)

        # 2. Partial substring matches
        for job_skill in job_set:
            if job_skill in used_job_skills:
                continue

            for app_skill in applicant_set:
                if app_skill in used_app_skills:
                    continue

                if (len(job_skill) >= 3 and len(app_skill) >= 3) or \
                   (job_skill in ALLOWED_SHORT_SKILLS or app_skill in ALLOWED_SHORT_SKILLS):

                    if job_skill == app_skill:
                        total_score += 1.0
                        match_details.append({
                            "job_skill": job_skill,
                            "match": f"Exact match: {app_skill}",
                            "score": 1.0
                        })
                        used_job_skills.add(job_skill)
                        used_app_skills.add(app_skill)
                        break

                    elif job_skill in app_skill or app_skill in job_skill:
                        total_score += 0.8
                        match_details.append({
                            "job_skill": job_skill,
                            "match": f"Partial match: {app_skill} contains {job_skill}",
                            "score": 0.8
                        })
                        used_job_skills.add(job_skill)
                        used_app_skills.add(app_skill)
                        break

        # 3. Synonym matching
        synonym_matches = {
            "android": "android sdk",
            "java": "java",
            "git": "github",
            "ci/cd": "continuous integration",
            "ml": "machine learning",
            "oop": "object oriented programming",
            "rest api": "rest apis",  # Added mapping for variations
            "rest apis": "rest api"    # Added mapping for variations
        }

        for job_skill in job_set:
            if job_skill in used_job_skills:
                continue

            for app_skill in applicant_set:
                if app_skill in used_app_skills:
                    continue

                if app_skill in synonym_matches:
                    synonym = synonym_matches[app_skill]
                    if synonym == job_skill or synonym in job_skill or job_skill in synonym:
                        total_score += 0.7
                        match_details.append({
                            "job_skill": job_skill,
                            "match": f"Synonym match: {app_skill} → {synonym}",
                            "score": 0.7
                        })
                        used_job_skills.add(job_skill)
                        used_app_skills.add(app_skill)
                        break

        return total_score, len(job_set), match_details

    applicant_set = normalize_skills(applicant_skills)
    job_set = normalize_skills(job_skills)

    if not job_set:
        return 0.0

    total_score, max_score, match_details = score_matches(applicant_set, job_set)
    if max_score == 0:
        return 0.0

    match_percentage = (total_score / max_score) * 100

    with st.expander("🔍 Detailed Matching Analysis"):
        st.write("### Normalized Applicant Skills")
        st.write(applicant_set)
        st.write("### Normalized Job Skills")
        st.write(job_set)
        st.write("### Match Breakdown")
        if match_details:
            for detail in match_details:
                st.write(f"- {detail['match']} → **+{detail['score']}**")
        else:
            st.warning("No matches found")

        st.write(f"**Total Score:** {total_score:.1f}/{max_score}")
        st.write(f"**Match Percentage:** {match_percentage:.2f}%")

    return round(match_percentage, 2)
