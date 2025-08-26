from app import db
from datetime import datetime

class Book(db.Model):
    __tablename__ = 'books'
    
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String(20), unique=True, nullable=False)
    title = db.Column(db.String(200), nullable=False)
    author = db.Column(db.String(100), nullable=False)
    publisher = db.Column(db.String(100))
    publication_year = db.Column(db.Integer)
    category = db.Column(db.String(50))
    description = db.Column(db.Text)
    total_copies = db.Column(db.Integer, default=1)
    available_copies = db.Column(db.Integer, default=1)  # Giữ lại để tương thích
    location = db.Column(db.String(100))
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Sử dụng back_populates thay vì backref
    loans = db.relationship('Loan', back_populates='book')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Tự động cập nhật available_copies khi khởi tạo
        self.update_availability()
    
    def is_available(self):
        """Kiểm tra sách có thể mượn được không"""
        return self.get_available_copies_count() > 0 and self.is_active
    
    def get_borrowed_copies(self):
        """Lấy số cuốn sách đang được mượn"""
        from app.models.loan import Loan
        return Loan.query.filter_by(
            book_id=self.id,
            status='borrowed'
        ).count()
    
    def get_available_copies_count(self):
        """Tính toán số cuốn sách có sẵn thực tế"""
        return self.total_copies - self.get_borrowed_copies()
    
    @property
    def available_copies_display(self):
        """Property để hiển thị available_copies (tính toán động)"""
        return self.get_available_copies_count()
    
    def can_borrow(self, user_id):
        """Kiểm tra user có thể mượn sách này không"""
        if not self.is_available():
            return False, "Sách không có sẵn hoặc không hoạt động"
        
        # Kiểm tra user đã mượn sách này chưa
        from app.models.loan import Loan
        existing_loan = Loan.query.filter_by(
            user_id=user_id,
            book_id=self.id,
            status='borrowed'
        ).first()
        
        if existing_loan:
            return False, "Bạn đã mượn sách này rồi"
        
        return True, "Có thể mượn"
    
    def update_availability(self):
        """Cập nhật available_copies dựa trên thực tế"""
        borrowed_count = self.get_borrowed_copies()
        self.available_copies = self.total_copies - borrowed_count
    
    def get_availability_status(self):
        """Lấy trạng thái sách"""
        if not self.is_active:
            return 'inactive'
        
        available = self.get_available_copies_count()
        if available == 0:
            return 'unavailable'
        elif available < self.total_copies:
            return 'limited'
        else:
            return 'available'
    
    def get_availability_display(self):
        """Lấy thông tin hiển thị về tình trạng sách"""
        status = self.get_availability_status()
        available = self.get_available_copies_count()
        borrowed = self.get_borrowed_copies()
        
        if status == 'inactive':
            return {
                'status': 'inactive',
                'text': 'Không hoạt động',
                'badge_class': 'bg-secondary',
                'available': 0,
                'borrowed': borrowed,
                'total': self.total_copies
            }
        elif status == 'unavailable':
            return {
                'status': 'unavailable',
                'text': 'Hết sách',
                'badge_class': 'bg-danger',
                'available': 0,
                'borrowed': borrowed,
                'total': self.total_copies
            }
        elif status == 'limited':
            return {
                'status': 'limited',
                'text': f'Còn {available} cuốn',
                'badge_class': 'bg-warning',
                'available': available,
                'borrowed': borrowed,
                'total': self.total_copies
            }
        else:
            return {
                'status': 'available',
                'text': 'Có sẵn',
                'badge_class': 'bg-success',
                'available': available,
                'borrowed': borrowed,
                'total': self.total_copies
            }
    
    def __repr__(self):
        return f'<Book {self.title}>' 