from typing import Optional


class Category:
    def __init__(self, id: str, name: str, slug: str, is_featured: bool = False, products_count: int = 0):
        self.id = id
        self.name = name
        self.slug = slug
        self.is_featured = is_featured
        self.products_count = products_count
