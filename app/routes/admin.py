from flask import Blueprint, render_template, request, redirect, url_for, flash, session
from flask_login import login_required, current_user
from app.models.user import User
from app.models.book import Book
from app.models.loan import Loan
from app import db
from datetime import datetime

admin_bp = Blueprint('admin', __name__)

def admin_required(f):
    from functools import wraps
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or not current_user.is_admin():
            flash('Bạn cần quyền admin để truy cập trang này!', 'danger')
            return redirect(url_for('books.index'))
        return f(*args, **kwargs)
    return decorated_function

@admin_bp.route('/admin')
@login_required
@admin_required
def admin_dashboard():
    # Thống kê tổng quan
    total_users = User.query.count()
    total_books = Book.query.count()
    total_loans = Loan.query.count()
    
    # Thống kê mượn sách
    active_loans = Loan.query.filter_by(status='borrowed').count()
    returned_loans = Loan.query.filter_by(status='returned').count()
    overdue_loans = Loan.query.filter(
        Loan.status == 'borrowed',
        Loan.due_date < datetime.utcnow()
    ).count()
    
    # Tính phần trăm
    loan_completion_rate = (returned_loans / total_loans * 100) if total_loans > 0 else 0
    overdue_rate = (overdue_loans / total_loans * 100) if total_loans > 0 else 0
    
    # Sách mới nhất
    recent_books = Book.query.order_by(Book.id.desc()).limit(5).all()
    
    # User mới nhất
    recent_users = User.query.order_by(User.id.desc()).limit(5).all()
    
    # Mượn sách gần đây
    recent_loans = Loan.query.order_by(Loan.loan_date.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_loans=total_loans,
                         active_loans=active_loans,
                         returned_loans=returned_loans,
                         overdue_loans=overdue_loans,
                         loan_completion_rate=loan_completion_rate,
                         overdue_rate=overdue_rate,
                         recent_books=recent_books,
                         recent_users=recent_users,
                         recent_loans=recent_loans)

@admin_bp.route('/admin/users')
@login_required
@admin_required
def manage_users():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    users = User.query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/users.html', users=users)

@admin_bp.route('/admin/user/<int:user_id>/toggle-status', methods=['POST'])
@login_required
@admin_required
def toggle_user_status(user_id):
    user = User.query.get_or_404(user_id)
    
    if user.id == current_user.id:
        flash('Không thể thay đổi trạng thái của chính mình!', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user.is_active = not user.is_active
        db.session.commit()
        
        status = "kích hoạt" if user.is_active else "vô hiệu hóa"
        flash(f'Đã {status} user {user.username}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/user/<int:user_id>/change-role', methods=['POST'])
@login_required
@admin_required
def change_user_role(user_id):
    user = User.query.get_or_404(user_id)
    new_role = request.form.get('role')
    
    if user.id == current_user.id:
        flash('Không thể thay đổi role của chính mình!', 'warning')
        return redirect(url_for('admin.manage_users'))
    
    if new_role not in ['user', 'librarian', 'admin']:
        flash('Role không hợp lệ!', 'danger')
        return redirect(url_for('admin.manage_users'))
    
    try:
        user.role = new_role
        db.session.commit()
        flash(f'Đã thay đổi role của {user.username} thành {new_role}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/add', methods=['POST'])
@login_required
@admin_required
def add_user():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        full_name = request.form.get('full_name')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password')
        role = request.form.get('role')
        is_active = request.form.get('is_active') == 'on'
        
        # Validation
        if not all([username, email, full_name, password, confirm_password, role]):
            flash('Vui lòng điền đầy đủ thông tin bắt buộc!', 'error')
            return redirect(url_for('admin.manage_users'))
        
        if password != confirm_password:
            flash('Mật khẩu xác nhận không khớp!', 'error')
            return redirect(url_for('admin.manage_users'))
        
        if len(password) < 6:
            flash('Mật khẩu phải có ít nhất 6 ký tự!', 'error')
            return redirect(url_for('admin.manage_users'))
        
        # Check if username or email already exists
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'error')
            return redirect(url_for('admin.manage_users'))
        
        if User.query.filter_by(email=email).first():
            flash('Email đã tồn tại!', 'error')
            return redirect(url_for('admin.manage_users'))
        
        try:
            # Create new user
            new_user = User(
                username=username,
                email=email,
                full_name=full_name,
                role=role,
                is_active=is_active
            )
            new_user.set_password(password)
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Đã thêm user "{full_name}" thành công!', 'success')
            
        except Exception as e:
            db.session.rollback()
            flash(f'Có lỗi xảy ra: {str(e)}', 'error')
        
        return redirect(url_for('admin.manage_users'))

@admin_bp.route('/admin/users/clear-session', methods=['POST'])
@login_required
@admin_required
def clear_add_user_session():
    session.pop('add_user_form_data', None)
    session.pop('add_user_errors', None)
    return '', 204 