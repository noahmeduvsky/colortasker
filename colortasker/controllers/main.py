from flask import Blueprint, render_template, redirect, url_for, request, jsonify
from flask_login import login_required, current_user
from colortasker.extensions import db
from colortasker.models import Folder, Task, User, Comment, Friend
from datetime import datetime, date
import calendar
main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    else:
        return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
@login_required
def dashboard():
    user_folders = current_user.folders
    user_tasks = current_user.tasks
    user_friends = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id)
    ).all()

    # Format friends as a list of dictionaries with resolved names
    friends_list = []
    for friend in user_friends:
        if friend.user_id == current_user.id:
            friends_list.append({'name': friend.friend.name})
        else:
            friends_list.append({'name': friend.user.name})

    return render_template(
        'dashboard.html',
        folders=user_folders,
        tasks=user_tasks,
        friends=friends_list
    )

@main_bp.route('/create_folder', methods=['POST'])
@login_required
def create_folder():
    data = request.get_json()
    folder_name = data.get('folder_name')
    if not folder_name:
        return jsonify({'error': 'Folder name is required.'}), 400

    new_folder = Folder(name=folder_name, owner=current_user)
    db.session.add(new_folder)
    db.session.commit()

    response = {'folder_name': new_folder.name, 'folder_id': new_folder.id}
    return jsonify(response), 200


@main_bp.route('/create_task', methods=['POST'])
@login_required
def create_task():
    task_name = request.form.get('task_name')
    folder_id = request.form.get('folder_id')
    deadline = request.form.get('deadline')
    color = request.form.get('color')
    description = request.form.get('description')

    # Validate task_name and folder_id
    if not task_name or not folder_id:
        return jsonify({'error': 'Task name and folder are required.'}), 400

    # Convert folder_id to integer
    try:
        folder_id = int(folder_id)  # Cast folder_id to integer
    except ValueError:
        return jsonify({'error': 'Invalid folder ID format.'}), 400

    # Validate folder ownership
    folder = Folder.query.filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        return jsonify({'error': 'Folder not found or not authorized.'}), 403

    # Parse deadline if provided
    deadline_date = None
    if deadline:
        try:
            deadline_date = datetime.strptime(deadline, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format.'}), 400

    # Create new Task instance with correct parameters
    new_task = Task(
        name=task_name,
        deadline=deadline_date,
        folder_id=folder.id,
        color=color,
        description=description,
    )

    # Assign the current user to the task
    new_task.users.append(current_user)

    db.session.add(new_task)
    db.session.commit()

    response = {
        'task_name': new_task.name,
        'task_id': new_task.id,
        'deadline': new_task.deadline.strftime('%Y-%m-%d') if new_task.deadline else None
    }
    return jsonify(response), 200

@main_bp.route('/get_folder_content')
@login_required
def get_folder_content():
    folder_id = request.args.get('folder_id')

    # Convert folder_id to integer
    try:
        folder_id = int(folder_id)
    except ValueError:
        return jsonify({'error': 'Invalid folder ID format.'}), 400

    # Validate folder ownership
    folder = Folder.query.filter_by(id=folder_id, owner=current_user).first()
    if not folder:
        return jsonify({'error': 'Folder not found or not authorized.'}), 403

    # Fetch tasks in the folder
    tasks = [
        {
            'id': task.id,
            'name': task.name,
            'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else None,
            'is_complete': task.is_complete,
            'color': task.color or '#ffffff',
            'description': task.description or ''
        }
        for task in folder.tasks
    ]

    response = {
        'folder_name': folder.name,
        'tasks': tasks
    }
    return jsonify(response), 200

@main_bp.route('/edit_task', methods=['POST'])
@login_required
def edit_task():
    task_id = request.form.get('task_id')
    task_name = request.form.get('task_name')
    deadline = request.form.get('deadline')
    color = request.form.get('color')
    description = request.form.get('description')
    folder_id = request.form.get('folder_id')

    # Validate inputs
    if not task_id or not task_name or not folder_id:
        return jsonify({'error': 'Task ID, Task Name, and Folder ID are required.'}), 400

    # Convert folder_id to integer
    try:
        folder_id = int(folder_id)
    except ValueError:
        return jsonify({'error': 'Invalid folder ID format.'}), 400

    # Retrieve the task and validate user access
    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or not authorized.'}), 403

    # Validate new folder ownership
    folder = Folder.query.filter_by(id=folder_id, owner_id=current_user.id).first()
    if not folder:
        return jsonify({'error': 'Folder not found or not authorized.'}), 403

    # Update task fields
    task.name = task_name
    task.description = description
    task.color = color
    task.folder_id = folder.id

    # Parse deadline if provided
    if deadline:
        try:
            task.deadline = datetime.strptime(deadline, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format.'}), 400
    else:
        task.deadline = None

    db.session.commit()

    response = {
        'task_name': task.name,
        'task_id': task.id,
        'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else None
    }
    return jsonify(response), 200

@main_bp.route('/get_task')
@login_required
def get_task():
    task_id = request.args.get('task_id')
    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or not authorized.'}), 403

    response = {
        'task_id': task.id,
        'task_name': task.name,
        'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else '',
        'description': task.description or '',
        'color': task.color or '#ffffff',
        'folder_id': task.folder_id,
        'folder_name': task.folder.name,
        'collaborators': [{'id': user.id, 'email': user.email} for user in task.users]
    }
    return jsonify(response), 200

@main_bp.route('/get_all_user_tasks', methods=['GET'])
@login_required
def get_all_user_tasks():
    tasks = Task.query.filter(Task.users.contains(current_user)).all()

    task_list = [
        {
            'id': task.id,
            'name': task.name,
            'deadline': task.deadline.strftime('%Y-%m-%d') if task.deadline else '',
            'color': task.color or '#ffffff',
            'description': task.description or '',
            'folder_name': task.folder.name if task.folder else None,
            'is_complete': task.is_complete,
        }
        for task in tasks
    ]

    return jsonify({'tasks': task_list}), 200

@main_bp.route('/delete_task', methods=['POST'])
@login_required
def delete_task():
    data = request.get_json()
    task_id = data.get('task_id')
    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or not authorized.'}), 403

    db.session.delete(task)
    db.session.commit()
    return jsonify({'message': 'Task deleted successfully.'}), 200

@main_bp.route('/mark_complete', methods=['POST'])
@login_required
def mark_complete():
    data = request.get_json()
    task_id = data.get('task_id')
    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or not authorized.'}), 403

    task.is_complete = True
    db.session.commit()
    return jsonify({'message': 'Task marked as complete.'}), 200

@main_bp.route('/delete_folder', methods=['POST'])
@login_required
def delete_folder():
    data = request.get_json()  # Get the JSON data from the request
    folder_id = data.get('folder_id')  # Extract the folder ID

    if not folder_id:  # Validate that folder_id is provided
        return jsonify({'error': 'Folder ID is required.'}), 400

    # Validate that the folder exists and belongs to the current user
    folder = Folder.query.filter_by(id=folder_id, owner=current_user).first()
    if not folder:
        return jsonify({'error': 'Folder not found or not authorized.'}), 403

    # Delete all tasks associated with the folder
    for task in folder.tasks:
        db.session.delete(task)

    # Delete the folder itself
    db.session.delete(folder)
    db.session.commit()

    return jsonify({'message': 'Folder deleted successfully.'}), 200

@main_bp.route('/edit_folder', methods=['POST'])
@login_required
def edit_folder():
    data = request.get_json()
    folder_id = data.get('folder_id')
    folder_name = data.get('folder_name')

    if not folder_id or not folder_name:
        return jsonify({'error': 'Folder ID and new name are required.'}), 400

    # Validate folder ownership
    folder = Folder.query.filter_by(id=folder_id, owner=current_user).first()
    if not folder:
        return jsonify({'error': 'Folder not found or not authorized.'}), 403

    # Update the folder name
    folder.name = folder_name
    db.session.commit()

    return jsonify({'message': 'Folder updated successfully.'}), 200

@main_bp.route('/get_user_folders')
@login_required
def get_user_folders():
    folders = [
        {'id': folder.id, 'name': folder.name}
        for folder in current_user.folders
    ]
    return jsonify({'folders': folders}), 200

@main_bp.route('/calendar')
@login_required
def calendar_view():
    # Get month and year from query parameters or use current month/year
    month = request.args.get('month', type=int)
    year = request.args.get('year', type=int)
    if not month or not year:
        today = date.today()
        month = today.month
        year = today.year

    # Get first and last day of the month
    first_day_of_month = date(year, month, 1)
    num_days = calendar.monthrange(year, month)[1]
    last_day_of_month = date(year, month, num_days)

    # Generate list of days in the month
    calendar_days = []
    for day_num in range(1, num_days + 1):
        day_date = date(year, month, day_num)
        tasks = Task.query.filter(
            Task.deadline == day_date,
            Task.users.any(id=current_user.id)
        ).all()
        day_tasks = [{
            'id': task.id,
            'name': task.name,
            'color': task.color or '#3498db'
        } for task in tasks]
        calendar_days.append({
            'day': day_num,
            'date': day_date.isoformat(),
            'is_today': day_date == date.today(),
            'tasks': day_tasks
        })

    current_month_year = first_day_of_month.strftime('%B %Y')

    return render_template(
        'calendar.html',
        calendar_days=calendar_days,
        current_month_year=current_month_year,
        current_month=month,
        current_year=year
    )


@main_bp.route('/invite_user', methods=['POST'])
@login_required
def invite_user():
    data = request.get_json()
    task_id = data.get('task_id')
    email = data.get('email')

    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or access denied.'}), 403

    user_to_invite = User.query.filter_by(email=email).first()
    if not user_to_invite:
        return jsonify({'error': 'User not found.'}), 404

    # Check if user is already a collaborator
    if user_to_invite in task.users:
        return jsonify({'error': 'User is already a collaborator.'}), 400

    # Add user to task collaborators
    task.users.append(user_to_invite)
    db.session.commit()

    return jsonify({'message': f'{user_to_invite.email} has been added to the task.'}), 200


@main_bp.route('/add_comment', methods=['POST'])
@login_required
def add_comment():
    data = request.get_json()
    task_id = data.get('task_id')
    content = data.get('content')

    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or access denied.'}), 403

    if not content:
        return jsonify({'error': 'Comment content is required.'}), 400

    comment = Comment(content=content, task=task, user=current_user)
    db.session.add(comment)
    db.session.commit()

    return jsonify({'message': 'Comment added successfully.'}), 200

@main_bp.route('/get_comments')
@login_required
def get_comments():
    task_id = request.args.get('task_id')

    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or access denied.'}), 403

    comments = [{
        'id': comment.id,
        'content': comment.content,
        'timestamp': comment.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
        'user_email': comment.user.email
    } for comment in task.comments]

    return jsonify({'comments': comments}), 200

@main_bp.route('/search_users', methods=['GET'])
@login_required
def search_users():
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'results': []}), 200

    # Search users by name (case-insensitive) and exclude the current user
    users = User.query.filter(
        User.name.ilike(f"%{query}%"),  # Partial match on name
        User.id != current_user.id
    ).all()

    # Format the results
    results = [{'id': user.id, 'username': user.name} for user in users]
    return jsonify({'results': results}), 200

@main_bp.route('/add_friend', methods=['POST'])
@login_required
def add_friend():
    data = request.get_json()
    friend_id = data.get('friend_id')

    if not friend_id:
        return jsonify({'error': 'Friend ID is required.'}), 400

    existing_friendship = Friend.query.filter_by(user_id=current_user.id, friend_id=friend_id).first() or \
                          Friend.query.filter_by(user_id=friend_id, friend_id=current_user.id).first()

    if existing_friendship:
        return jsonify({'error': 'Friendship already exists.'}), 400

    new_friendship = Friend(user_id=current_user.id, friend_id=friend_id)
    db.session.add(new_friendship)
    db.session.commit()

    return jsonify({'message': 'Friend added successfully.'})

@main_bp.route('/get_friends')
@login_required
def get_friends():
    friends = Friend.query.filter(
        (Friend.user_id == current_user.id) | (Friend.friend_id == current_user.id)
    ).all()

    friend_list = []
    for friend in friends:
        friend_user = friend.friend if friend.user_id == current_user.id else friend.user
        friend_list.append({'id': friend_user.id, 'name': friend_user.name})

    return jsonify({'friends': friend_list}), 200

@main_bp.route('/invite_friends_to_task', methods=['POST'])
@login_required
def invite_friends_to_task():
    data = request.get_json()
    task_id = data.get('task_id')
    friend_ids = data.get('friend_ids', [])

    task = Task.query.get(task_id)
    if not task or current_user not in task.users:
        return jsonify({'error': 'Task not found or access denied.'}), 403

    invited_count = 0
    for friend_id in friend_ids:
        try:
            friend_user = User.query.get(int(friend_id))
            if friend_user and friend_user not in task.users:
                task.users.append(friend_user)
                invited_count += 1
        except ValueError:
            continue

    db.session.commit()

    return jsonify({'message': f'{invited_count} friends successfully invited.'}), 200

