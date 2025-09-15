from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify
from flask_login import login_required, current_user
from app.models.book import Book
from app.models.loan import Loan
from app import db
from sqlalchemy import or_

books_bp = Blueprint('books', __name__)

@books_bp.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    books = Book.query.filter_by(is_active=True).order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('books/index.html', books=books)

@books_bp.route('/search')
def search():
    # Get all search parameters
    query = request.args.get('q', '')
    category = request.args.get('category', '')
    author = request.args.get('author', '')
    publisher = request.args.get('publisher', '')
    year = request.args.get('year', '')
    availability = request.args.get('availability', '')
    sort = request.args.get('sort', 'title')
    page = request.args.get('page', 1, type=int)
    per_page = 12
    
    # Start with base query
    search_query = Book.query.filter_by(is_active=True)
    
    # Text search (searches across multiple fields)
    if query:
        search_query = search_query.filter(
            or_(
                Book.title.ilike(f'%{query}%'),
                Book.author.ilike(f'%{query}%'),
                Book.isbn.ilike(f'%{query}%'),
                Book.description.ilike(f'%{query}%'),
                Book.publisher.ilike(f'%{query}%'),
                Book.publication_year.ilike(f'%{query}%')
            )
        )
    
    # Category filter
    if category:
        search_query = search_query.filter(Book.category == category)
    
    # Author filter
    if author:
        search_query = search_query.filter(Book.author.ilike(f'%{author}%'))
    
    # Publisher filter
    if publisher:
        search_query = search_query.filter(Book.publisher.ilike(f'%{publisher}%'))
    
    # Year filter
    if year:
        try:
            year_int = int(year)
            search_query = search_query.filter(Book.publication_year == year_int)
        except ValueError:
            pass  # Ignore invalid year
    
    # Availability filter
    if availability:
        if availability == 'available':
            # Books with available copies > 0
            search_query = search_query.filter(Book.available_copies > 0)
        elif availability == 'limited':
            # Books with 1-2 available copies
            search_query = search_query.filter(Book.available_copies.between(1, 2))
        elif availability == 'unavailable':
            # Books with no available copies
            search_query = search_query.filter(Book.available_copies == 0)
    
    # Sorting
    if sort == 'title':
        search_query = search_query.order_by(Book.title.asc())
    elif sort == 'title_desc':
        search_query = search_query.order_by(Book.title.desc())
    elif sort == 'author':
        search_query = search_query.order_by(Book.author.asc())
    elif sort == 'year':
        search_query = search_query.order_by(Book.publication_year.asc())
    elif sort == 'year_desc':
        search_query = search_query.order_by(Book.publication_year.desc())
    elif sort == 'created':
        search_query = search_query.order_by(Book.created_at.desc())
    else:
        search_query = search_query.order_by(Book.title.asc())
    
    # Pagination
    books = search_query.paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    # Get all categories for filter dropdown
    categories = db.session.query(Book.category).filter(
        Book.category.isnot(None), Book.is_active == True
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('books/search.html', 
                         books=books, 
                         query=query, 
                         category=category,
                         author=author,
                         publisher=publisher,
                         year=year,
                         availability=availability,
                         sort=sort,
                         categories=categories)

@books_bp.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    
    current_loan = None
    if current_user.is_authenticated:
        current_loan = Loan.query.filter_by(
            user_id=current_user.id,
            book_id=book_id
        ).filter(Loan.status.in_(['pending', 'borrowed'])).first()
    
    related_books = []
    if book.category:
        related_books = Book.query.filter(
            Book.category == book.category,
            Book.id != book.id,
            Book.is_active == True
        ).limit(4).all()
    
    return render_template('books/detail.html', book=book, current_loan=current_loan, related_books=related_books)

@books_bp.route('/book/<int:book_id>/borrow', methods=['POST'])
@login_required
def borrow_book(book_id):
    book = Book.query.get_or_404(book_id)
    
    if not book.is_available():
        flash('Sách này hiện không có sẵn để mượn!', 'warning')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
    existing_loan = Loan.query.filter_by(
        user_id=current_user.id,
        book_id=book_id
    ).filter(Loan.status.in_(['pending', 'borrowed'])).first()
    
    if existing_loan:
        if existing_loan.status == 'pending':
            flash('Bạn đã gửi yêu cầu mượn sách này rồi! Vui lòng chờ admin duyệt.', 'warning')
        else:
            flash('Bạn đã mượn sách này rồi!', 'warning')
        return redirect(url_for('books.book_detail', book_id=book_id))
    
    from datetime import datetime, timedelta
    
    new_loan = Loan(
        user_id=current_user.id,
        book_id=book_id,
        due_date=datetime.now() + timedelta(days=14),
        status='pending'  # Tạo loan với status pending
    )
    
    try:
        db.session.add(new_loan)
        db.session.commit()
        flash('Yêu cầu mượn sách đã được gửi! Vui lòng chờ admin duyệt.', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra khi gửi yêu cầu mượn sách!', 'danger')
    
    return redirect(url_for('books.book_detail', book_id=book_id))

@books_bp.route('/admin/books/add', methods=['GET', 'POST'])
@login_required
def add_book():
    if not current_user.is_librarian():
        flash('Bạn không có quyền thêm sách!', 'danger')
        return redirect(url_for('books.index'))
    
    if request.method == 'POST':
        isbn = request.form.get('isbn')
        title = request.form.get('title')
        author = request.form.get('author')
        publisher = request.form.get('publisher')
        publication_year = request.form.get('publication_year')
        category = request.form.get('category')
        description = request.form.get('description')
        total_copies = request.form.get('total_copies')
        location = request.form.get('location')
        
        if existing_book := Book.query.filter_by(isbn=isbn).first():
            flash('ISBN này đã tồn tại!', 'danger')
            return render_template('books/add.html')
        
        try:
            new_book = Book(
                isbn=isbn,
                title=title,
                author=author,
                publisher=publisher,
                publication_year=int(publication_year) if publication_year else None,
                category=category,
                description=description,
                total_copies=int(total_copies),
                available_copies=int(total_copies),
                location=location
            )
            
            db.session.add(new_book)
            db.session.commit()
            flash('Thêm sách thành công!', 'success')
            return redirect(url_for('books.admin_manage_books'))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi thêm sách!', 'danger')
    
    return render_template('books/add.html')

@books_bp.route('/admin/books/edit/<int:book_id>', methods=['GET', 'POST'])
@login_required
def edit_book(book_id):
    if not current_user.is_librarian():
        flash('Bạn không có quyền chỉnh sửa sách!', 'danger')
        return redirect(url_for('books.index'))
    
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
        
        try:
            db.session.commit()
            flash('Cập nhật sách thành công!', 'success')
            return redirect(url_for('books.admin_manage_books'))
        except Exception as e:
            db.session.rollback()
            flash('Có lỗi xảy ra khi cập nhật sách!', 'danger')
    
    return render_template('books/edit.html', book=book)

@books_bp.route('/delete/<int:book_id>', methods=['POST'])
@login_required
def delete_book(book_id):
    if not current_user.is_librarian():
        flash('Bạn không có quyền xóa sách!', 'danger')
        return redirect(url_for('books.index'))
    
    book = Book.query.get_or_404(book_id)
    
    try:
        # Check if book has active loans
        active_loans = Loan.query.filter_by(book_id=book.id, status='borrowed').count()
        if active_loans > 0:
            flash(f'Không thể xóa sách "{book.title}" vì đang có {active_loans} lượt mượn!', 'warning')
            return redirect(url_for('books.admin_manage_books'))
        
        db.session.delete(book)
        db.session.commit()
        flash(f'Đã xóa sách "{book.title}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('books.admin_manage_books'))

@books_bp.route('/toggle-status/<int:book_id>', methods=['POST'])
@login_required
def toggle_book_status(book_id):
    if not current_user.is_librarian():
        flash('Bạn không có quyền thay đổi trạng thái sách!', 'danger')
        return redirect(url_for('books.index'))
    
    book = Book.query.get_or_404(book_id)
    
    try:
        book.is_active = not book.is_active
        db.session.commit()
        
        status = "kích hoạt" if book.is_active else "vô hiệu hóa"
        flash(f'Đã {status} sách "{book.title}"!', 'success')
    except Exception as e:
        db.session.rollback()
        flash('Có lỗi xảy ra!', 'danger')
    
    return redirect(url_for('books.index'))

@books_bp.route('/categories')
def categories():
    categories = db.session.query(Book.category).filter(
        Book.category.isnot(None), Book.is_active == True
    ).distinct().all()
    categories = [cat[0] for cat in categories]
    
    return render_template('books/categories.html', categories=categories) 

# Admin book management routes
@books_bp.route('/admin/books')
@login_required
def admin_manage_books():
    if not current_user.is_admin():
        flash('Bạn cần quyền admin để truy cập trang này!', 'danger')
        return redirect(url_for('books.index'))
    
    page = request.args.get('page', 1, type=int)
    per_page = 20
    
    books = Book.query.order_by(Book.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )
    
    return render_template('admin/books.html', books=books) 