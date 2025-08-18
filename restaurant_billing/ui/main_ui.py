import tkinter as tk
from tkinter import ttk, messagebox
import json
from dataclasses import dataclass
from typing import List, Dict

# GST configuration
GST_PERCENT = 5.0

# ------------------- Data Model -------------------
@dataclass
class BillItem:
    name: str
    qty: int
    unit_price: float

    @property
    def line_total(self) -> float:
        return round(self.qty * self.unit_price, 2)

def compute_totals(items: List[BillItem], discount_pct: float = 0.0) -> Dict[str, float]:
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

# ------------------- GUI App -------------------
class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🍴 Restaurant Billing System")
        self.root.geometry("950x650")
        
        self.items: List[BillItem] = []
        self.discount_pct = 0.0
        self.order_mode = tk.StringVar(value="Dine-in")
        self.payment_method = tk.StringVar(value="Cash")

        # Title
        title = tk.Label(root, text="🍴 Restaurant Billing System", font=("Arial", 22, "bold"), bg="lightblue")
        title.pack(fill=tk.X, pady=10)

        # Main frame
        self.main_frame = tk.Frame(root, padx=10, pady=10)
        self.main_frame.pack(fill=tk.BOTH, expand=True)

        # Start screen
        self.show_start_screen()

    # ------------------- Screens -------------------
    def show_start_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        label = tk.Label(self.main_frame, text="Welcome to Restaurant Billing", font=("Arial", 18))
        label.pack(pady=20)

        start_btn = tk.Button(self.main_frame, text="🆕 New Order", font=("Arial", 16), command=self.show_menu_screen)
        start_btn.pack(pady=30)

    def show_menu_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="🍽️ Select Items", font=("Arial", 16, "bold")).pack(pady=10)

        # Items (example menu)
        self.menu_items = [
            ("Pizza", 200),
            ("Burger", 120),
            ("Pasta", 150),
            ("Cold Drink", 50)
        ]

        self.item_vars = {}
        for name, price in self.menu_items:
            frame = tk.Frame(self.main_frame)
            frame.pack(anchor="w", pady=5)
            tk.Label(frame, text=f"{name} - ₹{price}", font=("Arial", 14)).pack(side=tk.LEFT, padx=10)
            qty_var = tk.IntVar(value=0)
            self.item_vars[name] = (qty_var, price)
            spin = tk.Spinbox(frame, from_=0, to=10, textvariable=qty_var, width=5)
            spin.pack(side=tk.LEFT)

        tk.Button(self.main_frame, text="✅ Generate Bill", font=("Arial", 14), command=self.generate_bill).pack(pady=20)

    # ------------------- Billing -------------------
    def generate_bill(self):
        self.items.clear()
        for name, (qty_var, price) in self.item_vars.items():
            qty = qty_var.get()
            if qty > 0:
                self.items.append(BillItem(name, qty, price))

        if not self.items:
            messagebox.showwarning("No Items", "Please select at least one item!")
            return

        totals = compute_totals(self.items, self.discount_pct)

        for widget in self.main_frame.winfo_children():
            widget.destroy()

        tk.Label(self.main_frame, text="🧾 Bill Summary", font=("Arial", 16, "bold")).pack(pady=10)

        bill_text = tk.Text(self.main_frame, width=60, height=20, font=("Courier New", 12))
        bill_text.pack(pady=10)

        bill_text.insert(tk.END, "Item\tQty\tPrice\tTotal\n")
        bill_text.insert(tk.END, "-"*40 + "\n")
        for item in self.items:
            bill_text.insert(tk.END, f"{item.name}\t{item.qty}\t{item.unit_price}\t{item.line_total}\n")
        bill_text.insert(tk.END, "-"*40 + "\n")
        bill_text.insert(tk.END, f"Subtotal:\t\t\t{totals['subtotal']}\n")
        bill_text.insert(tk.END, f"GST ({GST_PERCENT}%):\t\t\t{totals['gst_amount']}\n")
        bill_text.insert(tk.END, f"Discount:\t\t\t{totals['discount_amount']}\n")
        bill_text.insert(tk.END, f"Total:\t\t\t{totals['total']}\n")

        bill_text.config(state="disabled")

        tk.Button(self.main_frame, text="💾 Export Bill", font=("Arial", 14), command=lambda: self.export_bill(totals)).pack(pady=10)
        tk.Button(self.main_frame, text="🔄 New Order", font=("Arial", 14), command=self.show_start_screen).pack(pady=10)

    # ------------------- Export -------------------
    def export_bill(self, totals: Dict[str, float]):
        data = {
            "mode": self.order_mode.get(),
            "payment": self.payment_method.get(),
            "items": [
                {
                    "name": i.name,
                    "qty": i.qty,
                    "unit_price": i.unit_price,
                    "line_total": i.line_total
                }
                for i in self.items
            ],
            "totals": totals
        }

        with open("bill.json", "w") as f:
            json.dump(data, f, indent=2)

        messagebox.showinfo("Exported", "Bill exported to bill.json ✅")

# ------------------- Main -------------------
if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBillingApp(root)
    root.mainloop()
