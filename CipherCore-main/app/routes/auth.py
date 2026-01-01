import os
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from app.db import get_db_connection
from werkzeug.security import generate_password_hash, check_password_hash

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
            "SELECT password_hash FROM users WHERE email = %s",
            (email,)
        )
        user = cursor.fetchone()
    conn.close()

    # ❌ Kullanıcı yok
    if user is None:
        return render_template(
            'login.html',
            error="user_not_found"
        )

    stored_hashed_password = user['password_hash']

    # ❌ Şifre yanlış
    if not check_password_hash(stored_hashed_password, password):
        return render_template(
            'login.html',
            error="wrong_password"
        )

    # ✅ Başarılı giriş
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

        conn = get_db_connection()
        with conn.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO users (username, email, password_hash)
                VALUES (%s, %s, %s)
                """,
                (username, email, hashed_password)
            )
            conn.commit()
        conn.close()

        return redirect(url_for('auth.login_page'))

    return render_template('register.html')

# Mail ekranı
@auth_bp.route('/dashboard')
def dashboard():
    return render_template('mail_screen.html')
