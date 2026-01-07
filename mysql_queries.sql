-- ==============================
-- CipherCoreDB - GÖRÜNTÜLEME KOMUTLARI
-- ==============================
-- Bu dosya sadece görüntüleme amaçlıdır, veri değiştirmez
-- Veritabanını incelemek ve analiz etmek için kullanılır

USE CipherCoreDB;

-- ==============================
-- VERİTABANI BİLGİLERİ
-- ==============================

-- Mevcut veritabanını göster
SELECT DATABASE();

-- Tüm tabloları listele
SHOW TABLES;

-- Veritabanı karakter seti ve collation
SHOW CREATE DATABASE CipherCoreDB;

-- ==============================
-- TABLO YAPILARI
-- ==============================

-- Users tablosu yapısı
DESCRIBE users;
-- veya
SHOW CREATE TABLE users;

-- Messages tablosu yapısı
DESCRIBE messages;
-- veya
SHOW CREATE TABLE messages;

-- Tüm tabloların yapısını göster
SHOW FULL COLUMNS FROM users;
SHOW FULL COLUMNS FROM messages;

-- ==============================
-- KULLANICI GÖRÜNTÜLEME
-- ==============================

-- Tüm kullanıcıları listele (hassas bilgiler olmadan)
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

-- Belirli bir kullanıcıyı görüntüle (ID ile)
SELECT 
    id,
    username,
    email,
    created_at,
    LENGTH(public_key) AS public_key_size,
    LENGTH(private_key) AS private_key_size
FROM users
WHERE id = 1;

-- Belirli bir kullanıcıyı görüntüle (email ile)
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE email = 'user@example.com';

-- Kullanıcı sayısı
SELECT COUNT(*) AS total_users FROM users;

-- Son kayıt olan kullanıcılar
SELECT 
    id,
    username,
    email,
    created_at
FROM users
ORDER BY created_at DESC
LIMIT 10;

-- ==============================
-- MESAJ GÖRÜNTÜLEME
-- ==============================

-- Tüm mesajları gönderen ve alıcı bilgileriyle görüntüle
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

-- Belirli bir kullanıcının gönderdiği mesajlar
SELECT 
    m.id,
    receiver.username AS receiver_username,
    receiver.email AS receiver_email,
    m.created_at
FROM messages m
JOIN users receiver ON m.receiver_id = receiver.id
WHERE m.sender_id = 1
ORDER BY m.created_at DESC;

-- Belirli bir kullanıcının aldığı mesajlar
SELECT 
    m.id,
    sender.username AS sender_username,
    sender.email AS sender_email,
    m.created_at
FROM messages m
JOIN users sender ON m.sender_id = sender.id
WHERE m.receiver_id = 1
ORDER BY m.created_at DESC;

-- Belirli bir mesajı görüntüle
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

-- Toplam mesaj sayısı
SELECT COUNT(*) AS total_messages FROM messages;

-- Son gönderilen mesajlar
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
-- İSTATİSTİKLER
-- ==============================

-- Genel istatistikler
SELECT 
    (SELECT COUNT(*) FROM users) AS total_users,
    (SELECT COUNT(*) FROM messages) AS total_messages,
    (SELECT COUNT(DISTINCT sender_id) FROM messages) AS active_senders,
    (SELECT COUNT(DISTINCT receiver_id) FROM messages) AS active_receivers;

-- Kullanıcı başına mesaj istatistikleri
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

-- En aktif gönderenler
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

-- En aktif alıcılar
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

-- Günlük mesaj istatistikleri
SELECT 
    DATE(created_at) AS date,
    COUNT(*) AS message_count
FROM messages
GROUP BY DATE(created_at)
ORDER BY date DESC
LIMIT 30;

-- ==============================
-- VERİ BOYUTLARI
-- ==============================

-- Tablo boyutları (yaklaşık)
SELECT 
    table_name AS 'Table',
    ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Size (MB)',
    table_rows AS 'Rows'
FROM information_schema.TABLES
WHERE table_schema = 'CipherCoreDB'
ORDER BY (data_length + index_length) DESC;

-- Users tablosu boyut analizi
SELECT 
    COUNT(*) AS total_users,
    AVG(LENGTH(public_key)) AS avg_public_key_size,
    AVG(LENGTH(private_key)) AS avg_private_key_size,
    AVG(LENGTH(key_salt)) AS avg_key_salt_size,
    AVG(LENGTH(key_iv)) AS avg_key_iv_size,
    SUM(LENGTH(public_key) + LENGTH(private_key) + LENGTH(key_salt) + LENGTH(key_iv)) AS total_key_storage
FROM users;

-- Messages tablosu boyut analizi
SELECT 
    COUNT(*) AS total_messages,
    AVG(LENGTH(encrypted_message)) AS avg_message_size,
    AVG(LENGTH(encrypted_aes_key)) AS avg_aes_key_size,
    AVG(LENGTH(iv)) AS avg_iv_size,
    AVG(LENGTH(message_hash)) AS avg_hash_size,
    AVG(LENGTH(signature)) AS avg_signature_size
FROM messages;

-- ==============================
-- İLİŞKİLER VE FOREIGN KEY'LER
-- ==============================

-- Foreign key kısıtlamalarını görüntüle
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
-- VERİ BÜTÜNLÜĞÜ KONTROLLERİ
-- ==============================

-- Orphan mesajlar (geçersiz sender_id veya receiver_id)
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

-- NULL değer kontrolü (users)
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN username IS NULL THEN 1 ELSE 0 END) AS null_username,
    SUM(CASE WHEN email IS NULL THEN 1 ELSE 0 END) AS null_email,
    SUM(CASE WHEN public_key IS NULL THEN 1 ELSE 0 END) AS null_public_key,
    SUM(CASE WHEN private_key IS NULL THEN 1 ELSE 0 END) AS null_private_key
FROM users;

-- NULL değer kontrolü (messages)
SELECT 
    COUNT(*) AS total,
    SUM(CASE WHEN encrypted_message IS NULL THEN 1 ELSE 0 END) AS null_message,
    SUM(CASE WHEN encrypted_aes_key IS NULL THEN 1 ELSE 0 END) AS null_aes_key,
    SUM(CASE WHEN iv IS NULL THEN 1 ELSE 0 END) AS null_iv,
    SUM(CASE WHEN message_hash IS NULL THEN 1 ELSE 0 END) AS null_hash,
    SUM(CASE WHEN signature IS NULL THEN 1 ELSE 0 END) AS null_signature
FROM messages;

-- ==============================
-- ZAMAN BAZLI ANALİZLER
-- ==============================

-- Son 24 saatteki mesajlar
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

-- Son 7 gündeki mesajlar
SELECT 
    DATE(m.created_at) AS date,
    COUNT(*) AS message_count
FROM messages m
WHERE m.created_at >= DATE_SUB(NOW(), INTERVAL 7 DAY)
GROUP BY DATE(m.created_at)
ORDER BY date DESC;

-- Son 30 gündeki yeni kullanıcılar
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE created_at >= DATE_SUB(NOW(), INTERVAL 30 DAY)
ORDER BY created_at DESC;

-- ==============================
-- ARAMA VE FİLTRELEME
-- ==============================

-- Kullanıcı adına göre arama
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE username LIKE '%search_term%';

-- Email'e göre arama
SELECT 
    id,
    username,
    email,
    created_at
FROM users
WHERE email LIKE '%search_term%';

-- Belirli tarih aralığındaki mesajlar
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

