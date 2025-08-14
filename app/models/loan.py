from app import db
from datetime import datetime

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
    
    user = db.relationship('User', foreign_keys=[user_id])
    book = db.relationship('Book', foreign_keys=[book_id])
    
    def is_overdue(self):
        if self.status == 'returned':
            return False
        if self.due_date:
            return datetime.now() > self.due_date
        return False
    
    def get_days_overdue(self):
        if not self.is_overdue():
            return 0
        if self.due_date:
            return (datetime.now() - self.due_date).days
        return 0
    
    def return_book(self):
        self.status = 'returned'
        self.return_date = datetime.now()
    
    def get_status_display(self):
        if self.status == 'returned':
            return 'Đã trả'
        elif self.is_overdue():
            return 'Quá hạn'
        else:
            return 'Đang mượn'
    
    def __repr__(self):
        return f'<Loan {self.id}: {self.book_id} -> {self.user_id}>' 