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
def sample_book(app):
    """Create a sample book for testing."""
    book = Book(
        isbn='978-0-123456-47-4',
        title='Advanced Test Book',
        author='Advanced Author',
        publisher='Advanced Publisher',
        publication_year=2024,
        category='Non-Fiction',
        description='An advanced test book for comprehensive testing',
        total_copies=5,
        location='Shelf B2'
    )
    db.session.add(book)
    db.session.commit()
    return book

@pytest.fixture
def sample_user(app):
    """Create a sample user for testing."""
    user = User(
        username='advanceduser',
        email='advanced@example.com',
        full_name='Advanced User'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

class TestBookAdvancedFeatures:
    """Test advanced book features."""
    
    def test_book_initialization(self, app, sample_book):
        """Test book initialization with all fields."""
        assert sample_book.isbn == '978-0-123456-47-4'
        assert sample_book.title == 'Advanced Test Book'
        assert sample_book.author == 'Advanced Author'
        assert sample_book.publisher == 'Advanced Publisher'
        assert sample_book.publication_year == 2024
        assert sample_book.category == 'Non-Fiction'
        assert sample_book.description == 'An advanced test book for comprehensive testing'
        assert sample_book.total_copies == 5
        assert sample_book.location == 'Shelf B2'
        assert sample_book.is_active is True
        assert sample_book.created_at is not None
    
    def test_book_availability_edge_cases(self, app, sample_book):
        """Test book availability edge cases."""
        # Test with 0 total copies
        sample_book.total_copies = 0
        db.session.commit()
        
        assert sample_book.get_available_copies_count() == 0
        assert sample_book.is_available() is False
        assert sample_book.get_availability_status() == 'unavailable'
        
        # Test with negative total copies (edge case)
        sample_book.total_copies = -1
        db.session.commit()
        
        assert sample_book.get_available_copies_count() == -1
        assert sample_book.is_available() is False
    
    def test_book_inactive_status(self, app, sample_book):
        """Test book inactive status."""
        sample_book.is_active = False
        db.session.commit()
        
        assert sample_book.is_available() is False
        assert sample_book.get_availability_status() == 'inactive'
        
        display = sample_book.get_availability_display()
        assert display['status'] == 'inactive'
        assert display['text'] == 'Không hoạt động'
        assert display['badge_class'] == 'bg-secondary'
    
    def test_book_limited_availability(self, app, sample_book, sample_user):
        """Test book with limited availability."""
        # Borrow 3 out of 5 copies
        for i in range(3):
            loan = Loan(
                user_id=sample_user.id,
                book_id=sample_book.id,
                due_date=datetime.utcnow() + timedelta(days=14)
            )
            db.session.add(loan)
        
        db.session.commit()
        db.session.refresh(sample_book)
        
        assert sample_book.get_available_copies_count() == 2
        assert sample_book.get_availability_status() == 'limited'
        
        display = sample_book.get_availability_display()
        assert display['status'] == 'limited'
        assert display['text'] == 'Còn 2 cuốn'
        assert display['badge_class'] == 'bg-warning'
        assert display['available'] == 2
        assert display['borrowed'] == 3
        assert display['total'] == 5
    
    def test_book_full_availability(self, app, sample_book):
        """Test book with full availability."""
        assert sample_book.get_available_copies_count() == 5
        assert sample_book.get_availability_status() == 'available'
        
        display = sample_book.get_availability_display()
        assert display['status'] == 'available'
        assert display['text'] == 'Có sẵn'
        assert display['badge_class'] == 'bg-success'
        assert display['available'] == 5
        assert display['borrowed'] == 0
        assert display['total'] == 5
    
    def test_book_can_borrow_validation(self, app, sample_book, sample_user):
        """Test book borrow validation."""
        # Test normal case
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is True
        assert message == "Có thể mượn"
        
        # Test with inactive book
        sample_book.is_active = False
        db.session.commit()
        
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is False
        assert "không có sẵn" in message or "unavailable" in message
        
        # Test with no available copies
        sample_book.is_active = True
        sample_book.total_copies = 0
        db.session.commit()
        
        can_borrow, message = sample_book.can_borrow(sample_user.id)
        assert can_borrow is False
        assert "không có sẵn" in message or "unavailable" in message
    
    def test_book_update_availability(self, app, sample_book, sample_user):
        """Test book availability update."""
        # Initial state
        assert sample_book.available_copies == 5
        
        # Borrow a book
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
        
        assert sample_book.available_copies == 4
        assert sample_book.get_available_copies_count() == 4
