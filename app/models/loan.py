from app import db
from datetime import datetime

class Loan(db.Model):
    __tablename__ = 'loans'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    book_id = db.Column(db.Integer, db.ForeignKey('books.id'), nullable=False)
    loan_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    due_date = db.Column(db.DateTime, nullable=False)
    return_date = db.Column(db.DateTime)
    status = db.Column(db.String(20), default='borrowed')  # borrowed, returned, overdue
    
    # Relationships - sử dụng back_populates để tránh conflict
    user = db.relationship('User', back_populates='loans')
    book = db.relationship('Book', back_populates='loans')
    
    def __repr__(self):
        return f'<Loan {self.id}: {self.user.username} borrowed {self.book.title}>'
    
    def is_overdue(self):
        if self.status == 'returned':
            return False
        return datetime.utcnow() > self.due_date
    
    def get_status_display(self):
        if self.status == 'returned':
            return 'Đã trả'
        elif self.is_overdue():
            return 'Quá hạn'
        else:
            return 'Đang mượn'
    
    def get_days_remaining(self):
        if self.status == 'returned':
            return 0
        remaining = self.due_date - datetime.utcnow()
        return max(0, remaining.days)
    
    def return_book(self):
        """Trả sách"""
        self.status = 'returned'
        self.return_date = datetime.utcnow() 
    
    def get_days_overdue(self):
        """Lấy số ngày quá hạn"""
        if self.status == 'returned' or not self.is_overdue():
            return 0
        overdue = datetime.utcnow() - self.due_date
        return overdue.days 