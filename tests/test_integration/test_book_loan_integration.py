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
def sample_data(app):
    """Create sample data for integration tests."""
    # Create users with unique usernames
    user1 = User(username='user1', email='user1@example.com', full_name='User One')
    user1.set_password('password123')
    
    user2 = User(username='user2', email='user2@example.com', full_name='User Two')
    user2.set_password('password123')
    
    admin = User(username='admin1', email='admin1@example.com', full_name='Admin User', role='admin')
    admin.set_password('admin123')
    
    db.session.add_all([user1, user2, admin])
    
    # Create books with unique ISBNs
    book1 = Book(
        isbn='978-0-123456-47-2',
        title='Book One',
        author='Author One',
        total_copies=2
    )
    
    book2 = Book(
        isbn='978-0-123456-47-3',
        title='Book Two',
        author='Author Two',
        total_copies=1
    )
    
    db.session.add_all([book1, book2])
    db.session.commit()
    
    return {
        'users': [user1, user2, admin],
        'books': [book1, book2]
    }

class TestBookLoanIntegration:
    """Integration tests for book loan functionality."""
    
    @pytest.mark.integration
    def test_complete_loan_cycle(self, app, sample_data):
        """Test complete loan cycle: borrow -> check availability -> return."""
        user1 = sample_data['users'][0]
        book1 = sample_data['books'][0]
        
        # Initial state
        assert book1.get_available_copies_count() == 2
        assert book1.is_available() is True
        
        # Create loan
        loan = Loan(
            user_id=user1.id,
            book_id=book1.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan)
        db.session.commit()
        
        # Check book availability after loan
        db.session.refresh(book1)
        assert book1.get_available_copies_count() == 1
        assert book1.is_available() is True
        
        # Create second loan
        loan2 = Loan(
            user_id=user1.id,
            book_id=book1.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan2)
        db.session.commit()
        
        # Check book availability after second loan
        db.session.refresh(book1)
        assert book1.get_available_copies_count() == 0
        assert book1.is_available() is False
        
        # Return first book
        loan.status = 'returned'
        loan.return_date = datetime.utcnow()
        db.session.commit()
        
        # Check book availability after return
        db.session.refresh(book1)
        assert book1.get_available_copies_count() == 1
        assert book1.is_available() is True
    
    @pytest.mark.integration
    def test_multiple_users_loan_same_book(self, app, sample_data):
        """Test multiple users trying to loan the same book."""
        user1 = sample_data['users'][0]
        user2 = sample_data['users'][1]
        book2 = sample_data['books'][1]  # Only 1 copy available
        
        # User1 borrows the book
        loan1 = Loan(
            user_id=user1.id,
            book_id=book2.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan1)
        db.session.commit()
        
        # Check book availability
        db.session.refresh(book2)
        assert book2.get_available_copies_count() == 0
        assert book2.is_available() is False
        
        # User2 tries to borrow the same book
        can_borrow, message = book2.can_borrow(user2.id)
        assert can_borrow is False
        assert "không có sẵn" in message or "unavailable" in message
    
    @pytest.mark.integration
    def test_user_loan_limit(self, app, sample_data):
        """Test user cannot borrow the same book multiple times."""
        user1 = sample_data['users'][0]
        book1 = sample_data['books'][0]
        
        # First loan
        loan1 = Loan(
            user_id=user1.id,
            book_id=book1.id,
            due_date=datetime.utcnow() + timedelta(days=14)
        )
        db.session.add(loan1)
        db.session.commit()
        
        # Try to borrow the same book again
        can_borrow, message = book1.can_borrow(user1.id)
        assert can_borrow is False
        assert "đã mượn" in message or "already borrowed" in message
    
    @pytest.mark.integration
    def test_overdue_loan_handling(self, app, sample_data):
        """Test handling of overdue loans."""
        user1 = sample_data['users'][0]
        book1 = sample_data['books'][0]
        
        # Create overdue loan
        overdue_loan = Loan(
            user_id=user1.id,
            book_id=book1.id,
            due_date=datetime.utcnow() - timedelta(days=5)  # 5 days overdue
        )
        db.session.add(overdue_loan)
        db.session.commit()
        
        # Check loan status
        assert overdue_loan.is_overdue() is True
        assert overdue_loan.get_status_display() == 'Quá hạn'
        
        # Book should still be marked as borrowed
        db.session.refresh(book1)
        assert book1.get_borrowed_copies() == 1
        assert book1.get_available_copies_count() == 1  # 2 total - 1 borrowed
