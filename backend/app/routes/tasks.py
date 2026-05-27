from flask import Blueprint, request, jsonify
from app.services.supabase_client import supabase
from app.services.email_service import send_task_assigned_email, send_task_completed_email

tasks_bp = Blueprint("tasks", __name__)

@tasks_bp.route("/", methods=["GET"])
def get_tasks():
    user_id = request.args.get("user_id")
    status = request.args.get("status")
    search = request.args.get("search")
    
    query = supabase.table("tasks").select(
        "*, creator:profiles!created_by(full_name, email), assignee:profiles!assigned_to(full_name, email)"
    ).or_(f"created_by.eq.{user_id},assigned_to.eq.{user_id}")
    
    if status and status != "all":
        query = query.eq("status", status)
    if search:
        query = query.ilike("title", f"%{search}%")
    
    response = query.order("created_at", desc=True).execute()
    return jsonify(response.data), 200

@tasks_bp.route("/", methods=["POST"])
def create_task():
    data = request.json
    response = supabase.table("tasks").insert({
        "title": data["title"],
        "description": data.get("description", ""),
        "created_by": data["created_by"],
        "assigned_to": data.get("assigned_to"),
        "status": "pending",
        "priority": data.get("priority", "medium"),
        "due_date": data.get("due_date")
    }).execute()
    
    task = response.data[0]

    if task.get("assigned_to"):
        assignee = supabase.table("profiles").select("*").eq("id", task["assigned_to"]).execute()
        creator = supabase.table("profiles").select("*").eq("id", task["created_by"]).execute()
        if assignee.data and creator.data:
            send_task_assigned_email(
                to_email=assignee.data[0]["email"],
                to_name=assignee.data[0]["full_name"] or assignee.data[0]["email"],
                task_title=task["title"],
                creator_name=creator.data[0]["full_name"] or creator.data[0]["email"]
            )

    return jsonify(task), 201

@tasks_bp.route("/<task_id>", methods=["PUT"])
def update_task(task_id):
    data = request.json
    response = supabase.table("tasks").update(data).eq("id", task_id).execute()
    return jsonify(response.data[0]), 200

@tasks_bp.route("/<task_id>/status", methods=["PATCH"])
def update_status(task_id):
    data = request.json
    new_status = data.get("status")
    response = supabase.table("tasks").update({"status": new_status}).eq("id", task_id).execute()
    task = response.data[0]

    if new_status == "completed":
        creator = supabase.table("profiles").select("*").eq("id", task["created_by"]).execute()
        if creator.data:
            send_task_completed_email(
                to_email=creator.data[0]["email"],
                to_name=creator.data[0]["full_name"] or creator.data[0]["email"],
                task_title=task["title"]
            )

    return jsonify(task), 200

@tasks_bp.route("/<task_id>/complete", methods=["PATCH"])
def complete_task(task_id):
    response = supabase.table("tasks").update({"status": "completed"}).eq("id", task_id).execute()
    task = response.data[0]

    creator = supabase.table("profiles").select("*").eq("id", task["created_by"]).execute()
    if creator.data:
        send_task_completed_email(
            to_email=creator.data[0]["email"],
            to_name=creator.data[0]["full_name"] or creator.data[0]["email"],
            task_title=task["title"]
        )

    return jsonify(task), 200

@tasks_bp.route("/<task_id>", methods=["DELETE"])
def delete_task(task_id):
    supabase.table("tasks").delete().eq("id", task_id).execute()
    return jsonify({"message": "Task deleted"}), 200

@tasks_bp.route("/<task_id>/comments", methods=["GET"])
def get_comments(task_id):
    response = supabase.table("comments").select(
        "*, user:profiles!user_id(full_name, email)"
    ).eq("task_id", task_id).order("created_at").execute()
    return jsonify(response.data), 200

@tasks_bp.route("/<task_id>/comments", methods=["POST"])
def add_comment(task_id):
    data = request.json
    response = supabase.table("comments").insert({
        "task_id": task_id,
        "user_id": data["user_id"],
        "content": data["content"]
    }).execute()
    return jsonify(response.data[0]), 201

@tasks_bp.route("/<task_id>/comments/<comment_id>", methods=["DELETE"])
def delete_comment(task_id, comment_id):
    supabase.table("comments").delete().eq("id", comment_id).execute()
    return jsonify({"message": "Comment deleted"}), 200