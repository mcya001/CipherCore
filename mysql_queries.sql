-- ==============================
-- CipherCoreDB - VIEWING COMMANDS
-- ==============================
-- This file is for viewing purposes only, it does not modify data
-- Used to inspect and analyze the database

USE CipherCoreDB;

-- ==============================
-- DATABASE INFORMATION
-- ==============================

-- Show current database
SELECT DATABASE();

-- List all tables
SHOW TABLES;

-- Database character set and collation
SHOW CREATE DATABASE CipherCoreDB;

-- ==============================
-- TABLE STRUCTURES
-- ==============================

-- Users table structure
DESCRIBE users;
-- or
SHOW CREATE TABLE users;

-- Messages table structure
DESCRIBE messages;
-- or
SHOW CREATE TABLE messages;

-- Show structure of all tables
SHOW FULL COLUMNS FROM users;
SHOW FULL COLUMNS FROM messages;

-- ==============================
-- VIEW USERS
-- ==============================

-- List all users (without sensitive information)
SELECT 
    id,
    username,
    email,
    created_at,
    LENGTH(public_key) AS public_key_size,
    LENGTH(private_key) AS private_key_size,
    LENGTH(key_salt) AS key_salt_size,
    LENGTH(key_iv) AS key_iv_size
FROM users
ORDER BY created_at DESC;

-- View a specific user (by ID)
SELECT 
    id,
    username,
    email,
    created_at,
    LENGTH(public_key) AS public_key_size,
    LENGTH(private_key) AS private_key_size
FROM users
WHERE id = 1;

-- View a specific user (by email)
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE email = 'user@example.com';

-- Number of users
SELECT COUNT(*) AS total_users FROM users;

-- Recently registered users
SELECT 
    id,
    username,
    email,
    created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;

-- ==============================
-- VIEW MESSAGES
-- ==============================

-- View all messages with sender and receiver details
SELECT 
    m.id,
    sender.username AS sender_username,
    sender.email AS sender_email,
    receiver.username AS receiver_username,
    receiver.email AS receiver_email,
    m.created_at,
    LENGTH(m.encrypted_message) AS message_size,
    LENGTH(m.encrypted_aes_key) AS aes_key_size,
    LENGTH(m.iv) AS iv_size,
    LENGTH(m.message_hash) AS hash_size,
    LENGTH(m.signature) AS signature_size
FROM messages m
JOIN users sender ON m.sender_id = sender.id
JOIN users receiver ON m.receiver_id = receiver.id
ORDER BY m.created_at DESC;

-- Messages sent by a specific user
SELECT 
    m.id,
    receiver.username AS receiver_username,
    receiver.email AS receiver_email,
    m.created_at
FROM messages m
JOIN users receiver ON m.receiver_id = receiver.id
WHERE m.sender_id = 1
ORDER BY m.created_at DESC;

-- Messages received by a specific user
SELECT 
    m.id,
    sender.username AS sender_username,
    sender.email AS sender_email,
    m.created_at
FROM messages m
JOIN users sender ON m.sender_id = sender.id
WHERE m.receiver_id = 1
ORDER BY m.created_at DESC;

-- View a specific message
SELECT 
    m.id,
    sender.username AS sender_username,
    sender.email AS sender_email,
    receiver.username AS receiver_username,
    receiver.email AS receiver_email,
    m.created_at,
    LENGTH(m.encrypted_message) AS message_size,
    LENGTH(m.encrypted_aes_key) AS aes_key_size,
    LENGTH(m.iv) AS iv_size,
    LENGTH(m.message_hash) AS hash_size,
    LENGTH(m.signature) AS signature_size
FROM messages m
JOIN users sender ON m.sender_id = sender.id
JOIN users receiver ON m.receiver_id = receiver.id
WHERE m.id = 1;

-- Total number of messages
SELECT COUNT(*) AS total_messages FROM messages;

-- Recently sent messages
SELECT 
    m.id,
    sender.username AS sender_username,
    receiver.username AS receiver_username,
    m.created_at
FROM messages m
JOIN users sender ON m.sender_id = sender.id
JOIN users receiver ON m.receiver_id = receiver.id
ORDER BY m.created_at DESC
LIMIT 10;

-- ==============================
-- STATISTICS
-- ==============================

-- General statistics
SELECT 
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM messages) AS total_messages,
    (SELECT COUNT(DISTINCT sender_id) FROM messages) AS active_senders,
    (SELECT COUNT(DISTINCT receiver_id) FROM messages) AS active_receivers;

-- Message statistics per user
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(DISTINCT m_sent.id) AS messages_sent,
    COUNT(DISTINCT m_received.id) AS messages_received,
    COUNT(DISTINCT m_sent.id) + COUNT(DISTINCT m_received.id) AS total_activity
FROM users u
LEFT JOIN messages m_sent ON u.id = m_sent.sender_id
LEFT JOIN messages m_received ON u.id = m_received.receiver_id
GROUP BY u.id, u.username, u.email
ORDER BY total_activity DESC;

-- Top active senders
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(m.id) AS message_count
FROM users u
JOIN messages m ON u.id = m.sender_id
GROUP BY u.id, u.username, u.email
ORDER BY message_count DESC
LIMIT 10;

-- Top active receivers
SELECT 
    u.id,
    u.username,
    u.email,
    COUNT(m.id) AS message_count
FROM users u
JOIN messages m ON u.id = m.receiver_id
GROUP BY u.id, u.username, u.email
ORDER BY message_count DESC
LIMIT 10;

-- Daily message statistics
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS message_count
FROM messages
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;

-- ==============================
-- DATA SIZES
-- ==============================

-- Table sizes (approximate)
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows AS 'Rows'
FROM information_schema.TABLES
WHERE table_schema = 'CipherCoreDB'
ORDER BY (data_length + index_length) DESC;

-- Users table size analysis
SELECT 
    COUNT(*) AS total_users,
    AVG(LENGTH(public_key)) AS avg_public_key_size,
    AVG(LENGTH(private_key)) AS avg_private_key_size,
    AVG(LENGTH(key_salt)) AS avg_key_salt_size,
    AVG(LENGTH(key_iv)) AS avg_key_iv_size,
    SUM(LENGTH(public_key) + LENGTH(private_key) + LENGTH(key_salt) + LENGTH(key_iv)) AS total_key_storage
FROM users;

-- Messages table size analysis
SELECT 
    COUNT(*) AS total_messages,
    AVG(LENGTH(encrypted_message)) AS avg_message_size,
    AVG(LENGTH(encrypted_aes_key)) AS avg_aes_key_size,
    AVG(LENGTH(iv)) AS avg_iv_size,
    AVG(LENGTH(message_hash)) AS avg_hash_size,
    AVG(LENGTH(signature)) AS avg_signature_size
FROM messages;

-- ==============================
-- RELATIONSHIPS AND FOREIGN KEYS
-- ==============================

-- View Foreign Key constraints
SELECT 
    CONSTRAINT_NAME,
    TABLE_NAME,
    COLUMN_NAME,
    REFERENCED_TABLE_NAME,
    REFERENCED_COLUMN_NAME
FROM information_schema.KEY_COLUMN_USAGE
WHERE TABLE_SCHEMA = 'CipherCoreDB'
  AND REFERENCED_TABLE_NAME IS NOT NULL;

-- ==============================
-- DATA INTEGRITY CHECKS
-- ==============================

-- Orphan messages (invalid sender_id or receiver_id)
SELECT 
    m.id,
    m.sender_id,
    m.receiver_id,
    'Invalid sender_id' AS issue
FROM messages m
LEFT JOIN users u ON m.sender_id = u.id
WHERE u.id IS NULL

UNION ALL

SELECT 
    m.id,
    m.sender_id,
    m.receiver_id,
    'Invalid receiver_id' AS issue
FROM messages m
LEFT JOIN users u ON m.receiver_id = u.id
WHERE u.id IS NULL;

-- NULL value check (users)
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN username IS NULL THEN 1 ELSE 0 END) AS null_username,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_email,
    SUM(CASE WHEN public_key IS NULL THEN 1 ELSE 0 END) AS null_public_key,
    SUM(CASE WHEN private_key IS NULL THEN 1 ELSE 0 END) AS null_private_key
FROM users;

-- NULL value check (messages)
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN encrypted_message IS NULL THEN 1 ELSE 0 END) AS null_message,
    SUM(CASE WHEN encrypted_aes_key IS NULL THEN 1 ELSE 0 END) AS null_aes_key,
    SUM(CASE WHEN iv IS NULL THEN 1 ELSE 0 END) AS null_iv,
    SUM(CASE WHEN message_hash IS NULL THEN 1 ELSE 0 END) AS null_hash,
    SUM(CASE WHEN signature IS NULL THEN 1 ELSE 0 END) AS null_signature
FROM messages;

-- ==============================
-- TIME-BASED ANALYSES
-- ==============================

-- Messages in the last 24 hours
SELECT 
    m.id,
    sender.username AS sender,
    receiver.username AS receiver,
    m.created_at
FROM messages m
JOIN users sender ON m.sender_id = sender.id
JOIN users receiver ON m.receiver_id = receiver.id
WHERE m.created_at >= DATE_SUB(NOW(), INTERVAL 24 HOUR)
ORDER BY m.created_at DESC;

-- Messages in the last 7 days
SELECT 
    DATE(m.created_at) AS date,
    COUNT(*) AS message_count
FROM messages m
WHERE m.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(m.created_at)
ORDER BY date DESC;

-- New users in the last 30 days
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC;

-- ==============================
-- SEARCH AND FILTERING
-- ==============================

-- Search by username
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE username LIKE '%search_term%';

-- Search by email
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE email LIKE '%search_term%';

-- Messages within a specific date range
SELECT 
    m.id,
    sender.username AS sender,
    receiver.username AS receiver,
    m.created_at
FROM messages m
JOIN users sender ON m.sender_id = sender.id
JOIN users receiver ON m.receiver_id = receiver.id
WHERE m.created_at BETWEEN '2024-01-01' AND '2024-12-31'
ORDER BY m.created_at DESC;
