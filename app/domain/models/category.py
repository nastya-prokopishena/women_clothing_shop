from typing import Optional


class Category:
    def __init__(self, name: str, slug: str, parent_id: Optional[str] = None, image: Optional[str] = None,
                 is_featured: bool = False):
        self.name = name
        self.slug = slug
        self.parent_id = parent_id
        self.image = image
        self.is_featured = is_featured