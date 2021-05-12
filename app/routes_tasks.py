from flask import Blueprint, request, jsonify, make_response
from app import db 
from app.models.task import Task 
from sqlalchemy import asc, desc
from datetime import datetime
import os, requests
from dotenv import load_dotenv

load_dotenv()

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_tasks_or_tasks_by_title():
    requested_title = request.args.get("sort")
    
    if requested_title == "asc": 
        tasks = Task.query.order_by(Task.title.asc())
    elif requested_title == "desc":
        tasks = Task.query.order_by(Task.title.desc())
    else: 
        tasks = Task.query.all() 
    
    tasks_response = [] 

    for task in tasks: 
        tasks_response.append(task.tasks_to_json())

    return jsonify(tasks_response), 200

@tasks_bp.route("/<task_id>", methods=["GET"], strict_slashes=False)
def get_one_task(task_id):
    task = Task.query.get(task_id)
    
    if task: 
        return jsonify(task.specific_task_to_json()), 200
    
    return make_response("", 404)

@tasks_bp.route("", methods=["POST"], strict_slashes=False)
def post_task(): 
    request_body = request.get_json()
    
    keys = ["title", "description", "completed_at"]
    for key in keys: 
        if key not in request_body:
            return {"details": "Invalid data"}, 400

    new_task = Task.make_a_task(request_body, id=None)

    db.session.add(new_task)
    db.session.commit() 
    return jsonify(new_task.specific_task_to_json()), 201

@tasks_bp.route("<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id): 
    task = Task.query.get(task_id)
    
    if task: 
        update_data = request.get_json() 
        update_data["task_id"] = task_id
        db.session.query(Task).update(update_data)

        # update_task = Task.make_a_task(update_data, task_id)
        # db.session.query(Task).update(update_task.db_to_json())
        db.session.commit()
        return jsonify(task.specific_task_to_json()), 200
    
    return make_response("", 404)

@tasks_bp.route("<task_id>", methods=["DELETE"], strict_slashes=False)
def delete_task(task_id):
    task = Task.query.get(task_id)

    if task: 
        db.session.delete(task)
        db.session.commit()
        
        return {
            "details": f"Task {task_id} \"{task.title}\" successfully deleted"
        }, 200 
    
    return make_response("", 404)

def slack_post_message(title):

    path = "https://slack.com/api/chat.postMessage"
    slack_api_key = os.environ.get("SLACK_API_KEY")
    message = f"Someone just completed the task {title} Task"
    
    params = {
        "channel": "task-notifications",
        "text": message,
        "format": "json"
    }
    headers = {"authorization": f"Bearer {slack_api_key}"}

    requests.post(path, params=params, headers=headers)

@tasks_bp.route("<task_id>/<completion_status>", methods=["PATCH"], strict_slashes=False)
def task_mark_complete_or_incompe(task_id, completion_status=None): 
    task = Task.query.get(task_id)

    if task and completion_status == "mark_complete":
        task.completed_at = datetime.utcnow()
        slack_post_message(task.title)
        return jsonify(task.specific_task_to_json()), 200
    elif task and completion_status == "mark_incomplete":
        task.completed_at = None
        return jsonify(task.specific_task_to_json()), 200

    return make_response("", 404)