"""
File chính để khởi động server IoT cho Hệ thống Nhận diện Cảm xúc.
"""
from flask import Flask
from flask_cors import CORS
import threading
import time

from utils import initialize_directories
from models import MusicPlayer, SensorData
from routes import register_routes
from config import SERVER_HOST, SERVER_PORT, DEBUG_MODE

# Khởi tạo ứng dụng Flask
app = Flask(__name__)
CORS(app)

# Đăng ký tất cả các route
register_routes(app)

# Hàm cập nhật dữ liệu giả lập
def update_simulated_data():
    """Cập nhật dữ liệu nhiệt độ, độ ẩm theo thời gian."""
    while True:
        SensorData.update_simulated_data()
        time.sleep(10)

if __name__ == "__main__":
    # Khởi tạo thư mục và file nhạc
    initialize_directories()
    
    # Khởi tạo hệ thống âm thanh
    MusicPlayer.initialize()
    
    # Chạy thread cập nhật dữ liệu giả lập
    update_thread = threading.Thread(target=update_simulated_data)
    update_thread.daemon = True
    update_thread.start()
    
    print("Khởi động IoT Server cho Hệ thống Nhận diện Cảm xúc...")
    print(f"Server đang chạy tại địa chỉ: http://{SERVER_HOST}:{SERVER_PORT}/")
    app.run(host=SERVER_HOST, port=SERVER_PORT, debug=DEBUG_MODE)