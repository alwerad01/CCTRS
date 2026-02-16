-- MySQL Schema for Civic Complaint Tracking System
-- This schema can be used if you prefer MySQL over SQLite

CREATE DATABASE IF NOT EXISTS civic_complaints CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE civic_complaints;

-- Departments Table
CREATE TABLE IF NOT EXISTS departments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_name (name)
) ENGINE=InnoDB;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(80) NOT NULL UNIQUE,
    email VARCHAR(120) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'citizen',
    department_id INT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_username (username),
    INDEX idx_role (role),
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE SET NULL,
    CHECK (role IN ('citizen', 'officer', 'admin'))
) ENGINE=InnoDB;

-- Complaints Table
CREATE TABLE IF NOT EXISTS complaints (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    description TEXT NOT NULL,
    citizen_id INT NOT NULL,
    department_id INT NOT NULL,
    assigned_officer_id INT NULL,
    current_status VARCHAR(50) NOT NULL DEFAULT 'Received',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_citizen (citizen_id),
    INDEX idx_department (department_id),
    INDEX idx_status (current_status),
    INDEX idx_created_at (created_at),
    FOREIGN KEY (citizen_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE RESTRICT,
    FOREIGN KEY (assigned_officer_id) REFERENCES users(id) ON DELETE SET NULL,
    CHECK (current_status IN ('Received', 'In Progress', 'Resolved'))
) ENGINE=InnoDB;

-- Status History Table
CREATE TABLE IF NOT EXISTS status_history (
    id INT AUTO_INCREMENT PRIMARY KEY,
    complaint_id INT NOT NULL,
    previous_status VARCHAR(50) NOT NULL,
    new_status VARCHAR(50) NOT NULL,
    changed_by_user_id INT NOT NULL,
    notes TEXT,
    changed_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_complaint (complaint_id),
    INDEX idx_changed_at (changed_at),
    FOREIGN KEY (complaint_id) REFERENCES complaints(id) ON DELETE CASCADE,
    FOREIGN KEY (changed_by_user_id) REFERENCES users(id) ON DELETE CASCADE
) ENGINE=InnoDB;
