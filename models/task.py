
from datetime import datetime
from extensions import db

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    completed = db.Column(db.Boolean, default=False)
    due_date = db.Column(db.DateTime, nullable=True)

    def __repr__(self):
        return f"<Task {self.id} - {self.title}>"

    @property
    def is_overdue(self) -> bool:
        return bool(self.due_date and self.due_date.date() < datetime.utcnow().date())



