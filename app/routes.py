from flask import Blueprint, request, jsonify, make_response
from app import db 
from app.models.task import Task 

tasks_bp = Blueprint("tasks", __name__, url_prefix="/tasks")

# def null_convert_to_false_for_all_tasks(tasks_response): 
#     for task in tasks_response: 
#         if task["is_complete"] is None: 
#             task["is_complete"] = False

#     return tasks_response

# def null_convert_to_false_for_specific_task(jsonified_task): 
#     if jsonified_task["task"]["is_complete"] is None: 
#         jsonified_task["task"]["is_complete"] = False
    
#     return jsonified_task

@tasks_bp.route("", methods=["GET"], strict_slashes=False)
def get_tasks():
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
    if len(request_body) == 3: 
        new_task = Task(title=request_body["title"],
                        description=request_body["description"], 
                        completed_at=request_body["completed_at"])

        db.session.add(new_task)
        db.session.commit() 
        return jsonify(new_task.specific_task_to_json()), 201
    
    return {"details": "Invalid data"}, 400

@tasks_bp.route("<task_id>", methods=["PUT"], strict_slashes=False)
def update_task(task_id): 
    task = Task.query.get(task_id)
    
    if task: 
        update_data = request.get_json() 
        task.title = update_data["title"]
        task.description = update_data["description"]
        task.completed_at = update_data["completed_at"]
    
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