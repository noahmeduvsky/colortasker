from extensions import db

class Folder(db.Model):
    __tablename__ = 'folders'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    owner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

    # Relationships
    tasks = db.relationship('Task', backref='folder', lazy='dynamic')

    # ... any additional methods or attributes ...
