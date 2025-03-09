"""
Mô hình dữ liệu cho đề xuất
"""

class Suggestion:
    """
    Đại diện cho một đề xuất từ hệ thống
    """
    def __init__(self, message, action=None, params=None):
        self.message = message
        self.action = action
        self.params = params if params else {}
        
    def to_dict(self):
        """
        Chuyển đổi đề xuất thành từ điển
        """
        return {
            'message': self.message,
            'action': self.action,
            'params': self.params
        }
    
    @classmethod
    def from_dict(cls, data):
        """
        Tạo đề xuất từ từ điển
        """
        return cls(
            message=data.get('message', ''),
            action=data.get('action'),
            params=data.get('params', {})
        )

def filter_suggestions(suggestions, max_count=5):
    """
    Lọc danh sách đề xuất theo số lượng tối đa
    """
    if len(suggestions) <= max_count:
        return suggestions
    
    # Sắp xếp theo độ ưu tiên hoặc lấy các đề xuất mới nhất
    return suggestions[:max_count]