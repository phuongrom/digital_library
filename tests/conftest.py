import os
import sys
import tempfile
import pytest

# Add the project root directory to Python path
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from app import create_app, db
from app.models.book import Book
from app.models.user import User
from app.models.loan import Loan

@pytest.fixture(scope='session')
def app():
    """Create application for the tests."""
    app = create_app()
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    app.config['WTF_CSRF_ENABLED'] = False
    app.config['SECRET_KEY'] = 'test-secret-key'
    
    return app

@pytest.fixture(scope='function')
def client(app):
    """Create test client."""
    return app.test_client()

@pytest.fixture(scope='function')
def app_context(app):
    """Create application context."""
    with app.app_context():
        yield app

@pytest.fixture(scope='function')
def db_session(app_context):
    """Create database session."""
    db.create_all()
    yield db
    db.session.remove()
    db.drop_all()

@pytest.fixture
def sample_user(db_session):
    """Create a sample user for testing."""
    user = User(
        username='testuser',
        email='test@example.com',
        full_name='Test User',
        role='user'
    )
    user.set_password('password123')
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture
def admin_user(db_session):
    """Create an admin user for testing."""
    user = User(
        username='admin',
        email='admin@example.com',
        full_name='Admin User',
        role='admin'
    )
    user.set_password('admin123')
    db_session.session.add(user)
    db_session.session.commit()
    return user

@pytest.fixture
def sample_book(db_session):
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
    db_session.session.add(book)
    db_session.session.commit()
    return book

@pytest.fixture
def sample_loan(db_session, sample_user, sample_book):
    """Create a sample loan for testing."""
    from datetime import datetime, timedelta
    
    loan = Loan(
        user_id=sample_user.id,
        book_id=sample_book.id,
        due_date=datetime.utcnow() + timedelta(days=14)
    )
    db_session.session.add(loan)
    db_session.session.commit()
    return loan
