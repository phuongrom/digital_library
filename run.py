#!/usr/bin/env python3

from app import create_app, db
from app.models.user import User
from app.models.book import Book
from app.models.loan import Loan

app = create_app()

@app.shell_context_processor
def make_shell_context():
    return {
        'db': db,
        'User': User,
        'Book': Book,
        'Loan': Loan
    }

@app.cli.command()
def init_db():
    from app import db
    from app.models.user import User
    from app.models.book import Book
    
    print("Creating database tables...")
    db.create_all()
    
    admin_user = User.query.filter_by(username='admin').first()
    if not admin_user:
        print("Creating admin user...")
        admin_user = User(
            username='admin',
            email='admin@library.com',
            full_name='Administrator',
            role='admin'
        )
        admin_user.set_password('admin123')
        db.session.add(admin_user)
        
        librarian_user = User(
            username='librarian',
            email='librarian@library.com',
            full_name='Thủ thư',
            role='librarian'
        )
        librarian_user.set_password('librarian123')
        db.session.add(librarian_user)
        
        regular_user = User(
            username='user',
            email='user@library.com',
            full_name='Người dùng',
            role='user'
        )
        regular_user.set_password('user123')
        db.session.add(regular_user)
        
        db.session.commit()
        print("Sample users created successfully!")
    
    if Book.query.count() == 0:
        print("Creating sample books...")
        sample_books = [
            {
                'isbn': '978-0-7475-3269-9',
                'title': 'Harry Potter và Hòn đá Phù thủy',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2000,
                'category': 'Văn học',
                'description': 'Câu chuyện về cậu bé phù thủy Harry Potter và cuộc phiêu lưu kỳ diệu tại trường Hogwarts.',
                'total_copies': 5,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3270-5',
                'title': 'Harry Potter và Phòng chứa Bí mật',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2001,
                'category': 'Văn học',
                'description': 'Năm thứ hai tại Hogwarts, Harry phát hiện ra bí mật về Phòng chứa Bí mật.',
                'total_copies': 4,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3271-2',
                'title': 'Harry Potter và Tên tù nhân Azkaban',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2002,
                'category': 'Văn học',
                'description': 'Năm thứ ba tại Hogwarts, Harry gặp gỡ Sirius Black và khám phá bí mật về quá khứ.',
                'total_copies': 4,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3272-9',
                'title': 'Harry Potter và Chiếc cốc Lửa',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2003,
                'category': 'Văn học',
                'description': 'Harry tham gia giải đấu Tam Pháp Thuật và chứng kiến sự trở lại của Chúa tể Voldemort.',
                'total_copies': 3,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3273-6',
                'title': 'Harry Potter và Hội Phượng Hoàng',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2004,
                'category': 'Văn học',
                'description': 'Harry thành lập Hội Phượng Hoàng để dạy phòng thủ chống lại Nghệ thuật Hắc ám.',
                'total_copies': 3,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3274-3',
                'title': 'Harry Potter và Hoàng tử Lai',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2005,
                'category': 'Văn học',
                'description': 'Harry học về quá khứ của Voldemort và chứng kiến cái chết của Dumbledore.',
                'total_copies': 3,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3275-0',
                'title': 'Harry Potter và Bảo bối Tử thần',
                'author': 'J.K. Rowling',
                'publisher': 'NXB Trẻ',
                'publication_year': 2007,
                'category': 'Văn học',
                'description': 'Cuộc chiến cuối cùng giữa Harry và Voldemort, kết thúc chuỗi truyện Harry Potter.',
                'total_copies': 3,
                'location': 'Kệ A1'
            },
            {
                'isbn': '978-0-7475-3276-7',
                'title': 'Nhà Giả Kim',
                'author': 'Paulo Coelho',
                'publisher': 'NXB Văn học',
                'publication_year': 1988,
                'category': 'Văn học',
                'description': 'Câu chuyện về Santiago, một cậu bé chăn cừu đi tìm kho báu và khám phá ý nghĩa cuộc sống.',
                'total_copies': 4,
                'location': 'Kệ A2'
            },
            {
                'isbn': '978-0-7475-3277-4',
                'title': 'Đắc Nhân Tâm',
                'author': 'Dale Carnegie',
                'publisher': 'NXB Tổng hợp TP.HCM',
                'publication_year': 1936,
                'category': 'Kinh tế',
                'description': 'Cuốn sách về nghệ thuật đối nhân xử thế và cách xây dựng mối quan hệ tốt đẹp.',
                'total_copies': 5,
                'location': 'Kệ B1'
            },
            {
                'isbn': '978-0-7475-3278-1',
                'title': 'Cách Nghĩ Để Thành Công',
                'author': 'Napoleon Hill',
                'publisher': 'NXB Tổng hợp TP.HCM',
                'publication_year': 1937,
                'category': 'Kinh tế',
                'description': 'Phân tích những nguyên tắc thành công từ những người thành đạt nhất thế giới.',
                'total_copies': 4,
                'location': 'Kệ B1'
            },
            {
                'isbn': '978-0-7475-3279-8',
                'title': 'Sapiens: Lược sử loài người',
                'author': 'Yuval Noah Harari',
                'publisher': 'NXB Tri thức',
                'publication_year': 2011,
                'category': 'Lịch sử',
                'description': 'Cuốn sách về lịch sử loài người từ thời kỳ săn bắn hái lượm đến thời đại kỹ thuật số.',
                'total_copies': 3,
                'location': 'Kệ C1'
            },
            {
                'isbn': '978-0-7475-3280-4',
                'title': 'Homo Deus: Lược sử tương lai',
                'author': 'Yuval Noah Harari',
                'publisher': 'NXB Tri thức',
                'publication_year': 2015,
                'category': 'Khoa học',
                'description': 'Dự đoán về tương lai của loài người trong thời đại trí tuệ nhân tạo và công nghệ sinh học.',
                'total_copies': 3,
                'location': 'Kệ C2'
            }
        ]
        
        for book_data in sample_books:
            book = Book(**book_data)
            db.session.add(book)
        
        db.session.commit()
        print("Sample books created successfully!")
    
    print("Database initialization completed!")

@app.cli.command()
def create_admin():
    from app import db
    from app.models.user import User
    
    admin_user = User.query.filter_by(username='admin').first()
    if admin_user:
        print("Admin user already exists!")
        return
    
    admin_user = User(
        username='admin',
        email='admin@library.com',
        full_name='Administrator',
        role='admin'
    )
    admin_user.set_password('admin123')
    
    db.session.add(admin_user)
    db.session.commit()
    print("Admin user created successfully!")
    print("Username: admin")
    print("Password: admin123")

@app.cli.command()
def reset_db():
    from app import db
    
    print("Dropping all tables...")
    db.drop_all()
    print("Creating all tables...")
    db.create_all()
    print("Database reset completed!")

if __name__ == '__main__':
    print("Starting Digital Library application...")
    print("Admin credentials: admin/admin123")
    print("Librarian credentials: librarian/librarian123")
    print("User credentials: user/user123")
    print("--------------------------------------------------")
    app.run(debug=True, host='0.0.0.0', port=5001) 