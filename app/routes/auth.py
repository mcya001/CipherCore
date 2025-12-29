import os 
from flask import Blueprint, jsonify, render_template, request, redirect, url_for
from app.db import get_db_connection

# --- DOSYA YOLU AYARI ---

template_path = r"C:\Users\seher\CipherCore\templates"

# 2. CSS ve Resimlerin dosya yolu

static_path = r"C:\Users\seher\CipherCore\static"

# Blueprint Ayarları
auth_bp = Blueprint("auth", __name__, 
                    template_folder=template_path,
                    static_folder=static_path,
                    static_url_path='/assets')


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

# Login İşlemleri

# 1. Login Sayfasını Göster (GET)
@auth_bp.route('/', methods=['GET'])
@auth_bp.route('/login', methods=['GET'])
def login_page():
    # templates klasöründeki login.html dosyasını ekrana bastır
    return render_template('login.html')

# 2. Login Formu Gönderildiğinde (POST)
@auth_bp.route('/login', methods=['POST'])
def login_post():
    # Formdan gelen verileri al
    username = request.form.get('username')
    password = request.form.get('password')

    # Burası şimdilik terminale basar, veritabanı bağlantısını sonra yapılsın
    print(f"GİRİŞ DENEMESİ -> Kullanıcı: {username}, Şifre: {password}")

    # İşlem bitince 
    # "Başarılı" diye bir yazı döndürsün.
    return f"Hoşgeldin {username}, şifren backend'e ulaştı!"

# --- REGISTER SAYFASI ---
@auth_bp.route('/register', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        # Buraya kayıt olma mantığı (Database kayıt vb.) yapılacak
        fullname = request.form.get('fullname')
        email = request.form.get('email')
        # Şimdilik sadece print edelim
        print(f"KAYIT İSTEĞİ: {fullname} - {email}")
        return redirect(url_for('auth.login_page'))
    
    return render_template('register.html')