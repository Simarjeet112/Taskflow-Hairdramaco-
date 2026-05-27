from flask import Blueprint, jsonify
from app.services.supabase_client import supabase

users_bp = Blueprint("users", __name__)

@users_bp.route("/", methods=["GET"])
def get_users():
    response = supabase.table("profiles").select("id, full_name, email, avatar_url").execute()
    return jsonify(response.data), 200