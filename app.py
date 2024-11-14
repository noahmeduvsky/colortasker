from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime
import re

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# Example in-memory data structures for demonstration
folders = []
users = []
friendships = {}  # Dictionary to store friendships {user_id: [list of friend_ids]}

class Folder:
    def __init__(self, id, name, assigned_users=None):
        self.id = id
        self.name = name
        self.tasks = []
        self.assigned_users = assigned_users if assigned_users else []  # List of assigned users

class Task:
    def __init__(self, id, name, color, deadline, users=None):
        self.id = id
        self.name = name
        self.color = color
        self.deadline = deadline
        self.users = users if users else []  # List of assigned users

class User:
    def __init__(self, id, name, email, password):
        self.id = id
        self.name = name
        self.email = email
        self.password = password

# Function to validate email format
def is_valid_email(email):
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    return re.match(pattern, email)

# Route for the signup page with password confirmation and email validation
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm_password']

        # Check if email is valid
        if not is_valid_email(email):
            flash('Invalid email address.')
            return redirect(url_for('signup'))

        # Check if passwords match
        if password != confirm_password:
            flash('Passwords do not match.')
            return redirect(url_for('signup'))

        # Check if user already exists
        if next((u for u in users if u.name == username or u.email == email), None):
            flash('Username or email already exists.')
            return redirect(url_for('signup'))

        new_user = User(id=len(users) + 1, name=username, email=email, password=password)
        users.append(new_user)
        session['user_id'] = new_user.id  # Log the user in immediately after signup
        friendships[new_user.id] = []  # Initialize friendships list for the new user
        return redirect(url_for('index'))
    
    return render_template('signup.html')

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u.name == username and u.password == password), None)
        
        if user:
            session['user_id'] = user.id
            # Ensure the user has an entry in the friendships dictionary
            if user.id not in friendships:
                friendships[user.id] = []
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    current_user = next((u for u in users if u.id == user_id), None)
    user_folders = [folder for folder in folders if current_user in folder.assigned_users]
    
    # Get the list of friends' User objects for the logged-in user
    friend_ids = friendships.get(user_id, [])
    friends = [user for user in users if user.id in friend_ids]
    
    return render_template('index.html', folders=user_folders, users=users, friends=friends, current_user=current_user)

# Route to add a new folder with assigned users
@app.route('/add_folder', methods=['POST'])
def add_folder():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder_name = request.form['folder_name']
    user_id = session['user_id']
    
    # Get selected friend IDs for the folder (can be empty)
    friend_ids = request.form.getlist('assigned_users')  # Get selected friend IDs as strings
    assigned_users = [user for user in users if str(user.id) in friend_ids]

    # Add the current logged-in user to the assigned users list
    current_user = next((u for u in users if u.id == user_id), None)
    if current_user:
        assigned_users.append(current_user)  # Ensure the logged-in user is included

    # Create the new folder with the name and assigned users (including the logged-in user)
    new_folder = Folder(id=len(folders) + 1, name=folder_name, assigned_users=assigned_users)
    folders.append(new_folder)
    
    return redirect(url_for('index'))

@app.route('/folder/<int:folder_id>')
def folder_page(folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder = next((f for f in folders if f.id == folder_id), None)
    if not folder:
        flash("Folder not found.", "warning")
        return redirect(url_for('index'))
    
    # Get friends of the logged-in user for task assignment
    user_id = session['user_id']
    current_user = next((u for u in users if u.id == user_id), None)
    friend_ids = friendships.get(user_id, [])
    friends = [user for user in users if user.id in friend_ids]
    
    return render_template('folder.html', folder=folder, friends=friends, current_user=current_user)

# Route to add a new task to a specific folder with deadline and assigned users
@app.route('/add_task', methods=['POST'])
def add_task():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder_id = int(request.form['folder_id'])
    task_name = request.form['task_name']
    color = request.form['color']
    deadline_str = request.form['deadline']
    user_ids = request.form.getlist('assigned_users')  # Get selected user IDs

    try:
        deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    except ValueError:
        deadline = None  # Handle invalid date format by setting deadline to None

    # Automatically assign to the current user if no users are selected
    current_user_id = session['user_id']
    assigned_users = [user for user in users if str(user.id) in user_ids]
    if not assigned_users:
        current_user = next((u for u in users if u.id == current_user_id), None)
        if current_user:
            assigned_users.append(current_user)

    new_task = Task(id=len(folders[folder_id-1].tasks) + 1, name=task_name, color=color, deadline=deadline, users=assigned_users)
    folder = next((f for f in folders if f.id == folder_id), None)
    if folder:
        folder.tasks.append(new_task)

    return redirect(url_for('folder_page', folder_id=folder_id))

# Route to delete a folder
@app.route('/delete_folder/<int:folder_id>', methods=['POST'])
def delete_folder(folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    global folders
    folders = [folder for folder in folders if folder.id != folder_id]
    return redirect(url_for('index'))

# Route to edit a folder's name and assigned users
@app.route('/edit_folder/<int:folder_id>', methods=['POST'])
def edit_folder(folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    folder = next((f for f in folders if f.id == folder_id), None)
    if not folder:
        flash("Folder not found.", "warning")
        return redirect(url_for('index'))

    folder_name = request.form['folder_name']
    friend_ids = request.form.getlist('assigned_users')

    # Update folder name and assigned users
    folder.name = folder_name
    folder.assigned_users = [user for user in users if str(user.id) in friend_ids]
    
    flash("Folder updated successfully!", "success")
    return redirect(url_for('index'))

# Route to edit a task's name, deadline, color, and assigned users
@app.route('/edit_task/<int:task_id>/<int:folder_id>', methods=['POST'])
def edit_task(task_id, folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))

    folder = next((f for f in folders if f.id == folder_id), None)
    if not folder:
        flash("Folder not found.", "warning")
        return redirect(url_for('folder_page', folder_id=folder_id))

    task = next((t for t in folder.tasks if t.id == task_id), None)
    if not task:
        flash("Task not found.", "warning")
        return redirect(url_for('folder_page', folder_id=folder_id))

    # Update task details
    task.name = request.form['task_name']
    task.color = request.form['color']
    deadline_str = request.form['deadline']
    friend_ids = request.form.getlist('assigned_users')
    try:
        task.deadline = datetime.strptime(deadline_str, '%Y-%m-%d')
    except ValueError:
        flash("Invalid date format.", "warning")

    task.users = [user for user in users if str(user.id) in friend_ids]
    
    flash("Task updated successfully!", "success")
    return redirect(url_for('folder_page', folder_id=folder_id))

# Route to delete a task from a specific folder
@app.route('/delete_task/<int:task_id>/<int:folder_id>', methods=['POST'])
def delete_task(task_id, folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder = next((f for f in folders if f.id == folder_id), None)
    if folder:
        folder.tasks = [task for task in folder.tasks if task.id != task_id]
    return redirect(url_for('folder_page', folder_id=folder_id))

# Route to display the calendar
@app.route('/calendar')
def calendar():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    today = datetime.now()
    month_days = [{'day': day, 'date': today.replace(day=day).strftime('%Y-%m-%d')} for day in range(1, 31)]
    return render_template('calendar.html', month_days=month_days)

# Route to handle fetching tasks for a specific day
@app.route('/tasks_for_day', methods=['POST'])
def tasks_for_day():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    date = data['date']

    tasks_for_date = []
    for folder in folders:
        for task in folder.tasks:
            if task.deadline and task.deadline.strftime('%Y-%m-%d') == date:
                tasks_for_date.append({'name': task.name, 'folder': folder.name, 'color': task.color})

    return jsonify(tasks_for_date)

# Route to search for users by name for friend suggestions
@app.route('/search_users', methods=['POST'])
def search_users():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    search_query = data.get('search_query', '').lower()
    user_id = session['user_id']
    suggestions = [
        {'id': user.id, 'name': user.name} for user in users 
        if search_query in user.name.lower() and user.id != user_id
    ]
    return jsonify(suggestions)

# Route to add a friend
@app.route('/add_friend', methods=['POST'])
def add_friend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    friend_id = int(request.form['friend_id'])
    
    if friend_id not in friendships[user_id]:
        friendships[user_id].append(friend_id)
        friendships[friend_id].append(user_id)  # Add reciprocal friendship
        flash('Friend added successfully!', 'success')
    else:
        flash('This user is already your friend.', 'warning')
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
