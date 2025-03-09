"""
Dịch vụ Text-to-Speech
"""
import queue
import threading
import time
from utils.audio_utils import text_to_speech

class TTSService:
    """
    Dịch vụ chuyển văn bản thành giọng nói
    """
    def __init__(self):
        self.tts_queue = queue.Queue()
        self.is_speaking = False
        self.tts_thread = threading.Thread(target=self._tts_worker)
        self.tts_thread.daemon = True
        self.tts_thread.start()
        
    def _tts_worker(self):
        """
        Worker xử lý hàng đợi TTS
        """
        while True:
            text = self.tts_queue.get()
            if text is None:
                break
                
            # Bỏ qua bước lọc cụm từ gây nhầm lẫn khi đọc đề xuất
            # Chỉ thực hiện khi không phải là đọc đề xuất
            if not text.startswith("Các đề xuất:"):
                filtered_text = text
                phrases_to_filter = [
                    "bạn có vẻ buồn", "tạo không gian", "yên tĩnh", "phát một bản nhạc",
                    "nhẹ nhàng", "giúp bạn thư giãn", "nhạc vui", "nhạc buồn"
                ]
                
                for phrase in phrases_to_filter:
                    if phrase.lower() in filtered_text.lower():
                        filtered_text = filtered_text.lower().replace(phrase.lower(), "[đề xuất]")
            else:
                # Không lọc khi đọc đề xuất
                filtered_text = text
            
            # Đánh dấu rằng hệ thống đang phát âm
            self.is_speaking = True
            
            # Phát âm văn bản
            if not self._should_skip(filtered_text):
                text_to_speech(filtered_text)
            
            # Đợi thêm một chút sau khi phát âm để tránh ảnh hưởng
            time.sleep(0.2)
            
            # Đánh dấu rằng hệ thống đã ngừng phát âm
            self.is_speaking = False
            
            self.tts_queue.task_done()
            
    def _should_skip(self, text):
        """
        Kiểm tra xem có nên bỏ qua việc đọc văn bản này không
        """
        return text.startswith("Lỗi") or "không nhận diện" in text.lower()
            
    def speak(self, text):
        """
        Thêm văn bản vào hàng đợi để phát âm
        """
        self.tts_queue.put(text)
        
    def is_busy(self):
        """
        Kiểm tra xem dịch vụ TTS có đang bận không
        """
        return self.is_speaking
        
    def stop(self):
        """
        Dừng dịch vụ TTS
        """
        self.tts_queue.put(None)