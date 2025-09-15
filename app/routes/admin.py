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
    pending_loans = Loan.query.filter_by(status='pending').count()
    return_requests = Loan.query.filter_by(status='return_requested').count()
    extend_requests = Loan.query.filter_by(status='extend_requested').count()
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
                         pending_loans=pending_loans,
                         return_requests=return_requests,
                         extend_requests=extend_requests,
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

@admin_bp.route('/admin/loan-requests')
@login_required
@admin_required
def loan_requests():
    """Trang duyệt yêu cầu mượn sách"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Lấy danh sách yêu cầu mượn sách chờ duyệt
    pending_loans = Loan.query.filter_by(status='pending').order_by(Loan.loan_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Thống kê
    total_pending = Loan.query.filter_by(status='pending').count()
    total_approved_today = Loan.query.filter(
        Loan.status == 'borrowed',
        Loan.loan_date >= datetime.utcnow().date()
    ).count()
    
    return render_template('admin/loan_requests.html', 
                         pending_loans=pending_loans,
                         total_pending=total_pending,
                         total_approved_today=total_approved_today)

@admin_bp.route('/admin/loan-requests/approve/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def approve_loan_request(loan_id):
    """Duyệt yêu cầu mượn sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'pending':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.loan_requests'))
    
    try:
        # Kiểm tra sách còn khả dụng không
        if not loan.book.is_available():
            flash(f'Sách "{loan.book.title}" hiện không còn khả dụng!', 'warning')
            return redirect(url_for('admin.loan_requests'))
        
        # Duyệt yêu cầu
        loan.approve()
        db.session.commit()
        
        flash(f'Đã duyệt yêu cầu mượn sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi duyệt yêu cầu!', 'danger')
    
    return redirect(url_for('admin.loan_requests'))

@admin_bp.route('/admin/loan-requests/reject/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def reject_loan_request(loan_id):
    """Từ chối yêu cầu mượn sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'pending':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.loan_requests'))
    
    try:
        # Từ chối yêu cầu
        loan.reject()
        db.session.commit()
        
        flash(f'Đã từ chối yêu cầu mượn sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi từ chối yêu cầu!', 'danger')
    
    return redirect(url_for('admin.loan_requests'))

@admin_bp.route('/admin/loan-requests/bulk-action', methods=['POST'])
@login_required
@admin_required
def bulk_loan_action():
    """Xử lý hàng loạt yêu cầu mượn sách"""
    action = request.form.get('action')
    loan_ids = request.form.getlist('loan_ids')
    
    if not loan_ids:
        flash('Vui lòng chọn ít nhất một yêu cầu!', 'warning')
        return redirect(url_for('admin.loan_requests'))
    
    if action not in ['approve', 'reject']:
        flash('Hành động không hợp lệ!', 'danger')
        return redirect(url_for('admin.loan_requests'))
    
    try:
        loans = Loan.query.filter(
            Loan.id.in_(loan_ids),
            Loan.status == 'pending'
        ).all()
        
        success_count = 0
        for loan in loans:
            if action == 'approve':
                if loan.book.is_available():
                    loan.approve()
                    success_count += 1
            else:  # reject
                loan.reject()
                success_count += 1
        
        db.session.commit()
        
        action_text = "duyệt" if action == 'approve' else "từ chối"
        flash(f'Đã {action_text} {success_count} yêu cầu thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi xử lý hàng loạt!', 'danger')
    
    return redirect(url_for('admin.loan_requests'))

@admin_bp.route('/admin/return-requests')
@login_required
@admin_required
def return_requests():
    """Trang duyệt yêu cầu trả sách"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Lấy danh sách yêu cầu trả sách chờ duyệt
    return_requests = Loan.query.filter_by(status='return_requested').order_by(Loan.loan_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Thống kê
    total_return_requests = Loan.query.filter_by(status='return_requested').count()
    total_processed_today = Loan.query.filter(
        Loan.status == 'returned',
        Loan.return_date >= datetime.utcnow().date()
    ).count()
    
    return render_template('admin/return_requests.html', 
                         return_requests=return_requests,
                         total_return_requests=total_return_requests,
                         total_processed_today=total_processed_today)

@admin_bp.route('/admin/extend-requests')
@login_required
@admin_required
def extend_requests():
    """Trang duyệt yêu cầu gia hạn sách"""
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    # Lấy danh sách yêu cầu gia hạn chờ duyệt
    extend_requests = Loan.query.filter_by(status='extend_requested').order_by(Loan.loan_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Thống kê
    total_extend_requests = Loan.query.filter_by(status='extend_requested').count()
    total_approved_today = Loan.query.filter(
        Loan.status == 'borrowed',
        Loan.loan_date >= datetime.utcnow().date()
    ).count()
    
    from datetime import timedelta
    
    return render_template('admin/extend_requests.html', 
                         extend_requests=extend_requests,
                         total_extend_requests=total_extend_requests,
                         total_approved_today=total_approved_today,
                         timedelta=timedelta)

@admin_bp.route('/admin/return-requests/approve/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def approve_return_request(loan_id):
    """Duyệt yêu cầu trả sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'return_requested':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.return_requests'))
    
    try:
        # Duyệt yêu cầu trả sách
        loan.approve_return()
        db.session.commit()
        
        flash(f'Đã duyệt yêu cầu trả sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi duyệt yêu cầu!', 'danger')
    
    return redirect(url_for('admin.return_requests'))

@admin_bp.route('/admin/return-requests/reject/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def reject_return_request(loan_id):
    """Từ chối yêu cầu trả sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'return_requested':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.return_requests'))
    
    try:
        # Từ chối yêu cầu trả sách
        loan.reject_return()
        db.session.commit()
        
        flash(f'Đã từ chối yêu cầu trả sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi từ chối yêu cầu!', 'danger')
    
    return redirect(url_for('admin.return_requests'))

@admin_bp.route('/admin/extend-requests/approve/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def approve_extend_request(loan_id):
    """Duyệt yêu cầu gia hạn sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'extend_requested':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.extend_requests'))
    
    try:
        # Duyệt yêu cầu gia hạn
        loan.approve_extension()
        db.session.commit()
        
        flash(f'Đã duyệt yêu cầu gia hạn sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi duyệt yêu cầu!', 'danger')
    
    return redirect(url_for('admin.extend_requests'))

@admin_bp.route('/admin/extend-requests/reject/<int:loan_id>', methods=['POST'])
@login_required
@admin_required
def reject_extend_request(loan_id):
    """Từ chối yêu cầu gia hạn sách"""
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.status != 'extend_requested':
        flash('Yêu cầu này không còn chờ duyệt!', 'warning')
        return redirect(url_for('admin.extend_requests'))
    
    try:
        # Từ chối yêu cầu gia hạn
        loan.reject_extension()
        db.session.commit()
        
        flash(f'Đã từ chối yêu cầu gia hạn sách "{loan.book.title}" của {loan.user.full_name}!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi từ chối yêu cầu!', 'danger')
    
    return redirect(url_for('admin.extend_requests'))

@admin_bp.route('/admin/api/stats')
@login_required
@admin_required
def api_stats():
    """API endpoint để lấy thống kê real-time"""
    try:
        pending_loans = Loan.query.filter_by(status='pending').count()
        return_requests = Loan.query.filter_by(status='return_requested').count()
        extend_requests = Loan.query.filter_by(status='extend_requested').count()
        overdue_loans = Loan.query.filter(
            Loan.status == 'borrowed',
            Loan.due_date < datetime.utcnow()
        ).count()
        
        return {
            'pending_loans': pending_loans,
            'return_requests': return_requests,
            'extend_requests': extend_requests,
            'overdue_loans': overdue_loans,
            'total_requests': pending_loans + return_requests + extend_requests,
            'timestamp': datetime.utcnow().isoformat()
        }
    except Exception as e:
        return {'error': str(e)}, 500 