import pytest
from datetime import datetime, timedelta
from app import create_app, db
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

@pytest.fixture
def admin_user(app):
    """Create an admin user for testing."""
    user = User(
        username='admin',
        email='admin@example.com',
        full_name='Admin User',
        role='admin'
    )
    user.set_password('admin123')
    db.session.add(user)
    db.session.commit()
    return user

@pytest.fixture
def librarian_user(app):
    """Create a librarian user for testing."""
    user = User(
        username='librarian',
        email='librarian@example.com',
        full_name='Librarian User',
        role='librarian'
    )
    user.set_password('lib123')
    db.session.add(user)
    db.session.commit()
    return user

class TestUserModel:
    """Test cases for User model."""
    
    def test_user_creation(self, app, sample_user):
        """Test user creation with all required fields."""
        assert sample_user.id is not None
        assert sample_user.username == 'testuser'
        assert sample_user.email == 'test@example.com'
        assert sample_user.full_name == 'Test User'
        assert sample_user.role == 'user'
        assert sample_user.is_active is True
        assert sample_user.created_at is not None
    
    def test_user_repr(self, app, sample_user):
        """Test user string representation."""
        assert str(sample_user) == '<User testuser>'
        assert repr(sample_user) == '<User testuser>'
    
    def test_password_hashing(self, app, sample_user):
        """Test password hashing and verification."""
        # Test password verification
        assert sample_user.check_password('password123') is True
        assert sample_user.check_password('wrongpassword') is False
        
        # Test password hashing
        assert sample_user.password_hash != 'password123'
        assert sample_user.password_hash is not None
    
    def test_password_setting(self, app):
        """Test setting new password."""
        user = User(
            username='newuser',
            email='new@example.com',
            full_name='New User'
        )
        
        # Initially no password hash
        assert user.password_hash is None
        
        # Set password
        user.set_password('newpassword')
        assert user.password_hash is not None
        assert user.check_password('newpassword') is True
    
    def test_role_permissions(self, app, sample_user, admin_user, librarian_user):
        """Test user role permissions."""
        # Regular user
        assert sample_user.is_admin() is False
        assert sample_user.is_librarian() is False
        
        # Admin user
        assert admin_user.is_admin() is True
        assert admin_user.is_librarian() is True
        
        # Librarian user
        assert librarian_user.is_admin() is False
        assert librarian_user.is_librarian() is True
    
    def test_user_activation(self, app, sample_user):
        """Test user activation/deactivation."""
        assert sample_user.is_active is True
        
        # Deactivate user
        sample_user.is_active = False
        db.session.commit()
        
        assert sample_user.is_active is False
    
    def test_unique_constraints(self, app, sample_user):
        """Test unique constraints for username and email."""
        # Try to create user with same username
        duplicate_username = User(
            username='testuser',  # Same username
            email='different@example.com',
            full_name='Different User'
        )
        duplicate_username.set_password('password123')
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.session.add(duplicate_username)
            db.session.commit()
        
        db.session.rollback()
        
        # Try to create user with same email
        duplicate_email = User(
            username='differentuser',
            email='test@example.com',  # Same email
            full_name='Different User'
        )
        duplicate_email.set_password('password123')
        
        with pytest.raises(Exception):  # Should raise integrity error
            db.session.add(duplicate_email)
            db.session.commit()
    
    def test_user_relationships(self, app, sample_user):
        """Test user relationships."""
        # User should have loans relationship
        assert hasattr(sample_user, 'loans')
        assert len(sample_user.loans) == 0
