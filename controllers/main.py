from flask import Blueprint, render_template, redirect, url_for, request, flash, jsonify
from flask_login import login_required, current_user
from extensions import db
from models.folder import Folder
from models.task import Task
from datetime import datetime

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    return render_template('auth/login.html')

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_folders = current_user.folders.all()
    user_tasks = current_user.tasks.all()
    return render_template('dashboard.html', folders=user_folders, tasks=user_tasks)

@main_bp.route('/create_folder', methods=['GET', 'POST'])
@login_required
def create_folder():
    folder_name = request.form.get('folder_name')
    if not folder_name:
        return 'Folder name is required.', 400  # Bad Request

    new_folder = Folder(name=folder_name, owner=current_user)
    db.session.add(new_folder)
    db.session.commit()

    response = {'folder_name': new_folder.name, 'folder_id': new_folder.id}
    return jsonify(response), 200

@main_bp.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    task_name = request.form.get('task_name')
    folder_id = request.form.get('folder_id')
    deadline = request.form.get('deadline')

    if not task_name or not folder_id:
        return 'Task name and folder are required.', 400

    # Validate folder ownership
    folder = Folder.query.filter_by(id=folder_id, owner=current_user).first()
    if not folder:
        return 'Folder not found or not authorized.', 403  # Forbidden

    # Parse deadline if provided
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d')
        except ValueError:
            return 'Invalid date format.', 400
    else:
        deadline_date = None

    new_task = Task(
        name=task_name,
        folder=folder,
        assignee=current_user,
        deadline=deadline_date
    )
    db.session.add(new_task)
    db.session.commit()

    response = {
        'task_name': new_task.name,
        'task_id': new_task.id,
        'deadline': new_task.deadline.strftime('%Y-%m-%d') if new_task.deadline else 'No deadline'
    }
    return jsonify(response), 200