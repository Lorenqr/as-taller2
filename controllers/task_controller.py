"""
Controlador de Tareas - Maneja la lógica de negocio de las tareas
"""

from flask import render_template, request, redirect, url_for, flash, jsonify
from datetime import datetime
from models.task import Task
from app import db


def register_routes(app):
    """Registra todas las rutas del controlador de tareas en la aplicación Flask"""

    @app.route('/')
    def index():
        """Ruta principal - Redirige a la lista de tareas"""
        return redirect(url_for('task_list'))

    @app.route('/tasks')
    def task_list():
        """
        Muestra la lista de todas las tareas
        Permite filtrar y ordenar con query params:
        - filter = all | pending | completed
        - sort = date | title | created
        """
        filter_option = request.args.get('filter', 'all')
        sort_option = request.args.get('sort', 'created')

        query = Task.query

        # Filtro por estado
        if filter_option == 'pending':
            query = query.filter_by(completed=False)
        elif filter_option == 'completed':
            query = query.filter_by(completed=True)

        # Ordenamiento
        if sort_option == 'date':
            query = query.order_by(Task.due_date.asc())
        elif sort_option == 'title':
            query = query.order_by(Task.title.asc())
        else:  # por defecto, fecha de creación
            query = query.order_by(Task.created_at.desc())

        tasks = query.all()
        return render_template('tasks/list.html', tasks=tasks)

    @app.route('/tasks/new', methods=['GET', 'POST'])
    def task_create():
        """Crea una nueva tarea"""
        if request.method == 'POST':
            title = request.form.get('title')
            description = request.form.get('description')
            due_date_str = request.form.get('due_date')

            if not title:
                flash('El título es obligatorio.', 'danger')
                return redirect(url_for('task_create'))

            due_date = None
            if due_date_str:
                try:
                    due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Formato de fecha inválido. Usa YYYY-MM-DD.', 'danger')

            new_task = Task(title=title, description=description, due_date=due_date)
            db.session.add(new_task)
            db.session.commit()
            flash('Tarea creada con éxito.', 'success')
            return redirect(url_for('task_list'))

        return render_template('tasks/create.html')

    @app.route('/tasks/<int:task_id>')
    def task_detail(task_id):
        """Muestra los detalles de una tarea específica"""
        task = Task.query.get_or_404(task_id)
        return render_template('tasks/detail.html', task=task)

    @app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
    def task_edit(task_id):
        """Edita una tarea existente"""
        task = Task.query.get_or_404(task_id)

        if request.method == 'POST':
            task.title = request.form.get('title')
            task.description = request.form.get('description')
            due_date_str = request.form.get('due_date')

            if due_date_str:
                try:
                    task.due_date = datetime.strptime(due_date_str, '%Y-%m-%d')
                except ValueError:
                    flash('Formato de fecha inválido.', 'danger')

            db.session.commit()
            flash('Tarea actualizada con éxito.', 'success')
            return redirect(url_for('task_list'))

        return render_template('tasks/edit.html', task=task)

    @app.route('/tasks/<int:task_id>/delete', methods=['POST'])
    def task_delete(task_id):
        """Elimina una tarea"""
        task = Task.query.get_or_404(task_id)
        db.session.delete(task)
        db.session.commit()
        flash('Tarea eliminada con éxito.', 'success')
        return redirect(url_for('task_list'))

    @app.route('/tasks/<int:task_id>/toggle', methods=['POST'])
    def task_toggle(task_id):
        """Cambia el estado de completado de una tarea"""
        task = Task.query.get_or_404(task_id)
        task.completed = not task.completed
        db.session.commit()
        flash('Estado de la tarea actualizado.', 'success')
        return redirect(url_for('task_list'))

    # API básica (futuro)
    @app.route('/api/tasks', methods=['GET'])
    def api_tasks():
        tasks = Task.query.all()
        return jsonify([{
            'id': t.id,
            'title': t.title,
            'description': t.description,
            'completed': t.completed,
            'due_date': t.due_date.strftime('%Y-%m-%d') if t.due_date else None,
            'created_at': t.created_at.strftime('%Y-%m-%d %H:%M:%S')
        } for t in tasks])

    @app.errorhandler(404)
    def not_found_error(error):
        """Maneja errores 404 - Página no encontrada"""
        return render_template('404.html'), 404

    @app.errorhandler(500)
    def internal_error(error):
        """Maneja errores 500 - Error interno del servidor"""
        db.session.rollback()
        return render_template('500.html'), 500

