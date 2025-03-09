"""
Các tiện ích xử lý âm thanh
"""
import os
import time
import tempfile
import pygame
from gtts import gTTS

def ensure_sounds_exist(sound_dir, sound_files, command_success_sound):
    """
    Đảm bảo các file âm thanh tồn tại, nếu không thì tạo file giả
    """
    if not os.path.exists(sound_dir):
        os.makedirs(sound_dir)
            
    dummy_mp3 = b'\xff\xfb\x90\x44\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    
    for emotion, sound_file in sound_files.items():
        if not os.path.exists(sound_file):
            os.makedirs(os.path.dirname(sound_file), exist_ok=True)
            with open(sound_file, 'wb') as f:
                f.write(dummy_mp3)
            print(f"Đã tạo file âm thanh giả lập: {sound_file}")
            
    if not os.path.exists(command_success_sound):
        os.makedirs(os.path.dirname(command_success_sound), exist_ok=True)
        with open(command_success_sound, 'wb') as f:
            f.write(dummy_mp3)
        print(f"Đã tạo file âm thanh giả lập: {command_success_sound}")

def play_sound(sound_file):
    """
    Phát một file âm thanh
    """
    try:
        if os.path.exists(sound_file):
            sound = pygame.mixer.Sound(sound_file)
            sound.play()
            print(f"Đang phát âm thanh: {sound_file}")
            return True
        else:
            print(f"Không tìm thấy file âm thanh: {sound_file}")
    except Exception as e:
        print(f"Lỗi khi phát âm thanh: {str(e)}")
    return False

def text_to_speech(text, lang='vi'):
    """
    Chuyển đổi văn bản thành giọng nói và phát ra
    """
    try:
        # Kiểm tra xem pygame mixer có đang bận không
        if pygame.mixer.music.get_busy():
            print(f"Đang có âm thanh phát, chờ kết thúc trước khi phát: {text}")
            start_time = time.time()
            # Chờ tối đa 1 giây thay vì 3 giây
            while pygame.mixer.music.get_busy() and time.time() - start_time < 1:
                time.sleep(0.1)
            
        print(f"Đang phát âm: {text}")
        tts = gTTS(text=text, lang=lang)
        
        # Tạo tên file tạm thời với timestamp để tránh xung đột
        timestamp = int(time.time() * 1000)
        temp_filename = f"temp_tts_{timestamp}.mp3"
        temp_path = os.path.join(tempfile.gettempdir(), temp_filename)
        
        # Lưu và phát
        tts.save(temp_path)
        
        try:
            pygame.mixer.music.load(temp_path)
            pygame.mixer.music.play()
            
            # Chờ phát xong
            while pygame.mixer.music.get_busy():
                time.sleep(0.1)
            
            # Đảm bảo file được giải phóng trước khi xóa
            pygame.mixer.music.unload()
            
            # Giảm thời gian chờ xuống
            time.sleep(0.1)
        except Exception as e:
            print(f"Lỗi khi phát file âm thanh: {str(e)}")
        
        # Xóa file sau khi sử dụng, với cơ chế thử lại
        delete_attempts = 0
        max_attempts = 3
        while delete_attempts < max_attempts:
            try:
                os.unlink(temp_path)
                break
            except Exception as e:
                delete_attempts += 1
                if delete_attempts >= max_attempts:
                    print(f"Không thể xóa file tạm sau {max_attempts} lần thử: {str(e)}")
                else:
                    print(f"Thử xóa file lần {delete_attempts}, đợi thêm...")
                    time.sleep(0.1)
        
        return True
    except Exception as e:
        print(f"Lỗi khi sử dụng gTTS: {str(e)}")
        return False