from flask import Blueprint, jsonify
from app.db import get_db_connection
from flask import abort


# creating the messages_bp object so that Flask can recognize these routes
messages_bp = Blueprint("messages", __name__)

@messages_bp.route("/messages-test")
def messages_test():
    return jsonify({"status": "Messages route is working!"})

from flask import render_template

@messages_bp.route("/inbox")
def inbox():
    conn = get_db_connection()
    cursor = conn.cursor()

    cursor.execute("""
        SELECT 
            m.id,
            u.username AS sender,
            m.created_at
        FROM messages m
        JOIN users u ON m.sender_id = u.id
        WHERE m.receiver_id = 1
        ORDER BY m.created_at DESC
    """)

    mails = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template("inbox.html", mails=mails)

@messages_bp.route("/send-mail")
def send_mail():
    return render_template("send_mail.html")

@messages_bp.route("/mail/<int:mail_id>")
def read_mail(mail_id):
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
        WHERE m.id = %s AND m.receiver_id = 1
    """, (mail_id,))

    mail = cursor.fetchone()

    cursor.close()
    conn.close()

    if mail is None:
        abort(404)

    return render_template("read_mail.html", mail=mail)


