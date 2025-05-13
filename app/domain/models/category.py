from typing import Optional


class Category:
    def __init__(self, name: str, slug: str, parent_id: Optional[str] = None, image: Optional[str] = None,
                 is_featured: bool = False):
        self.name = name
        self.slug = slug
        self.is_featured = is_featured