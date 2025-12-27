from flask import Blueprint, jsonify

# creating the messages_bp object so that Flask can recognize these routes
messages_bp = Blueprint("messages", __name__)

@messages_bp.route("/messages-test")
def messages_test():
    return jsonify({"status": "Messages route is working!"})