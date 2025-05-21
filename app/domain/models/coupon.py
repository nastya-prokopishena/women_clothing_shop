from datetime import datetime
from typing import List, Optional


class DiscountType:
    PERCENTAGE = "percentage"
    FIXED = "fixed"


class Coupon:
    def __init__(self, code: str, discount_type: str, value: float, min_order: Optional[float] = None,
                 expires_at: Optional[datetime] = None, used_by: Optional[List[str]] = None):
        if discount_type not in [DiscountType.PERCENTAGE, DiscountType.FIXED]:
            raise ValueError("Invalid discount type")
        self.code = code
        self.discount_type = discount_type
        self.value = value
        self.min_order = min_order
        self.expires_at = expires_at
        self.used_by = used_by or []