import os
from flask import Blueprint, jsonify, render_template, request, redirect, url_for, session
from ..db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers.aead import AESGCM


# --- DİNAMİK DOSYA YOLU AYARI ---
current_dir = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.abspath(os.path.join(current_dir, "../../"))

template_path = os.path.join(BASE_DIR, "templates")
static_path = os.path.join(BASE_DIR, "static")

auth_bp = Blueprint(
    "auth", __name__,
    template_folder=template_path,
    static_folder=static_path,
    static_url_path='/assets'
)

# MEVCUT DATABASE TEST KODU
@auth_bp.route("/test-db")
def test_db():
    try:
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
        conn.close()
        return jsonify({"status": "Success", "tables": tables})
    except Exception as e:
        return jsonify({"status": "Error", "message": str(e)})

# --- LOGIN SAYFASI ---
@auth_bp.route('/', methods=['GET'])
@auth_bp.route('/login', methods=['GET'])
def login_page():
    return render_template('login.html', error=False)

@auth_bp.route('/login', methods=['POST'])
def login_post():
    email = request.form.get('email')
    password = request.form.get('password')

    conn = get_db_connection()
    with conn.cursor() as cursor:
        cursor.execute(
            """
            SELECT id, password_hash, private_key, key_salt, key_iv
            FROM users
            WHERE email = %s
            """,
            (email,)
        )

        user = cursor.fetchone()
    conn.close()

    # Kullanıcı yok
    if user is None:
        return render_template(
            'login.html',
            error="user_not_found"
        )

    stored_hashed_password = user['password_hash']

    # Şifre yanlış
    if not check_password_hash(stored_hashed_password, password):
        return render_template(
            'login.html',
            error="wrong_password"
        )

    # Private Key doğrulaması
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=user['key_salt'],
            iterations=100_000
        )

        kek = kdf.derive(password.encode())
        aesgcm = AESGCM(kek)

        private_key_pem = aesgcm.decrypt(
            user['key_iv'],
            user['private_key'],
            None
        )


    except Exception:
        # Password doğru olsa bile key decrypt edilemiyorsa
        return render_template(
            'login.html',
            error="wrong_password"
        )

    # Başarılı giriş
    session['user_id'] = user['id']
    return redirect(url_for('auth.dashboard'))


# --- REGISTER SAYFASI ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')

        if password != confirm_password:
            return "Şifreler uyuşmuyor!"

        hashed_password = generate_password_hash(password)

        # RSA KEY PAIR
        private_key = rsa.generate_private_key(
            public_exponent=65537,
            key_size=2048
        )
        public_key = private_key.public_key()

        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # PRIVATE KEY → PASSWORD'DAN TÜRETİLEN KEY İLE ENCRYPT
        salt = os.urandom(16)

        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100_000
        )

        kek = kdf.derive(password.encode())
        aesgcm = AESGCM(kek)
        iv = os.urandom(12)

        private_pem = private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption()
        )

        encrypted_private_key = aesgcm.encrypt(iv, private_pem, None)

        # DB INSERT
        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users
                (username, email, password_hash,
                 public_key, private_key, key_salt, key_iv)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (
                    username,
                    email,
                    hashed_password,
                    public_pem,
                    encrypted_private_key,
                    salt,
                    iv
                )
            )
            conn.commit()
        conn.close()


        return redirect(url_for('auth.login_page'))

    return render_template('register.html')

# Mail ekranı
@auth_bp.route('/dashboard')
def dashboard():
    return render_template('layout.html')
