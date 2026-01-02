import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from flask import Blueprint, jsonify
from ..db import get_db_connection
from flask import abort, request, session, redirect, url_for
from cryptography.hazmat.primitives.asymmetric import padding


# creating the messages_bp object so that Flask can recognize these routes
messages_bp = Blueprint("messages", __name__)

@messages_bp.route("/messages-test")
def messages_test():
    return jsonify({"status": "Messages route is working!"})

from flask import render_template

@messages_bp.route("/inbox")
def inbox():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    receiver_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            m.id,
            u.username AS sender,
            0 AS is_read,
            m.created_at
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = %s
        ORDER BY m.created_at DESC
    """, (receiver_id,))

    mails = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("inbox.html", mails=mails)

@messages_bp.route("/send-mail")
def send_mail():
    return render_template("send_mail.html")

# Encryption of mail, send mail (post)
@messages_bp.route("/send-mail", methods=["POST"])
def send_mail_post():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    sender_id = session["user_id"]
    receiver_email = request.form.get("receiver")
    message = request.form.get("message")
    password = request.form.get("password")  # private key unlock

    conn = get_db_connection()
    cursor = conn.cursor()

    # Receiver public key
    cursor.execute("""
        SELECT id, public_key
        FROM users
        WHERE email = %s
    """, (receiver_email,))
    receiver = cursor.fetchone()

    if receiver is None:
        conn.close()
        return "Receiver not found", 404

    # Sender private key material
    cursor.execute("""
        SELECT private_key, key_salt, key_iv
        FROM users
        WHERE id = %s
    """, (sender_id,))
    sender = cursor.fetchone()

    # PRIVATE KEY DECRYPT
    try:
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=sender["key_salt"],
            iterations=100_000
        )
        kek = kdf.derive(password.encode())
        aesgcm = AESGCM(kek)

        private_key_pem = aesgcm.decrypt(
            sender["key_iv"],
            sender["private_key"],
            None
        )

        private_key = serialization.load_pem_private_key(
            private_key_pem,
            password=None
        )
    except Exception:
        conn.close()
        return "Password incorrect", 403

    # AES MAIL ENCRYPTION
    aes_key = os.urandom(32)
    iv = os.urandom(12)
    aesgcm = AESGCM(aes_key)
    encrypted_message = aesgcm.encrypt(iv, message.encode(), None)

    # AES KEY → RECEIVER PUBLIC KEY
    receiver_public_key = serialization.load_pem_public_key(
        receiver["public_key"]
    )

    encrypted_aes_key = receiver_public_key.encrypt(
        aes_key,
        padding.OAEP(
            mgf=padding.MGF1(hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

    # HASH + SIGNATURE
    digest = hashes.Hash(hashes.SHA256())
    digest.update(message.encode())
    message_hash = digest.finalize()

    signature = private_key.sign(
        message_hash,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH
        ),
        hashes.SHA256()
    )

    # DB INSERT
    cursor.execute("""
        INSERT INTO messages
        (sender_id, receiver_id,
         encrypted_message, encrypted_aes_key,
         iv, message_hash, signature)
        VALUES (%s,%s,%s,%s,%s,%s,%s)
    """, (
        sender_id,
        receiver["id"],
        encrypted_message,
        encrypted_aes_key,
        iv,
        message_hash,
        signature
    ))

    conn.commit()
    conn.close()

    return redirect(url_for("messages.inbox"))


@messages_bp.route("/mail/<int:mail_id>")
def read_mail(mail_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    receiver_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            m.id,
            u.username AS sender,
            m.encrypted_message,
            m.created_at
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = %s AND m.receiver_id = %s
    """, (mail_id,receiver_id))

    mail = cursor.fetchone()

    cursor.close()
    conn.close()

    if mail is None:
        abort(404)

    return render_template("read_mail.html", mail=mail)


