-- Create database
CREATE DATABASE IF NOT EXISTS purchase;
USE purchase;

-- Create tenders table
CREATE TABLE IF NOT EXISTS tenders (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    document VARCHAR(255),
    contract_address VARCHAR(100),
    status VARCHAR(20) NOT NULL DEFAULT 'active'
);

-- Create users table (needed for foreign key in bids)
CREATE TABLE IF NOT EXISTS users (
    id INT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL
);

-- Create bids table
CREATE TABLE IF NOT EXISTS bids (
    id INT PRIMARY KEY AUTO_INCREMENT,
    user_id INT NOT NULL,
    tender_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    FOREIGN KEY (tender_id) REFERENCES tenders(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert a sample tender
INSERT INTO tenders (title, description, document, contract_address, status)
VALUES
('Solar Panel Supply', 'Procurement of solar panels for rural schools', 'solar.pdf', '0xabcdefabcdefabcdefabcdefabcdefabcdef', 'active');


-- Insert sample users with roles
INSERT INTO purchase.users (username, password, role) VALUES
('admin_user', 'adminpass', 'admin'),
('bidder_1', 'bidderpass1', 'bidder'),
('bidder_2', 'bidderpass2', 'bidder'),
('ppra_officer', 'pprapass', 'ppra');

DESCRIBE purchase.users;


ALTER TABLE purchase.users
ADD COLUMN password_hash VARCHAR(255);

ALTER TABLE purchase.users MODIFY role VARCHAR(20);



SET SQL_SAFE_UPDATES = 0;
DELETE FROM purchase.users;
SET SQL_SAFE_UPDATES = 1;

INSERT INTO purchase.users (username, email, password_hash, role) VALUES
('admin_user', 'admin@example.com', 'pbkdf2:sha256:260000$Y0Zr1PCO$7d89b89b5...', 'admin'),
('bidder_1', 'bidder1@example.com', 'pbkdf2:sha256:260000$7Ny94XLc$4c72817d...', 'bidder'),
('bidder_2', 'bidder2@example.com', 'pbkdf2:sha256:260000$T7eMfMx7$fa4896ab...', 'bidder'),
('ppra_officer', 'ppra@example.com', 'pbkdf2:sha256:260000$L12lkXja$1e7e72d0...', 'ppra');


ALTER TABLE purchase.tenders
ADD COLUMN po_awarded BOOLEAN DEFAULT FALSE;
