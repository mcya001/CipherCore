from flask import Blueprint, jsonify
from app.db import get_db_connection

auth_bp = Blueprint("auth", __name__)

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