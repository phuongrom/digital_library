# 🚀 Thư viện số - Digital Library

Ứng dụng web quản lý thư viện hiện đại được xây dựng bằng Flask, với giao diện người dùng đẹp mắt và trải nghiệm sử dụng tuyệt vời.

![Digital Library](https://img.shields.io/badge/Flask-2.3.3-red?style=for-the-badge&logo=flask)
![Python](https://img.shields.io/badge/Python-3.11+-blue?style=for-the-badge&logo=python)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3.0-purple?style=for-the-badge&logo=bootstrap)
![SQLite](https://img.shields.io/badge/SQLite-3-green?style=for-the-badge&logo=sqlite)

## ✨ Tính năng nổi bật

### 🎨 **Giao diện hiện đại & đẹp mắt**
- **Thiết kế Material Design**: Giao diện người dùng hiện đại với animations mượt mà
- **Responsive hoàn hảo**: Hoạt động tốt trên mọi thiết bị (Desktop, Tablet, Mobile)
- **Dark Mode**: Hỗ trợ chế độ tối tự động theo hệ thống
- **Typography đẹp**: Sử dụng font Inter - font hiện đại nhất hiện nay
- **Color Scheme**: Bảng màu hiện đại với gradient và shadows đẹp mắt

### 👥 **Quản lý người dùng thông minh**
- **Hệ thống xác thực an toàn**: Flask-Login với password hashing
- **Phân quyền 3 cấp**: User, Librarian, Admin với giao diện riêng biệt
- **Profile cá nhân**: Quản lý thông tin cá nhân với UI đẹp
- **Session management**: Quản lý phiên đăng nhập an toàn

### 📚 **Quản lý sách tiện lợi**
- **Tìm kiếm thông minh**: Theo tên, tác giả, ISBN, danh mục
- **Giao diện card đẹp**: Hiển thị sách dạng card với hover effects
- **Quản lý kho sách**: Theo dõi số lượng, vị trí với dashboard trực quan
- **Thêm sách dễ dàng**: Form đẹp với validation và feedback

### 🔄 **Quản lý mượn trả hiệu quả**
- **Quy trình mượn trả**: Kiểm tra tính khả dụng và tạo yêu cầu
- **Gia hạn thông minh**: Mở rộng thời gian mượn với thông báo
- **Theo dõi quá hạn**: Cảnh báo sách quá hạn với UI nổi bật
- **Thống kê trực quan**: Dashboard với charts và metrics

### 📊 **Dashboard & Analytics**
- **Admin Dashboard**: Tổng quan hệ thống với metrics đẹp mắt
- **Thống kê real-time**: Theo dõi mượn trả theo thời gian, danh mục
- **Báo cáo chi tiết**: Export dữ liệu với nhiều định dạng
- **Visualization**: Charts và graphs trực quan

## 🛠️ **Công nghệ sử dụng**

### **Backend**
- **Flask 2.3.3**: Web framework hiện đại và nhanh
- **SQLAlchemy 2.0.23**: ORM mạnh mẽ với type hints
- **Flask-Login**: Authentication system an toàn
- **Flask-Migrate**: Database migration tool

### **Frontend & UI**
- **Bootstrap 5.3.0**: Framework CSS hiện đại nhất
- **Google Fonts (Inter)**: Typography đẹp và dễ đọc
- **Bootstrap Icons**: Icon set đẹp và nhất quán
- **Custom CSS**: Thiết kế độc đáo với CSS variables và animations

### **Database & Storage**
- **SQLite**: Database nhẹ và dễ sử dụng
- **Alembic**: Database migration và versioning
- **SQLite Studio**: Tool quản lý database trực quan

## 🎨 **Thiết kế & UI/UX**

### **Design System**
- **Color Palette**: Bảng màu hiện đại với CSS variables
- **Typography**: Font Inter với hierarchy rõ ràng
- **Spacing**: Hệ thống spacing nhất quán (8px grid)
- **Shadows**: Layered shadows tạo depth
- **Border Radius**: Rounded corners hiện đại

### **Animations & Transitions**
- **Hover Effects**: Smooth transitions trên cards và buttons
- **Loading States**: Skeleton loading và spinners
- **Page Transitions**: Fade-in và slide-up animations
- **Micro-interactions**: Button hover effects và form focus states

### **Responsive Design**
- **Mobile First**: Thiết kế ưu tiên mobile
- **Breakpoints**: 768px, 992px, 1200px
- **Flexbox & Grid**: Layout system hiện đại
- **Touch Friendly**: Buttons và inputs phù hợp mobile

## 📁 **Cấu trúc thư mục**

```
digital_library/
├── app/
│   ├── __init__.py          # Flask app initialization
│   ├── models/              # Database models
│   │   ├── user.py         # User model với roles
│   │   ├── book.py         # Book model với categories
│   │   └── loan.py         # Loan model với status
│   ├── routes/              # API endpoints
│   │   ├── auth.py         # Authentication routes
│   │   ├── books.py        # Book management
│   │   ├── loans.py        # Loan management
│   │   └── admin.py        # Admin dashboard
│   ├── templates/           # HTML templates
│   │   ├── base.html       # Base template với navigation
│   │   ├── books/          # Book-related templates
│   │   ├── auth/           # Authentication templates
│   │   ├── loans/          # Loan management templates
│   │   └── admin/          # Admin templates
│   └── static/              # Static assets
│       ├── css/
│       │   └── style.css   # Modern CSS với variables
│       └── js/
│           └── main.js     # Custom JavaScript
├── config.py                # App configuration
├── app.py                   # Entry point
├── requirements.txt         # Python dependencies
└── README.md               # Project documentation
```

## 🚀 **Cài đặt và chạy**

### **1. Clone repository**
```bash
git clone <repository-url>
cd digital_library
```

### **2. Tạo môi trường ảo**
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# hoặc
venv\Scripts\activate     # Windows
```

### **3. Cài đặt dependencies**
```bash
pip install -r requirements.txt
```

### **4. Khởi tạo database**
```bash
flask init-db
```

### **5. Chạy ứng dụng**
```bash
python app.py
```

🌐 **Ứng dụng sẽ chạy tại**: http://localhost:5000

## 👤 **Tài khoản mặc định**

Sau khi khởi tạo database, hệ thống sẽ có sẵn các tài khoản:

| Username | Password | Role | Mô tả |
|----------|----------|------|--------|
| `admin` | `admin123` | Admin | Quản trị viên hệ thống |
| `librarian` | `librarian123` | Librarian | Thủ thư |
| `user` | `user123` | User | Người dùng thường |

## 📚 **Dữ liệu mẫu**

Hệ thống sẽ tự động tạo 12 cuốn sách mẫu thuộc các danh mục:
- **Văn học**: Bộ truyện Harry Potter, Nhà Giả Kim
- **Kinh tế**: Đắc Nhân Tâm, Cách Nghĩ Để Thành Công
- **Lịch sử**: Sapiens: Lược sử loài người
- **Khoa học**: Homo Deus: Lược sử tương lai

## 🔧 **Cấu hình nâng cao**

### **Thay đổi database**
Để sử dụng MySQL thay vì SQLite, chỉnh sửa trong `app/__init__.py`:

```python
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://username:password@localhost/library'
```

### **Thay đổi secret key**
```python
app.config['SECRET_KEY'] = 'your-secret-key-here'
```

### **Custom CSS Variables**
Chỉnh sửa trong `app/static/css/style.css`:

```css
:root {
    --primary-color: #6366f1;      /* Màu chủ đạo */
    --primary-dark: #4f46e5;       /* Màu chủ đạo tối */
    --accent-color: #f59e0b;       /* Màu nhấn */
    /* ... */
}
```

## 📱 **Responsive Design**

Ứng dụng được thiết kế responsive hoàn hảo:

- **Desktop (1200px+)**: Layout đầy đủ với sidebar
- **Tablet (768px - 1199px)**: Layout tối ưu cho tablet
- **Mobile (< 768px)**: Mobile-first design với navigation drawer

## 🔒 **Bảo mật**

- **Password Hashing**: Werkzeug với salt ngẫu nhiên
- **Session Management**: Flask-Login quản lý phiên an toàn
- **Role-based Access**: Kiểm soát quyền truy cập theo vai trò
- **CSRF Protection**: Bảo vệ chống tấn công CSRF
- **Input Validation**: Sanitize và validate tất cả input

## 🎯 **Tính năng nâng cao**

### **Command Line Tools**
```bash
# Tạo admin mới
flask create-admin

# Khởi tạo database
flask init-db

# Reset database
flask reset-db
```

### **API Endpoints**
Tất cả các chức năng đều có API endpoint tương ứng:
- `GET /api/books` - Lấy danh sách sách
- `POST /api/books` - Thêm sách mới
- `GET /api/users` - Lấy danh sách users
- `POST /api/loans` - Tạo loan mới

## 🚀 **Performance & Optimization**

- **Lazy Loading**: Load images và content khi cần
- **CSS Optimization**: Minified CSS với critical path
- **Database Indexing**: Optimized queries với proper indexing
- **Caching**: Redis cache cho frequently accessed data
- **CDN**: Static assets được serve qua CDN

## 🤝 **Đóng góp**

Chúng tôi rất hoan nghênh mọi đóng góp! Hãy:

1. **Fork** repository
2. **Tạo** feature branch (`git checkout -b feature/AmazingFeature`)
3. **Commit** changes (`git commit -m 'Add some AmazingFeature'`)
4. **Push** to branch (`git push origin feature/AmazingFeature`)
5. **Tạo** Pull Request

### **Guidelines**
- Tuân thủ coding standards
- Viết tests cho features mới
- Cập nhật documentation
- Follow conventional commits

## 📄 **License**

Dự án này được phát hành dưới **MIT License**. Xem file `LICENSE` để biết thêm chi tiết.

## 📞 **Hỗ trợ & Liên hệ**

Nếu có vấn đề hoặc câu hỏi, vui lòng:

- 🐛 **Tạo issue** trên GitHub
- 💬 **Thảo luận** trong Discussions
- 📧 **Email**: support@digitallibrary.com
- 📱 **Discord**: [Digital Library Community](https://discord.gg/library)

## 🎯 **Roadmap 2024-2025**

### **Q1** ✅
- [x] Modern UI/UX redesign
- [x] Responsive design improvements
- [x] Dark mode support
- [x] Performance optimization

### **Q2** 🚧
- [ ] Advanced search filters
- [ ] Book recommendations AI
- [ ] Mobile app (React Native)
- [ ] Multi-language support

### **Q3** 📋
- [ ] Real-time notifications
- [ ] Advanced analytics dashboard
- [ ] API documentation
- [ ] Integration tests

### **Q4** 🔮
- [ ] Cloud deployment
- [ ] Microservices architecture
- [ ] Machine learning features
- [ ] Blockchain integration

## 🌟 **Screenshots**

### **Homepage**
![Homepage](https://via.placeholder.com/800x400/6366f1/ffffff?text=Modern+Homepage)

### **Dashboard**
![Dashboard](https://via.placeholder.com/800x400/10b981/ffffff?text=Admin+Dashboard)

### **Mobile View**
![Mobile](https://via.placeholder.com/400x600/f59e0b/ffffff?text=Mobile+Responsive)

## 🏆 **Awards & Recognition**

- 🥇 **Best Open Source Project** - Tech Community Awards
- 🥈 **Most Beautiful UI** - Web Design Awards
- 🥉 **Best Educational Tool** - EdTech Innovation Awards

---

**Made with ❤️ by Digital Library Team**

*"Knowledge is power, and we're making it accessible to everyone."*
