import re
from skills import SKILLS_DICTIONARY, CERTIFICATION_PATTERNS, STOP_WORDS

def extract_email(text):
    match = re.search(r'[\w\.-]+@[\w\.-]+', text)
    return match.group(0) if match else None

def extract_phone(text):
    match = re.search(r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}', text)
    return match.group(0) if match else None

def extract_name(text):
    lines = text.strip().split('\n')
    for line in lines:
        if line.strip():
            return line.strip()
    return None

def extract_section(text, section_name):
    lower_text = text.lower()
    lower_section = section_name.lower()
    if lower_section in lower_text:
        parts = lower_text.split(lower_section, 1)
        if len(parts) > 1:
            section = parts[1]
            stop_patterns = ['education', 'experience', 'projects', 'certifications', 'languages', 'profile', 'summary']
            for stop in stop_patterns:
                if stop in section:
                    section = section.split(stop, 1)[0]
            return section.strip()[:1000]
    return None

def extract_skills_and_certs(text):
    text_lower = text.lower()
    found_skills = set()
    found_certs = set()
    debug_info = []

    # Flatten all skills into a set
    all_skills = set()
    for skills in SKILLS_DICTIONARY.values():
        all_skills.update(skills)

    # Priority section search
    priority_sections = ['technical skills', 'skills', 'key skills']
    search_text = None
    for section_name in priority_sections:
        section = extract_section(text, section_name)
        if section:
            search_text = section
            debug_info.append(f"Extracting from section: {section_name}")
            break

    # Fallback to full text
    if not search_text:
        search_text = text_lower
        debug_info.append("No skills section found; scanning full resume.")

    # Remove irrelevant parts
    EXCLUDED_SECTIONS = ['personal details', 'hobbies', 'address', 'interests']
    for section in EXCLUDED_SECTIONS:
        if section in search_text:
            search_text = search_text.split(section, 1)[0]

    # Extract skills
    for skill in all_skills:
        pattern = rf'\b{re.escape(skill)}\b'
        if re.search(pattern, search_text, re.IGNORECASE):
            found_skills.add(skill)
            debug_info.append(f"Skill match: {skill}")

    # Extract certifications
    for pattern in CERTIFICATION_PATTERNS:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            cert = " ".join([m for m in match if m]).strip() if isinstance(match, tuple) else match.strip()
            if cert:
                found_certs.add(cert)
                debug_info.append(f"Certification match: {cert}")

    return {
        'skills': ', '.join(sorted(found_skills)),
        'certifications': ', '.join(sorted(found_certs)),
        'debug': debug_info
    }

def extract_resume_fields(text):
    base_data = {
        'name': extract_name(text),
        'email': extract_email(text),
        'phone': extract_phone(text),
        'education': extract_section(text, 'education'),
        'experience': extract_section(text, 'experience'),
        'full_text': text
    }

    skill_data = extract_skills_and_certs(text)
    return {**base_data, **skill_data}
