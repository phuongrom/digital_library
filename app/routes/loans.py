from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user
from app.models.loan import Loan
from app.models.book import Book
from app.models.user import User
from app import db
from datetime import datetime, timedelta

loans_bp = Blueprint('loans', __name__)

@loans_bp.route('/my-loans')
@login_required
def my_loans():
    page = request.args.get('page', 1, type=int)
    per_page = 10
    
    loans = Loan.query.filter_by(user_id=current_user.id).order_by(Loan.loan_date.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    overdue_count = Loan.query.filter(
        Loan.user_id == current_user.id,
        Loan.status == 'borrowed',
        Loan.due_date < datetime.now()
    ).count()
    
    borrowed_count = Loan.query.filter(
        Loan.user_id == current_user.id,
        Loan.status == 'borrowed'
    ).count()
    
    returned_count = Loan.query.filter(
        Loan.user_id == current_user.id,
        Loan.status == 'returned'
    ).count()
    
    overdue_loans_list = Loan.query.filter(
        Loan.user_id == current_user.id,
        Loan.status == 'borrowed',
        Loan.due_date < datetime.now()
    ).all()
    
    return render_template('loans/my_loans.html', 
                         loans=loans, 
                         overdue_count=overdue_count,
                         borrowed_count=borrowed_count,
                         returned_count=returned_count,
                         overdue_loans_list=overdue_loans_list)

@loans_bp.route('/borrow/<int:book_id>', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    # Kiểm tra sách có thể mượn được không
    can_borrow, message = book.can_borrow(current_user.id)
    if not can_borrow:
        flash(message, 'error')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
    # Tạo loan mới
    loan = Loan(
        user_id=current_user.id,
        book_id=book_id,
        loan_date=datetime.now(),
        due_date=datetime.now() + timedelta(days=14),
        status='borrowed'
    )
    
    db.session.add(loan)
    db.session.commit()
    
    # Cập nhật availability sau khi commit
    book.update_availability()
    db.session.commit()
    
    flash(f'Bạn đã mượn sách "{book.title}" thành công! Hạn trả: {loan.due_date.strftime("%d/%m/%Y")}', 'success')
    return redirect(url_for('loans.my_loans'))

@loans_bp.route('/return_book/<int:loan_id>', methods=['POST'])
@login_required
def return_book(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.user_id != current_user.id:
        flash('Bạn không có quyền trả sách này.', 'error')
        return redirect(url_for('loans.my_loans'))
    
    if loan.status == 'returned':
        flash('Sách này đã được trả rồi.', 'error')
        return redirect(url_for('loans.my_loans'))
    
    # Trả sách
    loan.return_book()
    
    db.session.commit()
    
    # Cập nhật availability sau khi commit
    book = Book.query.get(loan.book_id)
    if book:
        book.update_availability()
        db.session.commit()
    
    flash('Bạn đã trả sách thành công!', 'success')
    return redirect(url_for('loans.my_loans'))

@loans_bp.route('/overdue')
@login_required
def overdue():
    if current_user.role not in ['admin', 'librarian']:
        flash('Bạn không có quyền truy cập trang này.', 'error')
        return redirect(url_for('books.index'))
    
    overdue_loans = Loan.query.filter(
        Loan.return_date.is_(None),
        Loan.due_date < datetime.now()
    ).all()
    
    total_overdue = len(overdue_loans)
    
    return render_template('loans/overdue.html', 
                         loans=overdue_loans,
                         total_overdue=total_overdue)

@loans_bp.route('/extend/<int:loan_id>', methods=['POST'])
@login_required
def extend_loan(loan_id):
    loan = Loan.query.get_or_404(loan_id)
    
    if loan.user_id != current_user.id:
        flash('Bạn không có quyền gia hạn sách này.', 'error')
        return redirect(url_for('loans.my_loans'))
    
    if loan.status == 'returned':
        flash('Sách này đã được trả rồi.', 'error')
        return redirect(url_for('loans.my_loans'))
    
    loan.due_date += timedelta(days=7)
    db.session.commit()
    
    flash('Gia hạn sách thành công! Hạn trả mới: ' + loan.due_date.strftime('%d/%m/%Y'), 'success')
    return redirect(url_for('loans.my_loans'))

@loans_bp.route('/statistics')
@login_required
def statistics():
    if current_user.role not in ['admin', 'librarian']:
        flash('Bạn không có quyền truy cập trang này.', 'error')
        return redirect(url_for('books.index'))
    
    total_books = Book.query.count()
    total_users = User.query.count()
    total_loans = Loan.query.count()
    active_loans = Loan.query.filter_by(return_date=None).count()
    returned_loans = Loan.query.filter(Loan.return_date.isnot(None)).count()
    overdue_loans = Loan.query.filter(
        Loan.return_date.is_(None),
        Loan.due_date < datetime.now()
    ).count()
    
    # Tính toán thống kê theo tháng (6 tháng gần nhất)
    monthly_stats = []
    current_time = datetime.now()
    
    for i in range(6):
        month_date = current_time - timedelta(days=30*i)
        month_start = month_date.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(seconds=1)
        
        month_loans = Loan.query.filter(
            Loan.loan_date >= month_start,
            Loan.loan_date <= month_end
        ).count()
        
        monthly_stats.append({
            'month': month_start.strftime('%m/%Y'),
            'loans': month_loans
        })
    
    monthly_stats.reverse()  # Sắp xếp từ cũ đến mới
    
    # Sửa query popular books để dễ sử dụng hơn
    popular_books_query = db.session.query(
        Book.id,
        Book.title,
        Book.author,
        Book.category,
        db.func.count(Loan.id).label('loan_count')
    ).join(Loan).group_by(
        Book.id, Book.title, Book.author, Book.category
    ).order_by(db.func.count(Loan.id).desc()).limit(10).all()
    
    # Chuyển đổi thành list of dictionaries
    popular_books = []
    for book_data in popular_books_query:
        popular_books.append({
            'id': book_data.id,
            'title': book_data.title,
            'author': book_data.author,
            'category': book_data.category,
            'loan_count': book_data.loan_count
        })
    
    return render_template('loans/statistics.html',
                         total_books=total_books,
                         total_users=total_users,
                         total_loans=total_loans,
                         active_loans=active_loans,
                         returned_loans=returned_loans,
                         overdue_loans=overdue_loans,
                         monthly_stats=monthly_stats,
                         popular_books=popular_books) 