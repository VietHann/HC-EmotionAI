"""
Dịch vụ phát hiện và xử lý cảm xúc
"""
import cv2
from deepface import DeepFace
import requests
import time
from models.suggestion import Suggestion

class EmotionService:
    """
    Dịch vụ phát hiện cảm xúc sử dụng DeepFace
    """
    def __init__(self, iot_server_url, emotion_labels, emotion_colors):
        self.iot_server_url = iot_server_url
        self.emotion_labels = emotion_labels
        self.emotion_colors = emotion_colors
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        self.current_emotion = None
        self.current_confidence = None
        self.emotion_processed = False
        self.emotion_timer = None
        self.suggestions = []
        
    def detect_emotion(self, frame):
        """
        Phát hiện cảm xúc từ khung hình
        """
        try:
            result = DeepFace.analyze(
                frame,
                actions=['emotion'],
                enforce_detection=True,
                detector_backend='mtcnn'
            )
            if result:
                emotions = result[0]['emotion']
                dominant_emotion = max(emotions.items(), key=lambda x: x[1])[0]
                confidence = emotions[dominant_emotion]
                return dominant_emotion, confidence
            return None, None
        except Exception as e:
            print(f"Lỗi khi phân tích cảm xúc: {str(e)}")
            return None, None
            
    def detect_faces(self, frame):
        """
        Phát hiện khuôn mặt trong khung hình
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.face_cascade.detectMultiScale(
            gray, 
            scaleFactor=1.3, 
            minNeighbors=5, 
            minSize=(100, 100)
        )
        return faces
        
    def update_emotion_to_server(self, emotion, confidence):
        """
        Gửi cập nhật cảm xúc đến server và nhận đề xuất
        """
        print(f"Đang gửi cập nhật cảm xúc {emotion} ({confidence:.1f}%) đến server")
        try:
            response = requests.post(
                f"{self.iot_server_url}/emotion/update",
                json={"emotion": emotion, "confidence": round(confidence)},
                headers={"Content-Type": "application/json"}
            )
            data = response.json()
            print(f"Phản hồi từ server: {data}")
            
            combined_message = ""
            
            if "suggestions" in data:
                new_suggestions = data["suggestions"]
                if new_suggestions != self.suggestions:
                    old_suggestion_count = len(self.suggestions)
                    self.suggestions = new_suggestions
                    
                    # Kết hợp thông báo đề xuất với thông báo cảm xúc
                    if len(new_suggestions) > 0:
                        # Thông báo đơn giản về đề xuất, không bao gồm hướng dẫn
                        combined_message = f"Có {len(new_suggestions)} đề xuất mới"
            
            # Trả về thông báo kết hợp (nếu có) để xử lý ở phương thức run
            return data.get("message", "Đã cập nhật cảm xúc"), combined_message
        except Exception as e:
            print(f"Lỗi khi gửi cập nhật cảm xúc: {str(e)}")
            return None, None
            
    def accept_suggestion(self, suggestion_index):
        if not self.suggestions or suggestion_index < 0 or suggestion_index >= len(self.suggestions):
            error_msg = "Không có đề xuất hợp lệ"
            print(error_msg)
            return error_msg
        
        suggestion = self.suggestions[suggestion_index]
        print(f"Đang chấp nhận đề xuất: {suggestion}")
        
        try:
            # Sử dụng endpoint mới dựa vào số đề xuất
            endpoint = f"{self.iot_server_url}/emotion/suggestion/accept/{suggestion_index + 1}"
            print(f"Gọi đến endpoint: {endpoint}")
            
            # Sử dụng GET thay vì POST để tránh lỗi JSON parsing
            response = requests.get(endpoint)
            
            data = response.json()
            print(f"Phản hồi từ server: {data}")
            # Bỏ gọi hàm play_command_success_sound
            result = data.get("message", "Đã thực hiện đề xuất")
            # Bỏ gọi hàm queue_speak
            return result
        except Exception as e:
            print(f"Lỗi khi gửi chấp nhận đề xuất: {str(e)}")
            error_msg = f"Lỗi khi thực hiện đề xuất: {str(e)}"
            # Bỏ gọi hàm queue_speak
            return error_msg
            
    def get_suggestions_text(self):
        """
        Lấy văn bản đọc cho các đề xuất
        """
        if not self.suggestions:
            return "Không có đề xuất nào"
        
        # Đọc nội dung đề xuất theo cách đơn giản và trực tiếp hơn
        full_text = "Các đề xuất: "
        
        for i, suggestion in enumerate(self.suggestions, 1):
            message = suggestion.get('message', '')
            full_text += f"đề xuất {i}: {message}. "
        
        return full_text