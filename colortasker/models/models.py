from colortasker.extensions import db
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

task_user = db.Table('task_user',
    db.Column('task_id', db.Integer, db.ForeignKey('tasks.id'), primary_key=True),
    db.Column('user_id', db.Integer, db.ForeignKey('users.id'), primary_key=True)
)

class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    tasks = db.relationship('Task', backref='folder', lazy='dynamic')



class Task(db.Model):
    __tablename__ = 'tasks'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)
    color = db.Column(db.String(50))
    deadline = db.Column(db.Date)
    is_complete = db.Column(db.Boolean, default=False)
    folder_id = db.Column(db.Integer, db.ForeignKey('folders.id'), nullable=False)
    users = db.relationship('User', secondary=task_user, back_populates='tasks')

    def __init__(self, name, description, color, deadline, folder_id):
        self.name = name
        self.description = description
        self.color = color
        self.deadline = deadline
        self.folder_id = folder_id

class User(db.Model, UserMixin):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)

    # Relationships
    folders = db.relationship('Folder', backref='owner', lazy=True)
    tasks = db.relationship('Task', secondary=task_user, back_populates='users')


    def __init__(self, name, email, password):
        self.name = name
        self.email = email
        self.set_password(password)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

