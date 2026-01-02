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
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- ==============================
-- USER KEYS (Asimetrik Anahtarlar)
-- ==============================
CREATE TABLE IF NOT EXISTS user_keys (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    public_key TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- ==============================
-- MESSAGES
-- ==============================
CREATE TABLE IF NOT EXISTS messages (
    id INT AUTO_INCREMENT PRIMARY KEY,
    sender_id INT NOT NULL,
    receiver_id INT NOT NULL,
    encrypted_message TEXT NOT NULL,
    encrypted_sym_key TEXT NOT NULL,
    signature TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (sender_id)
        REFERENCES users(id)
        ON DELETE CASCADE,
    FOREIGN KEY (receiver_id)
        REFERENCES users(id)
        ON DELETE CASCADE
);

-- In addition, these are the codes I used to work on tables

ALTER TABLE users
ADD public_key BLOB,
ADD private_key BLOB;

ALTER TABLE users
ADD key_salt BLOB,
ADD key_iv BLOB;

ALTER TABLE messages
CHANGE encrypted_sym_key encrypted_aes_key BLOB NOT NULL;

ALTER TABLE messages
ADD COLUMN iv BLOB NOT NULL,
ADD COLUMN message_hash BINARY(32) NOT NULL;

-- SELECT * FROM users;
-- SELECT * FROM messages;
-- SHOW CREATE TABLE messages;

ALTER TABLE messages
MODIFY encrypted_message BLOB NOT NULL,
MODIFY encrypted_aes_key BLOB NOT NULL,
MODIFY iv BLOB NOT NULL,
MODIFY signature BLOB NOT NULL;

