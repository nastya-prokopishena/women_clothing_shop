from datetime import datetime
from typing import List, Optional


class Review:
    def __init__(self, product_id: str, user_id: str, rating: int, text: str,
                 images: Optional[List[str]] = None):
        if not (1 <= rating <= 5):
            raise ValueError("Rating must be between 1 and 5")
        self.product_id = product_id
        self.user_id = user_id
        self.rating = rating
        self.text = text
        self.images = images or []
        self.created_at = datetime.utcnow()