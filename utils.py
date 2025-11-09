import re
import bcrypt
from datetime import datetime
from tkinter import messagebox


# === ตรวจสอบข้อมูล ===

def validate_email(email):
    """ตรวจสอบอีเมลให้ถูกต้อง"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    is_valid = re.match(pattern, email) is not None
    return is_valid


def validate_phone(phone):
    """ตรวจสอบเบอร์โทร"""
    pattern = r'^0\d{1,2}-?\d{3}-?\d{4}$'
    is_valid = re.match(pattern, phone) is not None
    return is_valid


def validate_password(password):
    """ตรวจสอบรหัสผ่าน - ต้องยาวอย่างน้อย 8 ตัว"""
    is_valid = len(password) >= 8
    return is_valid


# === เข้ารหัสรหัสผ่าน ===

def hash_password(password):
    """เข้ารหัสรหัสผ่าน"""
    password_bytes = password.encode()
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password_bytes, salt)
    return hashed


def check_password(password, hashed_from_db):
    """ตรวจสอบรหัสผ่านกับที่เข้ารหัสไว้"""
    password_bytes = password.encode()
    is_match = bcrypt.checkpw(password_bytes, hashed_from_db)
    return is_match


# === จัดรูปแบบข้อมูล ===

def format_currency(amount):
    """แปลงตัวเลขเป็นรูปแบบเงินบาท"""
    formatted = f"฿{amount:,.2f}"
    return formatted


def format_datetime(datetime_str):
    """แปลงวันที่เวลาให้อ่านง่าย"""
    try:
        dt = datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        formatted = dt.strftime("%d/%m/%Y %H:%M")
        return formatted
    except (ValueError, TypeError):
        return datetime_str


# === ตะกร้าสินค้า (แบบ Dictionary) ===

class Cart_Dict_Version:
    """จัดการตะกร้าสินค้าแบบง่าย"""
    
    def __init__(self):
        self.items = {}
    
    def add_item(self, product, quantity=1):
        """เพิ่มสินค้าลงตะกร้า"""
        product_id = product['product_id']
        
        if product_id in self.items:
            # มีอยู่แล้ว - เพิ่มจำนวน
            self.items[product_id]['quantity'] += quantity
        else:
            # ยังไม่มี - เพิ่มใหม่
            self.items[product_id] = {
                'product': product,
                'quantity': quantity
            }
    
    def remove_item(self, product_id):
        """ลบสินค้าออกจากตะกร้า"""
        if product_id in self.items:
            del self.items[product_id]
    
    def update_quantity(self, product_id, quantity):
        """เปลี่ยนจำนวนสินค้า"""
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id)
            else:
                self.items[product_id]['quantity'] = quantity
    
    def get_total(self):
        """คำนวณราคารวม"""
        total = 0
        for item in self.items.values():
            price = item['product']['price']
            qty = item['quantity']
            total += price * qty
        return total
    
    def get_item_count(self):
        """นับจำนวนสินค้าทั้งหมด"""
        count = 0
        for item in self.items.values():
            count += item['quantity']
        return count
    
    def clear(self):
        """ล้างตะกร้า"""
        self.items = {}
    
    def get_items_for_order(self):
        """เตรียมข้อมูลสำหรับสั่งซื้อ"""
        order_items = []
        for item in self.items.values():
            product = item['product']
            order_items.append({
                'product_id': product['product_id'],
                'quantity': item['quantity'],
                'price': product['price']
            })
        return order_items


# === แสดงข้อความ ===

def show_message(parent, title, message, msg_type="info"):
    """แสดงกล่องข้อความ"""
    if msg_type == "info":
        messagebox.showinfo(title, message, parent=parent)
    elif msg_type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    elif msg_type == "error":
        messagebox.showerror(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)


def confirm_dialog(parent, title, question):
    """แสดงกล่องถามยืนยัน"""
    answer = messagebox.askyesno(title, question, parent=parent)
    return answer