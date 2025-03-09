"""
Dịch vụ nhận diện giọng nói
"""
import speech_recognition as sr
import time

class VoiceService:
    """
    Dịch vụ nhận diện giọng nói sử dụng Google Speech Recognition
    """
    def __init__(self, filter_keywords=None):
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        self.filter_keywords = filter_keywords or []
        self.number_mapping = {
            "một": "1", "hai": "2", "ba": "3", "bốn": "4", "năm": "5",
            "sáu": "6", "bảy": "7", "tám": "8", "chín": "9", "mười": "10"
        }
        self.suggestion_keywords = [
            "đồng ý", "chấp nhận", "chọn", "làm theo", "thực hiện", 
            "ok", "được", "ừ", "theo", "làm", "một", "hai", "một", "hai", "ba"
        ]
        
    def listen(self, timeout=5, phrase_time_limit=3, language='vi-VN'):
        """
        Lắng nghe và nhận diện giọng nói
        """
        with self.microphone as source:
            print("Đang nghe... Hãy nói gì đó:")
            try:
                # Giảm thời gian điều chỉnh âm thanh để phản ứng nhanh hơn
                self.recognizer.adjust_for_ambient_noise(source, duration=0.2)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
                try:
                    text = self.recognizer.recognize_google(audio, language=language)
                    print(f"Bạn đã nói: {text}")
                    return text
                except sr.UnknownValueError:
                    print("Không nhận diện được âm thanh.")
                    return None
                except sr.RequestError as e:
                    print(f"Lỗi khi kết nối dịch vụ nhận diện giọng nói: {e}")
                    return None
            except Exception as e:
                print(f"Lỗi khi lắng nghe: {str(e)}")
                return None
                
    def preprocess_command(self, command_text):
        """
        Tiền xử lý lệnh giọng nói
        """
        if not command_text:
            return None
            
        command_text = command_text.lower()
        
        # Thay thế số tiếng Việt bằng số 
        for vn_num, digit in self.number_mapping.items():
            command_text = command_text.replace(vn_num, digit)
            
        # Lọc bỏ từ "nói" nếu người dùng nói "nói đọc đề xuất" 
        if "nói đọc đề xuất" in command_text:
            command_text = "đọc đề xuất"
            
        # Kiểm tra trước các cụm từ chính xác từ thông báo
        if "phát hiện cảm xúc" in command_text or "đề xuất mới" in command_text:
            print(f"Bỏ qua vì nhận diện trùng với thông báo hệ thống: '{command_text}'")
            return None
            
        # Kiểm tra từ khóa nhạy cảm
        should_skip = False
        for keyword in self.filter_keywords:
            if keyword in command_text:
                match_count = 0
                for other_keyword in self.filter_keywords:
                    if other_keyword in command_text and other_keyword != keyword:
                        match_count += 1
                # Chỉ bỏ qua nếu có ít nhất 2 từ khóa từ danh sách
                if match_count >= 1:
                    should_skip = True
                    break
        
        if should_skip:
            print(f"Bỏ qua vì nhận diện nhầm với nội dung đề xuất/cảm xúc: '{command_text}'")
            return None
            
        return command_text
        
    def check_suggestion_command(self, command_text, suggestions_count):
        """
        Kiểm tra xem lệnh có phải là chọn đề xuất không
        """
        if not command_text:
            return False, -1
            
        for keyword in self.suggestion_keywords:
            if keyword in command_text:
                # Tìm các số trong câu lệnh
                for i in range(1, suggestions_count + 1):
                    if str(i) in command_text:
                        return True, i - 1
        return False, -1