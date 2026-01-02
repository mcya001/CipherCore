-- ==============================
-- DATABASE
-- ==============================
CREATE DATABASE IF NOT EXISTS CipherCoreDB
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE CipherCoreDB;

-- ==============================
-- USERS
-- ==============================
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    public_key BLOB NOT NULL,
    private_key BLOB NOT NULL,
    key_salt BLOB NOT NULL,
    key_iv BLOB NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- MESSAGES
-- ==============================
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    encrypted_message BLOB NOT NULL,
    encrypted_aes_key BLOB NOT NULL,
    iv BLOB NOT NULL,
    message_hash BINARY(32) NOT NULL,
    signature BLOB NOT NULL,
    is_read TINYINT(1) DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);
