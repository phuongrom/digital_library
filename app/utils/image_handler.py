import os
import uuid
from PIL import Image
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename):
    """Kiểm tra file có được phép upload không"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in current_app.config['ALLOWED_EXTENSIONS']

def save_image(file, folder, max_size=(800, 600)):
    """
    Lưu hình ảnh và resize nếu cần
    
    Args:
        file: File object từ request
        folder: Thư mục con (books hoặc users)
        max_size: Kích thước tối đa (width, height)
    
    Returns:
        str: Đường dẫn tương đối đến file đã lưu, None nếu lỗi
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Tạo tên file unique
        filename = secure_filename(file.filename)
        name, ext = os.path.splitext(filename)
        unique_filename = f"{uuid.uuid4().hex}{ext}"
        
        # Tạo đường dẫn thư mục
        upload_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], folder)
        os.makedirs(upload_folder, exist_ok=True)
        
        # Đường dẫn file
        file_path = os.path.join(upload_folder, unique_filename)
        
        # Mở và resize hình ảnh
        with Image.open(file) as img:
            # Convert sang RGB nếu cần (cho PNG có alpha channel)
            if img.mode in ('RGBA', 'LA', 'P'):
                img = img.convert('RGB')
            
            # Resize nếu hình ảnh quá lớn
            if img.size[0] > max_size[0] or img.size[1] > max_size[1]:
                img.thumbnail(max_size, Image.Resampling.LANCZOS)
            
            # Lưu hình ảnh
            img.save(file_path, 'JPEG', quality=85, optimize=True)
        
        # Trả về đường dẫn tương đối
        return os.path.join('uploads', folder, unique_filename)
        
    except Exception as e:
        print(f"Error saving image: {e}")
        return None

def delete_image(image_path):
    """Xóa hình ảnh"""
    if not image_path:
        return True
    
    try:
        full_path = os.path.join(current_app.static_folder, image_path)
        if os.path.exists(full_path):
            os.remove(full_path)
        return True
    except Exception as e:
        print(f"Error deleting image: {e}")
        return False

def get_default_image(folder):
    """Lấy đường dẫn hình ảnh mặc định"""
    if folder == 'books':
        return 'images/default-book.jpg'
    elif folder == 'users':
        return 'images/default-user.jpg'
    return None

