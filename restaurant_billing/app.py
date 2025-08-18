import tkinter as tk
from tkinter import ttk, messagebox
import csv
import pywhatkit as kit
import datetime
from utils.db_utils import init_db, bootstrap_menu_from_csv, fetch_menu, save_order, sales_report


class RestaurantBillingApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Restaurant Billing System")

        # Menu dictionary {item_name: price}
        self.menu = {}

        # Initialize DB and load menu
        init_db()
        bootstrap_menu_from_csv()

        # Try loading menu from DB first
        rows = fetch_menu()
        if rows:
            for _id, name, category, price in rows:
                self.menu[name] = price
        else:
            try:
                with open("data/menu.csv", newline="", encoding="utf-8") as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        key_map = {k.lower(): k for k in row.keys()}
                        item_key = key_map.get("item") or key_map.get("name")
                        price_key = key_map.get("price")
                        if not item_key or not price_key:
                            raise ValueError("CSV must contain 'Item/Name' and 'Price' columns")
                        self.menu[row[item_key]] = float(row[price_key])
            except Exception as e:
                messagebox.showerror("Error", f"Could not load menu: {e}")

        # Cart storage
        self.cart = []

        # Build UI
        self.create_widgets()

    def create_widgets(self):
        # Frame for menu
        frame1 = ttk.LabelFrame(self.root, text="Menu")
        frame1.grid(row=0, column=0, padx=10, pady=10)

        self.item_var = tk.StringVar()
        self.qty_var = tk.IntVar(value=1)

        ttk.Label(frame1, text="Item:").grid(row=0, column=0, padx=5, pady=5)
        self.item_combo = ttk.Combobox(frame1, textvariable=self.item_var, values=list(self.menu.keys()))
        self.item_combo.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(frame1, text="Qty:").grid(row=1, column=0, padx=5, pady=5)
        self.qty_entry = ttk.Entry(frame1, textvariable=self.qty_var)
        self.qty_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Button(frame1, text="Add to Cart", command=self.add_to_cart).grid(
            row=2, column=0, columnspan=2, pady=10
        )

        # Cart table
        frame2 = ttk.LabelFrame(self.root, text="Cart")
        frame2.grid(row=0, column=1, padx=10, pady=10)

        self.cart_tree = ttk.Treeview(
            frame2, columns=("Item", "Qty", "Price", "Total"), show="headings"
        )
        for col in ("Item", "Qty", "Price", "Total"):
            self.cart_tree.heading(col, text=col)
        self.cart_tree.pack()

        # Customer phone input
        frame3 = ttk.LabelFrame(self.root, text="Customer Info")
        frame3.grid(row=1, column=0, columnspan=2, padx=10, pady=10)

        ttk.Label(frame3, text="Phone (+91...):").grid(row=0, column=0, padx=5, pady=5)
        self.phone_var = tk.StringVar()
        self.phone_entry = ttk.Entry(frame3, textvariable=self.phone_var)
        self.phone_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Button(frame3, text="Generate & Send Bill", command=self.generate_bill).grid(
            row=1, column=0, columnspan=2, pady=10
        )

    def add_to_cart(self):
        item = self.item_var.get()
        qty = self.qty_var.get()
        if not item or qty <= 0:
            messagebox.showwarning("Invalid", "Please select item and quantity > 0")
            return

        price = self.menu[item]
        total = price * qty
        self.cart.append((item, qty, price, total))
        self.cart_tree.insert("", tk.END, values=(item, qty, price, total))

    def generate_bill(self):
        if not self.cart:
            messagebox.showwarning("Empty", "No items in cart")
            return

        subtotal = sum(line[3] for line in self.cart)
        gst = subtotal * 0.05
        discount = subtotal * 0.1 if subtotal > 100 else 0
        total = subtotal + gst - discount

        # Save order in DB
        save_order("Dine-In", "Cash", self.cart, subtotal, gst, discount, total)

        bill_msg = "🧾 *Restaurant Bill* 🧾\n\n"
        for item, qty, price, t in self.cart:
            bill_msg += f"{item} x{qty} = {t}\n"
        bill_msg += f"\nSubtotal: {subtotal:.2f}\nGST: {gst:.2f}\nDiscount: {discount:.2f}\n*Total: {total:.2f}*"

        # Show in popup
        messagebox.showinfo("Bill", bill_msg)

        # Send via WhatsApp
        phone = self.phone_var.get().strip()
        if phone:
            now = datetime.datetime.now()
            hour, minute = now.hour, now.minute + 1  # schedule 1 min later
            try:
                kit.sendwhatmsg(phone, bill_msg, hour, minute, wait_time=10, tab_close=True)
                messagebox.showinfo("WhatsApp", "Bill sent successfully!")
            except Exception as e:
                messagebox.showerror("WhatsApp Error", f"Could not send: {e}")

        # Reset cart
        self.cart = []
        self.cart_tree.delete(*self.cart_tree.get_children())


if __name__ == "__main__":
    root = tk.Tk()
    app = RestaurantBillingApp(root)
    root.mainloop()
