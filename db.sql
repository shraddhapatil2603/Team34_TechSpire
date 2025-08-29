create database ats_system;
use ats_system;

CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('applicant', 'recruiter') NOT NULL
);

CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    file_path VARCHAR(255),
    extracted_text TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE job_descriptions (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT,
    job_id INT,
    match_score FLOAT,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id)
);
select * from users;

SHOW CREATE TABLE matches;
-- 🔴 Step 1: Drop foreign key constraint from `matches` to `resumes`
ALTER TABLE matches DROP FOREIGN KEY matches_ibfk_1;

-- 🔴 Step 2: Drop the old `resumes` table
DROP TABLE IF EXISTS resumes;

-- 🔴 Step 3: Recreate the `resumes` table with correct columns
CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    resume_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

drop database ats_system;
create database ats_system;





USE ats_system;

USE ats_system;

-- Step 2: Create users table
CREATE TABLE users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    user_type ENUM('applicant', 'recruiter') NOT NULL
);

-- Step 3: Create job_descriptions table
CREATE TABLE job_descriptions (
    job_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    title VARCHAR(255),
    description TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Step 4: Create matches table (references resumes)
CREATE TABLE matches (
    match_id INT AUTO_INCREMENT PRIMARY KEY,
    resume_id INT,
    job_id INT,
    match_score FLOAT,
    FOREIGN KEY (resume_id) REFERENCES resumes(resume_id),
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id)
);

-- Step 5: Drop foreign key constraint matches_ibfk_1 from matches
ALTER TABLE matches DROP FOREIGN KEY matches_ibfk_1;

-- Step 6: Drop resumes table
DROP TABLE resumes;

-- Step 7: Create resumes table with LONGTEXT resume_text
CREATE TABLE resumes (
    resume_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT,
    resume_text LONGTEXT,
    upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

-- Step 8: Add foreign key constraint back to matches for resumes

select * from job_descriptions;
ALTER TABLE resumes
ADD COLUMN name VARCHAR(255),
ADD COLUMN email VARCHAR(255),
ADD COLUMN phone VARCHAR(50),
ADD COLUMN skills TEXT,
ADD COLUMN education TEXT,
ADD COLUMN experience TEXT;


ALTER TABLE job_descriptions
ADD COLUMN skills TEXT;

ALTER TABLE resumes
ADD COLUMN skills TEXT;

ALTER TABLE job_descriptions
ADD CONSTRAINT fk_recruiter
FOREIGN KEY (recruiter_id) REFERENCES users(user_id)
ON DELETE CASCADE;


ALTER TABLE job_descriptions ADD COLUMN recruiter_id INT;

select * from users;

ALTER TABLE resumes MODIFY skills TEXT;
ALTER TABLE job_descriptions MODIFY skills TEXT;
ALTER TABLE resumes ADD COLUMN certifications TEXT AFTER skills;


CREATE TABLE recruiter_resumes (
    id INT AUTO_INCREMENT PRIMARY KEY,
    job_id INT NOT NULL,
    resume_id INT,
    file_name VARCHAR(255) NOT NULL,
    file_data LONGBLOB NOT NULL,
    extracted_text LONGTEXT,
    extracted_name VARCHAR(255),
    extracted_email VARCHAR(255),
    extracted_skills TEXT,
    match_percent FLOAT,
    upload_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id) ON DELETE CASCADE
);

select * from recruiter_resumes;

ALTER TABLE job_descriptions ADD COLUMN upload_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP;



SHOW TABLES;
select * from users;

CREATE TABLE messages (
    message_id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    job_id INT,
    message TEXT NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id) REFERENCES users(user_id),
    FOREIGN KEY (receiver_id) REFERENCES users(user_id),
    FOREIGN KEY (job_id) REFERENCES job_descriptions(job_id)
);

select*from resumes;

ALTER TABLE recruiter_resumes
ADD COLUMN applicant_id INT,
ADD CONSTRAINT fk_applicant
    FOREIGN KEY (applicant_id) REFERENCES users(user_id)
    ON DELETE SET NULL;
    
ALTER TABLE recruiter_resumes
DROP COLUMN applicant_id;

DROP TABLE resumes;

ALTER TABLE resumes 
ADD COLUMN job_id INT,
ADD COLUMN file_name VARCHAR(255),
ADD UNIQUE KEY unique_resume (user_id, job_id, file_name);

ALTER TABLE resumes 
ADD COLUMN job_id INT,
ADD COLUMN file_name VARCHAR(255),
ADD UNIQUE KEY unique_resume (user_id, job_id, file_name);

ALTER TABLE recruiter_resumes
ADD UNIQUE KEY unique_job_file (job_id, file_name);

DELETE r1 FROM recruiter_resumes r1
JOIN recruiter_resumes r2 
ON r1.job_id = r2.job_id AND r1.file_name = r2.file_name
WHERE r1.resume_id > r2.resume_id;
select * from  recruiter_resumes;

DROP TABLE recruiter_resumes;

ALTER TABLE recruiter_resumes;

SHOW tables;

select * from users;