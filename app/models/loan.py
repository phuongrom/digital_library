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
    status = db.Column(db.String(20), default='pending')  # pending, approved, borrowed, return_requested, extend_requested, returned, overdue, rejected
    
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
        elif self.status == 'pending':
            return 'Chờ duyệt mượn'
        elif self.status == 'approved':
            return 'Đã duyệt mượn'
        elif self.status == 'borrowed':
            return 'Đang mượn'
        elif self.status == 'return_requested':
            return 'Chờ duyệt trả'
        elif self.status == 'extend_requested':
            return 'Chờ duyệt gia hạn'
        elif self.status == 'rejected':
            return 'Từ chối'
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
    
    def approve(self):
        """Duyệt yêu cầu mượn sách"""
        self.status = 'borrowed'
        # Cập nhật available_copies của sách
        self.book.update_availability()
    
    def reject(self):
        """Từ chối yêu cầu mượn sách"""
        self.status = 'rejected'
        # Cập nhật available_copies của sách
        self.book.update_availability()
    
    def is_pending(self):
        """Kiểm tra loan có đang chờ duyệt không"""
        return self.status == 'pending'
    
    def is_approved(self):
        """Kiểm tra loan đã được duyệt chưa"""
        return self.status == 'borrowed'
    
    def request_return(self):
        """Yêu cầu trả sách"""
        if self.status == 'borrowed':
            self.status = 'return_requested'
    
    def request_extension(self, days=7):
        """Yêu cầu gia hạn sách"""
        if self.status == 'borrowed' and not self.is_overdue():
            self.status = 'extend_requested'
            # Tạm thời cập nhật due_date, sẽ được confirm khi admin duyệt
            from datetime import timedelta
            self.due_date = self.due_date + timedelta(days=days)
    
    def approve_return(self):
        """Admin duyệt trả sách"""
        if self.status == 'return_requested':
            self.status = 'returned'
            self.return_date = datetime.utcnow()
            # Cập nhật available_copies của sách
            self.book.update_availability()
    
    def approve_extension(self):
        """Admin duyệt gia hạn"""
        if self.status == 'extend_requested':
            self.status = 'borrowed'
            # Cập nhật available_copies của sách
            self.book.update_availability()
    
    def reject_return(self):
        """Admin từ chối trả sách"""
        if self.status == 'return_requested':
            self.status = 'borrowed'
    
    def reject_extension(self):
        """Admin từ chối gia hạn"""
        if self.status == 'extend_requested':
            self.status = 'borrowed'
            # Khôi phục due_date cũ
            from datetime import timedelta
            self.due_date = self.due_date - timedelta(days=7) 
