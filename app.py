from flask import Flask, render_template, request, redirect, url_for, jsonify, session, flash
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for session handling

# Example in-memory data structures for demonstration
folders = []
users = []

class Folder:
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.tasks = []

class Task:
    def __init__(self, id, name, color, deadline, users=None):
        self.id = id
        self.name = name
        self.color = color
        self.deadline = deadline
        self.users = users if users else []  # List of assigned users

class User:
    def __init__(self, id, name, password):
        self.id = id
        self.name = name
        self.password = password

# Route for the login page
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = next((u for u in users if u.name == username and u.password == password), None)
        
        if user:
            session['user_id'] = user.id
            return redirect(url_for('index'))
        else:
            flash('Invalid username or password')
    
    return render_template('login.html')

# Route for the signup page
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Check if user already exists
        if next((u for u in users if u.name == username), None):
            flash('Username already exists')
            return redirect(url_for('signup'))
        
        new_user = User(id=len(users) + 1, name=username, password=password)
        users.append(new_user)
        session['user_id'] = new_user.id  # Log the user in immediately after signup
        return redirect(url_for('index'))
    
    return render_template('signup.html')

# Route for logging out
@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

# Route for the homepage showing all folders and users
@app.route('/')
def index():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    return render_template('index.html', folders=folders, users=users)

# Route to add a new folder
@app.route('/add_folder', methods=['POST'])
def add_folder():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder_name = request.form['folder_name']
    new_folder = Folder(id=len(folders) + 1, name=folder_name)
    folders.append(new_folder)
    return redirect(url_for('index'))

# Route to delete a folder
@app.route('/delete_folder/<int:folder_id>', methods=['POST'])
def delete_folder(folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    global folders
    folders = [folder for folder in folders if folder.id != folder_id]
    return redirect(url_for('index'))

# Route to add a new user with a password
@app.route('/add_user', methods=['POST'])
def add_user():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user_name = request.form['user_name']
    password = request.form['password']
    new_user = User(id=len(users) + 1, name=user_name, password=password)
    users.append(new_user)
    return redirect(url_for('index'))

# Route to delete a user
@app.route('/delete_user/<int:user_id>', methods=['POST'])
def delete_user(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    global users
    users = [user for user in users if user.id != user_id]
    return redirect(url_for('index'))

# Route for viewing a specific folder and its tasks
@app.route('/folder/<int:folder_id>')
def folder_page(folder_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    folder = next((f for f in folders if f.id == folder_id), None)
    today = datetime.today().strftime('%Y-%m-%d')  # Current date in YYYY-MM-DD format
    return render_template('folder.html', folder=folder, today=today, users=users)

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

    # Find the selected users by their IDs
    assigned_users = [user for user in users if str(user.id) in user_ids]

    # Ensure at least one user is assigned
    if not assigned_users:
        return redirect(url_for('folder_page', folder_id=folder_id))  # Redirect back if no users selected

    new_task = Task(id=len(folders[folder_id-1].tasks) + 1, name=task_name, color=color, deadline=deadline, users=assigned_users)
    
    # Find the folder to which the task should be added
    folder = next((f for f in folders if f.id == folder_id), None)
    if folder:
        folder.tasks.append(new_task)

    return redirect(url_for('folder_page', folder_id=folder_id))

# Route to view tasks assigned to a specific user
@app.route('/user/<int:user_id>/tasks', methods=['POST'])
def user_tasks(user_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    # Get the password from the request form for validation
    entered_password = request.form['password']
    user = next((u for u in users if u.id == user_id), None)
    
    if user and user.password == entered_password:
        # Gather all tasks assigned to this user across folders
        user_tasks = []
        for folder in folders:
            for task in folder.tasks:
                if user in task.users:
                    user_tasks.append({
                        'task': task,
                        'folder': folder.name  # Include folder name for context
                    })

        return render_template('user_tasks.html', user=user, user_tasks=user_tasks)
    else:
        flash("Invalid password")
        return redirect(url_for('index'))

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
    
    # Generate a list of days for the current month (assuming a 30-day month for simplicity)
    today = datetime.now()
    month_days = [{'day': day, 'date': today.replace(day=day).strftime('%Y-%m-%d')} for day in range(1, 31)]
    return render_template('calendar.html', month_days=month_days)

# Route to handle fetching tasks for a specific day
@app.route('/tasks_for_day', methods=['POST'])
def tasks_for_day():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    data = request.get_json()
    date = data['date']  # Expected format: YYYY-MM-DD

    # Gather tasks with the specified date
    tasks_for_date = []
    for folder in folders:
        for task in folder.tasks:
            if task.deadline and task.deadline.strftime('%Y-%m-%d') == date:
                tasks_for_date.append({
                    'name': task.name,
                    'folder': folder.name,
                    'color': task.color
                })

    return jsonify(tasks_for_date)

if __name__ == '__main__':
    app.run(debug=True)
