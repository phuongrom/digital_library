from flask import Blueprint, render_template, request, redirect, url_for, flash
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
    total_users = User.query.count()
    total_books = Book.query.count()
    total_loans = Loan.query.count()
    active_loans = Loan.query.filter_by(status='borrowed').count()
    overdue_loans = Loan.query.filter(
        Loan.status == 'borrowed',
        Loan.due_date < datetime.utcnow()
    ).count()
    
    recent_books = Book.query.order_by(Book.created_at.desc()).limit(5).all()
    
    recent_users = User.query.order_by(User.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html',
                         total_users=total_users,
                         total_books=total_books,
                         total_loans=total_loans,
                         active_loans=active_loans,
                         overdue_loans=overdue_loans,
                         recent_books=recent_books,
                         recent_users=recent_users)

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

@admin_bp.route('/admin/books')
@login_required
@admin_required
def manage_books():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    books = Book.query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/books.html', books=books)

@admin_bp.route('/admin/book/<int:book_id>/edit', methods=['GET', 'POST'])
@login_required
@admin_required
def edit_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if request.method == 'POST':
        book.isbn = request.form.get('isbn')
        book.title = request.form.get('title')
        book.author = request.form.get('author')
        book.publisher = request.form.get('publisher')
        book.publication_year = int(request.form.get('publication_year')) if request.form.get('publication_year') else None
        book.category = request.form.get('category')
        book.description = request.form.get('description')
        book.total_copies = int(request.form.get('total_copies'))
        book.location = request.form.get('location')
        
        # Cập nhật available_copies nếu total_copies thay đổi
        if book.total_copies < book.available_copies:
            book.available_copies = book.total_copies
        
        try:
            db.session.commit()
            flash('Sách đã được cập nhật thành công!', 'success')
            return redirect(url_for('admin.manage_books'))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra!', 'danger')
    
    return render_template('admin/edit_book.html', book=book)

@admin_bp.route('/admin/book/<int:book_id>/delete', methods=['POST'])
@login_required
@admin_required
def delete_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    try:
        book.is_active = False
        db.session.commit()
        flash('Đã xóa sách!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('admin.manage_books'))

@admin_bp.route('/admin/loans')
@login_required
@admin_required
def manage_loans():
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    loans = Loan.query.order_by(Loan.loan_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/loans.html', loans=loans)

@admin_bp.route('/admin/loan/<int:loan_id>/return', methods=['POST'])
@login_required
@admin_required
def admin_return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.return_date:
        flash('Sách này đã được trả rồi!', 'warning')
        return redirect(url_for('admin.manage_loans'))
    
    try:
        loan.return_date = datetime.now()
        loan.status = 'returned'
        
        book = Book.query.get(loan.book_id)
        if book:
            book.update_availability()
        
        db.session.commit()
        flash('Đã trả sách thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('admin.manage_loans'))

@admin_bp.route('/admin/loan/<int:loan_id>/extend', methods=['POST'])
@login_required
@admin_required
def admin_extend_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.return_date:
        flash('Sách này đã được trả rồi!', 'warning')
        return redirect(url_for('admin.manage_loans'))
    
    try:
        from datetime import timedelta
        loan.due_date += timedelta(days=7)
        db.session.commit()
        flash('Đã gia hạn sách thành công!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('admin.manage_loans')) 