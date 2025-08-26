import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.book import Book
from app.models.user import User
from app.models.loan import Loan

@pytest.fixture
def app():
    """Create application for the tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()

@pytest.fixture
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture
def sample_book(app):
    """Create a sample book for testing."""
    book = Book(
        isbn='978-0-123456-47-2',
        title='Test Book',
        author='Test Author',
        publisher='Test Publisher',
        publication_year=2023,
        category='Fiction',
        description='A test book for testing purposes',
        total_copies=3,
        location='Shelf A1'
    )
    db.session.add(book)
    db.session.commit()
    return book

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='user'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

class TestBookModel:
    """Test cases for Book model."""
    
    def test_book_creation(self, app, sample_book):
        """Test book creation with all required fields."""
        assert sample_book.id is not None
        assert sample_book.isbn == '978-0-123456-47-2'
        assert sample_book.title == 'Test Book'
        assert sample_book.author == 'Test Author'
        assert sample_book.total_copies == 3
        assert sample_book.available_copies == 3
        assert sample_book.is_active is True
    
    def test_book_repr(self, app, sample_book):
        """Test book string representation."""
        assert str(sample_book) == '<Book Test Book>'
        assert repr(sample_book) == '<Book Test Book>'
    
    def test_book_availability(self, app, sample_book):
        """Test book availability methods."""
        assert sample_book.is_available() is True
        assert sample_book.get_available_copies_count() == 3
        assert sample_book.get_borrowed_copies() == 0
        assert sample_book.get_availability_status() == 'available'
    
    def test_book_with_loans(self, app, sample_book, sample_user):
        """Test book availability when it has loans."""
        # Create a loan
        loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Refresh book to get updated availability
        db.session.refresh(sample_book)
        
        assert sample_book.get_borrowed_copies() == 1
        assert sample_book.get_available_copies_count() == 2
        assert sample_book.is_available() is True
        assert sample_book.get_availability_status() == 'limited'
    
    def test_book_unavailable(self, app, sample_book, sample_user):
        """Test book when all copies are borrowed."""
        # Borrow all copies
        for i in range(3):
            loan = Loan(
                user_id=sample_user.id,
                book_id=sample_book.id,
                due_date=datetime.utcnow() + timedelta(days=14)
            )
            db.session.add(loan)
        
        db.session.commit()
        db.session.refresh(sample_book)
        
        assert sample_book.get_borrowed_copies() == 3
        assert sample_book.get_available_copies_count() == 0
        assert sample_book.is_available() is False
        assert sample_book.get_availability_status() == 'unavailable'
    
    def test_book_inactive(self, app, sample_book):
        """Test inactive book."""
        sample_book.is_active = False
        db.session.commit()
        
        assert sample_book.is_available() is False
        assert sample_book.get_availability_status() == 'inactive'
    
    def test_can_borrow(self, app, sample_book, sample_user):
        """Test if user can borrow book."""
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is True
        assert message == "Có thể mượn"
    
    def test_cannot_borrow_already_borrowed(self, app, sample_book, sample_user):
        """Test if user cannot borrow already borrowed book."""
        # Create a loan
        loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is False
        assert message == "Bạn đã mượn sách này rồi"
    
    def test_cannot_borrow_unavailable(self, app, sample_book, sample_user):
        """Test if user cannot borrow unavailable book."""
        # Make all copies unavailable
        sample_book.total_copies = 0
        db.session.commit()
        
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is False
        assert message == "Sách không có sẵn hoặc không hoạt động"
    
    def test_availability_display(self, app, sample_book):
        """Test availability display information."""
        display = sample_book.get_availability_display()
        
        assert display['status'] == 'available'
        assert display['text'] == 'Có sẵn'
        assert display['badge_class'] == 'bg-success'
        assert display['available'] == 3
        assert display['borrowed'] == 0
        assert display['total'] == 3
    
    def test_update_availability(self, app, sample_book, sample_user):
        """Test updating book availability."""
        # Create a loan
        loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Update availability
        sample_book.update_availability()
        db.session.commit()
        
        assert sample_book.available_copies == 2
        assert sample_book.get_available_copies_count() == 2
