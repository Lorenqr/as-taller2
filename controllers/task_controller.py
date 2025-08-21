from flask import Blueprint, jsonify
from models.task import Task

task_bp = Blueprint("tasks", __name__)

@task_bp.route("/tasks", methods=["GET"])
def get_tasks():
    tasks = Task.query.all()
    return jsonify([{
        "id": t.id,
        "title": t.title,
        "description": t.description,
        "completed": t.completed
    } for t in tasks])

def register_routes(app):
    app.register_blueprint(task_bp)  # 👉 esto conecta las rutas

