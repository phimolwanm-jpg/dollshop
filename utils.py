# M:/doll_shop/utils.py (ปรับปรุงเล็กน้อย)

import re # สำหรับตรวจสอบรูปแบบข้อความ (Regular Expression)
import bcrypt # สำหรับเข้ารหัสและตรวจสอบรหัสผ่าน
from datetime import datetime # สำหรับจัดการวันที่เวลา
from tkinter import messagebox # สำหรับแสดงกล่องข้อความ
# import customtkinter as ctk # ไม่ได้ใช้ ctk โดยตรงในไฟล์นี้

# --- ฟังก์ชันตรวจสอบ (Validation) ---

def validate_email(email):
    """ตรวจสอบรูปแบบอีเมล (ต้องมี @ และ . หลัง @)"""
    # ^     = เริ่มต้น string
    # [...] + = ตัวอักษรกลุ่มแรก 1 ตัวขึ้นไป (ห้ามมี @)
    # @     = ต้องมี @
    # [...] + = ตัวอักษรกลุ่มสอง 1 ตัวขึ้นไป (ห้ามมี @ หรือ .)
    # \.    = ต้องมี . (ต้องใส่ \ เพราะ . เป็นอักษรพิเศษ)
    # [...] {2,} = ตัวอักษรกลุ่มสาม 2 ตัวขึ้นไป (ส่วนขยาย เช่น com, net)
    # $     = จบ string
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$' 
    # re.match จะพยายามเทียบ pattern จาก *จุดเริ่มต้น* ของ email
    return re.match(pattern, email) is not None # คืนค่า True ถ้าเจอ pattern

def validate_phone(phone):
    """ตรวจสอบรูปแบบเบอร์โทร (รองรับ 0xx-xxx-xxxx หรือ 0xxxxxxxxxx)"""
    # ^0    = ขึ้นต้นด้วย 0
    # \d{1,2} = ตามด้วยตัวเลข 1 หรือ 2 ตัว (เช่น 8, 9, 42)
    # -?    = อาจจะมี "-" หรือไม่มีก็ได้ (ตัว ?)
    # \d{3} = ตามด้วยตัวเลข 3 ตัว
    # -?    = อาจจะมี "-" หรือไม่มีก็ได้
    # \d{4} = ตามด้วยตัวเลข 4 ตัว
    # $     = จบ string
    pattern = r'^0\d{1,2}-?\d{3}-?\d{4}$' 
    return re.match(pattern, phone) is not None

def validate_password(password):
    """ตรวจสอบความยาวรหัสผ่าน (ขั้นต่ำ 8 ตัว)"""
    # แค่เช็คความยาว
    return len(password) >= 8 

# --- ฟังก์ชันรหัสผ่าน (Password) ---

def hash_password(password):
    """เข้ารหัสรหัสผ่านด้วย bcrypt (ปลอดภัย)"""
    # password.encode() แปลง string เป็น bytes ก่อน
    # bcrypt.gensalt() สร้าง "เกลือ" (salt) แบบสุ่ม ทำให้ hash ไม่ซ้ำกัน
    hashed = bcrypt.hashpw(password.encode(), bcrypt.gensalt()) 
    return hashed # คืนค่า hashed password (เป็น bytes)

def check_password(password, hashed_password_from_db):
    """ตรวจสอบรหัสผ่านที่ user กรอก กับที่ hash เก็บไว้ใน DB"""
    # password.encode() แปลง string เป็น bytes
    # hashed_password_from_db คือ password (bytes) ที่อ่านมาจาก DB
    # bcrypt.checkpw จะทำการ hash password ที่ user กรอก (โดยใช้ salt ที่ฝังใน hashed_password_from_db)
    # แล้วเทียบว่าตรงกันหรือไม่
    return bcrypt.checkpw(password.encode(), hashed_password_from_db) # คืนค่า True ถ้าตรง

# --- ฟังก์ชันจัดรูปแบบ (Formatting) ---

def format_currency(amount):
    """จัดรูปแบบตัวเลขเป็นสกุลเงินบาท (เช่น ฿1,200.50)"""
    # f-string formatting:
    # :   = เริ่มต้น format specifier
    # ,   = ใส่ comma คั่นหลักพัน
    # .2f = แสดงเป็นเลขทศนิยม 2 ตำแหน่ง
    return f"฿{amount:,.2f}" 

def format_datetime(datetime_string_from_db):
    """จัดรูปแบบ string วันที่เวลาจาก DB (YYYY-MM-DD HH:MM:SS) เป็น DD/MM/YYYY HH:MM"""
    # ใช้ try...except เผื่อ format ที่ได้มาไม่ตรง
    try:
        # datetime.strptime แปลง string เป็น datetime object
        # ต้องระบุ format ของ string ต้นทาง ("%Y-%m-%d %H:%M:%S")
        datetime_object = datetime.strptime(datetime_string_from_db, "%Y-%m-%d %H:%M:%S") 
        # datetime_object.strftime แปลง datetime object กลับเป็น string ใน format ที่ต้องการ
        return datetime_object.strftime("%d/%m/%Y %H:%M") 
    except (ValueError, TypeError): # ดักจับ Error ถ้า format ผิด หรือ ค่าเป็น None
        # ถ้าแปลงไม่ได้ ก็คืนค่า string เดิมกลับไป
        return datetime_string_from_db 

# --- คลาส Cart (เวอร์ชัน Dictionary - อาจไม่ได้ใช้งานในโปรเจกต์หลัก) ---
# หมายเหตุ: โปรเจกต์หลักของคุณใช้ Cart จาก models.py ซึ่งใช้ CartItem object
# คลาสนี้เป็นเวอร์ชันที่ง่ายกว่า โดยใช้ Dictionary ล้วนๆ
class Cart_Dict_Version: 
    """คลาสจัดการตะกร้าสินค้า (ใช้ Dictionary เก็บข้อมูล)"""
    def __init__(self):
        # โครงสร้าง: { product_id: {'product': product_dict, 'quantity': int} }
        self.items = {}  
    
    def add_item(self, product_dict, quantity=1):
        """เพิ่มสินค้า (ที่เป็น dict) ในตะกร้า"""
        product_id = product_dict['product_id']
        if product_id in self.items:
            # ถ้ามีอยู่แล้ว บวกจำนวน
            self.items[product_id]['quantity'] += quantity
        else:
            # ถ้ายังไม่มี เพิ่มใหม่
            self.items[product_id] = {
                'product': product_dict, # เก็บ product dict ทั้งก้อน
                'quantity': quantity
            }
    
    def remove_item(self, product_id):
        """ลบสินค้าออกจากตะกร้า"""
        if product_id in self.items:
            del self.items[product_id]
    
    def update_quantity(self, product_id, quantity):
        """อัพเดทจำนวนสินค้า"""
        if product_id in self.items:
            if quantity <= 0:
                self.remove_item(product_id) # ถ้าจำนวน <= 0 ให้ลบ
            else:
                self.items[product_id]['quantity'] = quantity
    
    def get_total(self):
        """คำนวณราคารวมทั้งตะกร้า"""
        total_price = 0
        # วนลูป value (ที่เป็น dict {'product':..., 'quantity':...})
        for item_data in self.items.values(): 
            product_info = item_data['product']
            item_quantity = item_data['quantity']
            total_price += product_info['price'] * item_quantity
        return total_price
    
    def get_item_count(self):
        """นับจำนวนชิ้นสินค้าทั้งหมดในตะกร้า"""
        total_items = 0
        for item_data in self.items.values():
            total_items += item_data['quantity']
        return total_items
    
    def clear(self):
        """ล้างตะกร้า (ทำให้ dict ว่าง)"""
        self.items = {}
    
    def get_items_for_order(self):
        """
        เตรียมข้อมูล items ในรูปแบบที่ database.create_order ต้องการ
        (แต่ create_order ปัจจุบันรับ CartItem object)
        """
        order_items_list = []
        for item_data in self.items.values():
            product_info = item_data['product']
            order_items_list.append({
                'product_id': product_info['product_id'],
                'quantity': item_data['quantity'],
                'price': product_info['price'] # ราคา ณ ตอนที่หยิบใส่ตะกร้า
            })
        return order_items_list

# --- ฟังก์ชันแสดงข้อความ (Message Box Wrappers) ---

def show_message(parent_window, title_text, message_text, message_type="info"):
    """แสดงกล่องข้อความ (Info, Warning, Error)"""
    # ใช้ messagebox ที่ import ไว้ข้างบน
    if message_type == "info":
        messagebox.showinfo(title_text, message_text, parent=parent_window)
    elif message_type == "warning":
        messagebox.showwarning(title_text, message_text, parent=parent_window)
    elif message_type == "error":
        messagebox.showerror(title_text, message_text, parent=parent_window)
    else: # ถ้าใส่ type ผิด ก็ให้เป็น info
        messagebox.showinfo(title_text, message_text, parent=parent_window)

def confirm_dialog(parent_window, title_text, question_message):
    """แสดงกล่องข้อความถามยืนยัน (Yes/No)"""
    # ใช้ messagebox ที่ import ไว้ข้างบน
    # askyesno คืนค่า True ถ้ากด Yes, False ถ้ากด No
    return messagebox.askyesno(title_text, question_message, parent=parent_window)