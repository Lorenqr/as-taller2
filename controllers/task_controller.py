from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash
from extensions import db
from models.task import Task

def validate_task_form(form_data):
    errors = []
    title = (form_data.get("title") or "").strip()
    description = (form_data.get("description") or "").strip()
    due_date_str = (form_data.get("due_date") or "").strip()

    if not title:
        errors.append("El título es obligatorio.")

    due_date = None
    if due_date_str:
        try:
            due_date = datetime.strptime(due_date_str, "%Y-%m-%d")
        except ValueError:
            errors.append("La fecha de vencimiento no es válida (use YYYY-MM-DD).")
    
    return title, description, due_date, due_date_str, errors


task_bp = Blueprint("tasks", __name__)

@task_bp.route("/", methods=["GET"])
def index():
    state = request.args.get("state", "all")
    sort = request.args.get("sort", "due_date")

    query = Task.query

    if state == "pending":
        query = query.filter_by(completed=False)
    elif state == "completed":
        query = query.filter_by(completed=True)

    if sort == "title":
        query = query.order_by(Task.title.asc())
    else:
        query = query.order_by(Task.due_date.is_(None), Task.due_date.asc())

    tasks = query.all()
    return render_template("task_list.html", tasks=tasks, state=state, sort=sort)

@task_bp.route("/add", methods=["GET", "POST"])
def add_task():
    if request.method == "POST":
        title, description, due_date, due_date_str, errors = validate_task_form(request.form)

        if errors:
            return render_template(
                "task_form.html",
                errors=errors,
                task=None,
                form={"title": title, "description": description, "due_date": due_date_str},
            )

        task = Task(title=title, description=description, due_date=due_date)
        db.session.add(task)
        db.session.commit()
        flash("Tarea creada exitosamente", "success")
        return redirect(url_for("tasks.index"))

    return render_template("task_form.html", task=None, errors=None, form=None)

@task_bp.route("/edit/<int:task_id>", methods=["GET", "POST"])
def edit_task(task_id: int):
    task = Task.query.get_or_404(task_id)

    if request.method == "POST":
        title, description, due_date, due_date_str, errors = validate_task_form(request.form)
        completed = request.form.get("completed") == "on"

        if errors:
            return render_template(
                "task_form.html",
                errors=errors,
                task=task,
                form={"title": title, "description": description, "due_date": due_date_str, "completed": completed},
            )

        task.title = title
        task.description = description
        task.due_date = due_date
        task.completed = completed

        db.session.commit()
        flash("Tarea editada exitosamente", "success")
        return redirect(url_for("tasks.index"))

    return render_template("task_form.html", task=task, errors=None, form=None)


@task_bp.route("/toggle/<int:task_id>", methods=["POST"])
def toggle_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    task.completed = not task.completed
    db.session.commit()
    return redirect(url_for("tasks.index"))


@task_bp.route("/delete/<int:task_id>", methods=["POST"])
def delete_task(task_id: int):
    task = Task.query.get_or_404(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("tasks.index"))

