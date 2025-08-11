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
INSERT INTO users (username, password, role) VALUES
('admin_user', 'adminpass', 'admin'),
('bidder_1', 'bidderpass1', 'bidder'),
('bidder_2', 'bidderpass2', 'bidder'),
('ppra_officer', 'pprapass', 'ppra');

ALTER TABLE purchase.users
ADD COLUMN password_hash VARCHAR(255);
