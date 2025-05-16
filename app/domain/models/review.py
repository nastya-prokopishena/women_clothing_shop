# app/domain/models.py
class Review:
    def __init__(self, id, product_id, user_name, text, created_at, rating=0, images=None):
        self.id = id
        self.product_id = product_id
        self.user_name = user_name
        self.text = text
        self.created_at = created_at
        self.rating = rating
        self.images = images or []