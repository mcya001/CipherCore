# CipherCore
COMP417 - Introduction to Cryptography Project

A secure end-to-end encrypted email system.

## 🚀 Project Description

CipherCore is a secure email system that uses end-to-end encryption to protect user communications. Messages are encrypted using AES-GCM symmetric encryption, with keys protected by RSA asymmetric encryption. The system also includes digital signatures and hash verification to ensure message integrity and authenticity.

## ✨ Features

### ✅ Completed Features

1. **User Management**
   - Secure registration system with bcrypt password hashing
   - Login/Logout functionality
   - Session management
   - Duplicate email/username validation

2. **Cryptography**
   - RSA 2048-bit key pair generation
   - Private key encryption using password-derived keys (AES-GCM)
   - Message content encryption with AES-GCM
   - AES key encryption with receiver's public key (RSA-OAEP)
   - SHA-256 hash verification
   - Digital signature verification (RSA-PSS)

3. **Mail System**
   - Encrypted mail sending
   - Encrypted mail reading and decryption
   - Hash and signature verification
   - Unread mail indicator
   - Inbox listing
   - Mail status tracking (read/unread)

4. **Security**
   - Password hashing (Werkzeug)
   - Private key encryption (PBKDF2 + AES-GCM)
   - End-to-end encryption
   - Message integrity verification
   - Digital signature verification
   - Secure session management

## 📋 Requirements

- Python 3.8+
- MySQL 5.7+ or MariaDB
- pip

## 🔧 Installation

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd CipherCore
```

### Step 2: Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Create MySQL Database
```bash
mysql -u root -p < CipherCoreDB.sql
```

**Note:** If you have an existing database without the `is_read` column, run:
```bash
python run_migration.py
```

Or manually in MySQL:
```sql
USE CipherCoreDB;
ALTER TABLE messages 
ADD COLUMN is_read TINYINT(1) DEFAULT 0 AFTER signature;
```

### Step 5: Configure Environment Variables
Create a `.env` file in the project root:
```
MYSQL_HOST=localhost
MYSQL_USER=root
MYSQL_PASSWORD=your_password
MYSQL_DB=CipherCoreDB
SECRET_KEY=your-secret-key-here-change-in-production
```

### Step 6: Run the Application
```bash
python run.py
```

The application will be available at `http://localhost:5000`

## 📖 Usage

1. **Register:** Create a new account at `/register`
2. **Login:** Sign in at `/login`
3. **Send Mail:** Use "New Mail" from the dashboard to send encrypted messages
4. **Read Mail:** Select a mail from the inbox and enter your password to decrypt and verify

## 🗄️ Database Structure

### `users` Table
- `id`: Primary key
- `username`: Username (unique)
- `email`: Email address (unique)
- `password_hash`: Hashed password
- `public_key`: RSA public key (PEM format)
- `private_key`: Encrypted private key (AES-GCM)
- `key_salt`: PBKDF2 salt
- `key_iv`: AES-GCM IV
- `created_at`: Registration timestamp

### `messages` Table
- `id`: Primary key
- `sender_id`: Sender user ID (foreign key)
- `receiver_id`: Receiver user ID (foreign key)
- `encrypted_message`: Encrypted message content (AES-GCM)
- `encrypted_aes_key`: Encrypted AES key (RSA-OAEP)
- `iv`: AES-GCM initialization vector
- `message_hash`: SHA-256 hash
- `signature`: Digital signature (RSA-PSS)
- `is_read`: Read status (0 = unread, 1 = read)
- `created_at`: Message timestamp

## 🔐 Cryptography Details

### Key Generation
- **Algorithm:** RSA
- **Key Size:** 2048 bits
- **Public Exponent:** 65537

### Private Key Encryption
- **KDF:** PBKDF2-HMAC-SHA256
- **Iterations:** 100,000
- **Encryption:** AES-GCM-256
- **Salt & IV:** Random 16-byte salt, 12-byte IV

### Message Encryption
- **Symmetric Key:** Random 256-bit AES key
- **Encryption:** AES-GCM-256
- **Key Encryption:** RSA-OAEP (SHA-256)

### Integrity & Authentication
- **Hash Algorithm:** SHA-256
- **Signature:** RSA-PSS (SHA-256)

## 📁 Project Structure

```
CipherCore/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── db.py                 # Database connection
│   └── routes/
│       ├── auth.py           # Authentication routes
│       └── messages.py       # Message routes
├── templates/                # HTML templates
│   ├── layout.html
│   ├── login.html
│   ├── register.html
│   ├── inbox.html
│   ├── send_mail.html
│   └── read_mail.html
├── static/                   # CSS, JS, images
│   ├── style.css
│   ├── mail.css
│   └── images/
│       └── enc.png
├── config.py                 # Configuration
├── run.py                    # Application entry point
├── run_migration.py          # Database migration script
├── CipherCoreDB.sql          # Database schema
├── requirements.txt          # Python dependencies
└── README.md                 # This file
```

## 🔒 Security Notes

- **Production Deployment:**
  - Use a strong `SECRET_KEY` in production
  - Store MySQL credentials in `.env` (never commit to git)
  - Use HTTPS for all connections
  - Implement rate limiting
  - Add input validation and sanitization
  - Regular security audits

- **Best Practices:**
  - Keep dependencies updated
  - Use environment variables for sensitive data
  - Implement proper error handling
  - Log security events

## 🐛 Troubleshooting

### Database Connection Issues
- Verify MySQL is running
- Check `.env` file configuration
- Ensure database exists: `mysql -u root -p -e "SHOW DATABASES;"`

### Migration Issues
- Run `python run_migration.py` to add missing columns
- Check database permissions

### Import Errors
- Activate virtual environment
- Reinstall dependencies: `pip install -r requirements.txt`

## 📝 License

This project is for educational purposes.

## 👥 Development Team

This project was developed by a team of 6 members:

1. **Mustafa Ceylan**
2. **Çağla Toprak**
3. **Melda Paksoy**
4. **Seher Sesli**
5. **Şevval Yücel**
6. **Songül Takıcı**

---

**Course:** COMP417 - Introduction to Cryptography  
**Institution:** Abdullah Gul University  
**Term:** 2025-2026 Fall