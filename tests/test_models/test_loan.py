import pytest
from datetime import datetime, timedelta
from app import create_app, db
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User

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
        isbn='978-0-123456-47-2',
        title='Test Book',
        author='Test Author',
        total_copies=2
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
        full_name='Test User'
    )
    user.set_password('password123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def sample_loan(app, sample_user, sample_book):
    """Create a sample loan for testing."""
    loan = Loan(
        user_id=sample_user.id,
        book_id=sample_book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    db.session.add(loan)
    db.session.commit()
    return loan

class TestLoanModel:
    """Test cases for Loan model."""
    
    def test_loan_creation(self, app, sample_loan):
        """Test loan creation with all required fields."""
        assert sample_loan.id is not None
        assert sample_loan.user_id is not None
        assert sample_loan.book_id is not None
        assert sample_loan.loan_date is not None
        assert sample_loan.due_date is not None
        assert sample_loan.status == 'borrowed'
        assert sample_loan.return_date is None
    
    def test_loan_repr(self, app, sample_loan, sample_user, sample_book):
        """Test loan string representation."""
        expected_repr = f'<Loan {sample_loan.id}: {sample_user.username} borrowed {sample_book.title}>'
        assert str(sample_loan) == expected_repr
        assert repr(sample_loan) == expected_repr
    
    def test_loan_status_not_overdue(self, app, sample_loan):
        """Test loan that is not overdue."""
        assert sample_loan.is_overdue() is False
        assert sample_loan.get_status_display() == 'Đang mượn'
    
    def test_loan_status_overdue(self, app, sample_user, sample_book):
        """Test loan that is overdue."""
        overdue_loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() - timedelta(days=1)  # Due yesterday
        )
        db.session.add(overdue_loan)
        db.session.commit()
        
        assert overdue_loan.is_overdue() is True
        assert overdue_loan.get_status_display() == 'Quá hạn'
    
    def test_loan_status_returned(self, app, sample_loan):
        """Test loan that is returned."""
        sample_loan.status = 'returned'
        db.session.commit()
        
        assert sample_loan.is_overdue() is False
        assert sample_loan.get_status_display() == 'Đã trả'
    
    def test_days_remaining(self, app, sample_user, sample_book):
        """Test days remaining calculation."""
        # Loan due in 5 days
        future_loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=5)
        )
        db.session.add(future_loan)
        db.session.commit()
        
        days_remaining = future_loan.get_days_remaining()
        assert days_remaining >= 4  # Should be around 5 days
        assert days_remaining <= 5
        
        # Overdue loan
        overdue_loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() - timedelta(days=3)
        )
        db.session.add(overdue_loan)
        db.session.commit()
        
        assert overdue_loan.get_days_remaining() == 0
    
    def test_return_book(self, app, sample_loan):
        """Test returning a book."""
        assert sample_loan.status == 'borrowed'
        assert sample_loan.return_date is None
        
        sample_loan.return_book()
        db.session.commit()
        
        assert sample_loan.status == 'returned'
        assert sample_loan.return_date is not None
        assert sample_loan.get_status_display() == 'Đã trả'
        assert sample_loan.get_days_remaining() == 0
    
    def test_loan_relationships(self, app, sample_loan, sample_user, sample_book):
        """Test loan relationships."""
        # Test user relationship
        assert sample_loan.user.id == sample_user.id
        assert sample_loan.user.username == sample_user.username
        
        # Test book relationship
        assert sample_loan.book.id == sample_book.id
        assert sample_loan.book.title == sample_book.title
    
    def test_loan_date_defaults(self, app, sample_user, sample_book):
        """Test loan date defaults."""
        loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        # loan_date should be set automatically
        assert loan.loan_date is not None
        assert isinstance(loan.loan_date, datetime)
        
        # Should be close to current time
        time_diff = abs((loan.loan_date - datetime.utcnow()).total_seconds())
        assert time_diff < 10  # Within 10 seconds
    
    def test_loan_status_transitions(self, app, sample_user, sample_book):
        """Test loan status transitions."""
        loan = Loan(
            user_id=sample_user.id,
            book_id=sample_book.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Initial status
        assert loan.status == 'borrowed'
        assert loan.get_status_display() == 'Đang mượn'
        
        # Mark as overdue
        loan.due_date = datetime.utcnow() - timedelta(days=1)
        db.session.commit()
        
        assert loan.is_overdue() is True
        assert loan.get_status_display() == 'Quá hạn'
        
        # Return the book
        loan.return_book()
        db.session.commit()
        
        assert loan.status == 'returned'
        assert loan.get_status_display() == 'Đã trả'
        assert loan.is_overdue() is False
