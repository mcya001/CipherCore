import os
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.asymmetric import padding
from flask import Blueprint, jsonify, render_template, request, session, redirect, url_for, abort
from ..db import get_db_connection


# creating the messages_bp object so that Flask can recognize these routes
messages_bp = Blueprint("messages", __name__)

@messages_bp.route("/messages-test")
def messages_test():
    return jsonify({"status": "Messages route is working!"})

@messages_bp.route("/inbox")
def inbox():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    receiver_id = session["user_id"]

    conn = get_db_connection()
    cursor = conn.cursor()

    # Try to select with is_read, fallback if column doesn't exist
    try:
        cursor.execute("""
            SELECT 
                m.id,
                u.username AS sender,
                COALESCE(m.is_read, 0) AS is_read,
                m.created_at
            FROM messages m
            JOIN users u ON m.sender_id = u.id
            WHERE m.receiver_id = %s
            ORDER BY m.created_at DESC
        """, (receiver_id,))
    except Exception as e:
        # Fallback if is_read column doesn't exist yet
        # Check if it's a column error
        error_str = str(e).lower()
        if "unknown column" in error_str or "is_read" in error_str:
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
        else:
            # Re-raise if it's a different error
            raise

    mails = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("inbox.html", mails=mails)

@messages_bp.route("/send-mail")
def send_mail():
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))
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
        cursor.close()
        conn.close()
        return render_template("send_mail.html", error="Receiver not found")

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
        cursor.close()
        conn.close()
        return render_template("send_mail.html", error="Password incorrect")

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


@messages_bp.route("/mail/<int:mail_id>", methods=["GET", "POST"])
def read_mail(mail_id):
    if "user_id" not in session:
        return redirect(url_for("auth.login_page"))

    receiver_id = session["user_id"]
    conn = get_db_connection()
    cursor = conn.cursor()

    # Get all message data including encryption fields
    cursor.execute("""
        SELECT 
            m.id,
            u.username AS sender,
            u.id AS sender_id,
            m.encrypted_message,
            m.encrypted_aes_key,
            m.iv,
            m.message_hash,
            m.signature,
            m.created_at
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.id = %s AND m.receiver_id = %s
    """, (mail_id, receiver_id))

    mail = cursor.fetchone()

    if mail is None:
        cursor.close()
        conn.close()
        abort(404)

    # If POST, decrypt the message
    if request.method == "POST":
        password = request.form.get("password")
        error = None
        decrypted_message = None
        hash_valid = False
        signature_valid = False

        if not password:
            error = "Password is required to decrypt the message"
        else:
            try:
                # Get receiver's private key material
                cursor.execute("""
                    SELECT private_key, key_salt, key_iv, public_key
                    FROM users
                    WHERE id = %s
                """, (receiver_id,))
                receiver = cursor.fetchone()

                # Decrypt private key
                kdf = PBKDF2HMAC(
                    algorithm=hashes.SHA256(),
                    length=32,
                    salt=receiver["key_salt"],
                    iterations=100_000
                )
                kek = kdf.derive(password.encode())
                aesgcm = AESGCM(kek)

                private_key_pem = aesgcm.decrypt(
                    receiver["key_iv"],
                    receiver["private_key"],
                    None
                )

                private_key = serialization.load_pem_private_key(
                    private_key_pem,
                    password=None
                )

                # Decrypt AES key with receiver's private key
                aes_key = private_key.decrypt(
                    mail["encrypted_aes_key"],
                    padding.OAEP(
                        mgf=padding.MGF1(hashes.SHA256()),
                        algorithm=hashes.SHA256(),
                        label=None
                    )
                )

                # Decrypt message with AES key
                aesgcm = AESGCM(aes_key)
                decrypted_message = aesgcm.decrypt(
                    mail["iv"],
                    mail["encrypted_message"],
                    None
                ).decode('utf-8')

                # Verify hash
                digest = hashes.Hash(hashes.SHA256())
                digest.update(decrypted_message.encode())
                computed_hash = digest.finalize()
                hash_valid = computed_hash == mail["message_hash"]

                # Verify signature (get sender's public key)
                cursor.execute("""
                    SELECT public_key
                    FROM users
                    WHERE id = %s
                """, (mail["sender_id"],))
                sender = cursor.fetchone()
                sender_public_key = serialization.load_pem_public_key(
                    sender["public_key"]
                )

                try:
                    sender_public_key.verify(
                        mail["signature"],
                        mail["message_hash"],
                        padding.PSS(
                            mgf=padding.MGF1(hashes.SHA256()),
                            salt_length=padding.PSS.MAX_LENGTH
                        ),
                        hashes.SHA256()
                    )
                    signature_valid = True
                except Exception:
                    signature_valid = False

                # Mark as read (if column exists)
                try:
                    cursor.execute("""
                        UPDATE messages
                        SET is_read = 1
                        WHERE id = %s
                    """, (mail_id,))
                    conn.commit()
                except Exception:
                    # Column doesn't exist yet, skip
                    pass

            except Exception as e:
                error = f"Decryption failed: {str(e)}"

        cursor.close()
        conn.close()

        return render_template("read_mail.html", 
                             mail=mail,
                             decrypted_message=decrypted_message,
                             hash_valid=hash_valid,
                             signature_valid=signature_valid,
                             error=error)

    # GET request - show password form
    cursor.close()
    conn.close()
    return render_template("read_mail.html", mail=mail)


