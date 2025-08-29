-- USERS TABLE
Create database ats;
use ats;
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100),
    email VARCHAR(100) UNIQUE,
    password VARCHAR(255),
    role ENUM('applicant', 'recruiter') NOT NULL
);

-- JOBS TABLE
CREATE TABLE jobs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    recruiter_id INT,
    title VARCHAR(255),
    description TEXT,
    required_skills TEXT,
    FOREIGN KEY (recruiter_id) REFERENCES users(id)
);

-- RESUMES TABLE
CREATE TABLE resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT,
    job_id INT,
    file_name VARCHAR(255),
    uploaded_on TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    matched_skills TEXT,
    match_percentage FLOAT,
    FOREIGN KEY (applicant_id) REFERENCES users(id),
    FOREIGN KEY (job_id) REFERENCES jobs(id)
);

show tables;

