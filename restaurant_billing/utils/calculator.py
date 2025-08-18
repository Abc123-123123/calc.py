from dataclasses import dataclass
from typing import List, Dict

# Configure GST here (percent)
GST_PERCENT = 5.0

@dataclass
class BillItem:
    name: str
    qty: int
    unit_price: float

    @property
    def line_total(self) -> float:
        # Calculate line total exactly and round to 2 decimals
        return round(self.qty * self.unit_price, 2)

def compute_totals(items: List[BillItem], discount_pct: float = 0.0) -> Dict[str, float]:
    """
    Returns dict with keys:
      - subtotal
      - gst_amount
      - discount_amount
      - total
    """
    # subtotal: sum of line totals
    subtotal = round(sum(i.line_total for i in items), 2)
    gst_amount = round(subtotal * (GST_PERCENT / 100.0), 2)
    discount_amount = round(subtotal * (discount_pct / 100.0), 2) if discount_pct else 0.0
    total = round(subtotal + gst_amount - discount_amount, 2)
    return {
        "subtotal": subtotal,
        "gst_amount": gst_amount,
        "discount_amount": discount_amount,
        "total": total
    }