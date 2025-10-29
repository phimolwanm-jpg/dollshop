from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

# --- Data Classes  ---
@dataclass
class User:
    user_id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    role: str = 'customer'
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data):
        # ฟังก์ชันนี้ยังจำเป็นสำหรับ main.py
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone=data.get('phone'), # ใช้ .get() ป้องกัน key ไม่มี
            address=data.get('address'),
            role=data.get('role', 'customer'),
            created_at=data.get('created_at')
        )
    
    def is_admin(self) -> bool:
        # เช็คว่าเป็น admin หรือไม่
        return self.role == 'admin'

@dataclass
class Product:
    product_id: int
    name: str
    description: str
    price: float
    stock: int
    category: str
    image_url: Optional[str] = None
    created_at: Optional[str] = None
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            product_id=data['product_id'],
            name=data['name'],
            description=data.get('description'),
            price=data['price'],
            stock=data['stock'],
            category=data.get('category'),
            image_url=data.get('image_url'),
            created_at=data.get('created_at')
        )
    
    def is_available(self) -> bool:
        # เช็คว่ามีของในสต็อกหรือไม่
        return self.stock > 0

    def format_price(self) -> str:
        # จัดรูปแบบราคา (เช่น ฿1,200.50)
        return f"฿{self.price:,.2f}"
    
    def get_stock_status(self) -> tuple[str, str]:
        # คืนค่าข้อความและสีสำหรับแสดงสถานะสต็อก
        if self.stock > 10:
            return f"📦 คงเหลือ {self.stock}", "#32CD32" # สีเขียว
        elif self.stock > 0:
            return f"📦 เหลือเพียง {self.stock} ชิ้น", "#FFA500" # สีส้ม
        else:
            return "❌ สินค้าหมด", "#D22B2B" # สีแดง

@dataclass
class Order:
    order_id: int
    user_id: int
    total_amount: float
    status: str
    created_at: str
    shipping_address: str
    items: Optional[str] = None # รายการสินค้า (อาจเป็น None ถ้ายังไม่ได้ JOIN)

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data['order_id'],
            user_id=data['user_id'],
            total_amount=data['total_amount'],
            status=data.get('status', 'pending'),
            created_at=data['created_at'],
            shipping_address=data.get('shipping_address', ''),
            items=data.get('items') # ดึงรายการสินค้า (ถ้ามี)
        )

    def format_date(self) -> str:
        # จัดรูปแบบวันที่ (เช่น 29/10/2025 10:09)
        try:
            # ลองแปลงจาก format มาตรฐาน ISO
            dt_object = datetime.fromisoformat(self.created_at) 
            return dt_object.strftime("%d/%m/%Y %H:%M")
        except:
            # ถ้าแปลงไม่ได้ ก็คืนค่าเดิมไป
            return self.created_at

    def format_total(self) -> str:
        # จัดรูปแบบยอดรวม
        return f"฿{self.total_amount:,.2f}"

    def get_status_text(self) -> str:
        # แปลง status เป็นข้อความภาษาไทย
        status_map = {
            "pending": "⏳ รอดำเนินการ", 
            "confirmed": "✅ ยืนยันแล้ว", # เพิ่มสถานะ confirmed
            "shipped": "🚚 กำลังจัดส่ง", 
            "delivered": "✔️ จัดส่งสำเร็จ", 
            "cancelled": "❌ ยกเลิก"
        }
        return status_map.get(self.status, "❓ ไม่ทราบสถานะ") # ใช้ .get() ป้องกัน key ไม่มี

    def get_status_color(self) -> str:
        # คืนค่าสีตาม status
        color_map = {
            "pending": "#FFC107",   # เหลือง
            "confirmed": "#28A745", # เขียว (ใช้สีเดียวกับ delivered)
            "shipped": "#17A2B8",   # ฟ้า
            "delivered": "#28A745", # เขียว
            "cancelled": "#DC3545"  # แดง
        }
        return color_map.get(self.status, "gray") # ใช้ .get()

# --- Session Management (ปรับให้ง่าย) ---
class Session:
    # --- (ลบ _instance และ __new__ ทิ้งไป) ---
    
    def __init__(self):
        """
        เป็นคลาสธรรมดา ไม่ใช่ Singleton แล้ว
        สร้างตัวแปร current_user ตอนสร้าง object
        """
        self.current_user = None # เริ่มต้นยังไม่มีใคร login

    def login(self, user: User):
        """
        เก็บ object User ที่ login เข้ามา
        """
        self.current_user = user
   
    def logout(self):
        """
        ล้างข้อมูล user ที่ login อยู่
        """
        self.current_user = None
        
    def is_logged_in(self) -> bool:
        """
        เช็คว่ามี user login อยู่หรือไม่
        """
        return self.current_user is not None # เช็คว่าไม่ใช่ None
        
    def is_admin(self) -> bool:
        """
        เช็คว่าเป็น admin หรือไม่ (ต้อง login อยู่ด้วย)
        """
        # ต้องเช็ค is_logged_in() ก่อน เพื่อป้องกัน error ถ้า current_user เป็น None
        return self.is_logged_in() and self.current_user.is_admin()

# --- Cart Management ---
@dataclass
class CartItem:
    # เก็บ Product object ทั้งก้อน และจำนวน
    product: Product 
    quantity: int

    def get_total_price(self) -> float:
        # ราคารวมของรายการนี้ = ราคาต่อชิ้น * จำนวน
        return self.product.price * self.quantity
    
    def format_total_price(self) -> str:
        # จัดรูปแบบราคารวมของรายการนี้
        total = self.get_total_price()
        return f"฿{total:,.2f}"

class Cart:
    def __init__(self):
        """
        เป็นคลาสธรรมดา ไม่ใช่ Singleton แล้ว
        สร้าง dictionary ว่างๆ สำหรับเก็บ items ตอนสร้าง object
        โครงสร้าง: { product_id: CartItem_object }
        """
        self.items = {} 

    def add_item(self, product: Product, quantity: int = 1):
        """เพิ่มสินค้าในตะกร้า"""
        product_id = product.product_id # เอา ID สินค้ามาใช้เป็น key
        
        # เช็คว่ามีสินค้านี้ในตะกร้าหรือยัง
        if product_id in self.items:
            # ถ้ามีแล้ว ก็บวกจำนวนเพิ่มเข้าไป
            self.items[product_id].quantity += quantity
        else:
            # ถ้ายังไม่มี ก็สร้าง CartItem ใหม่ แล้วเพิ่มเข้าไปใน dict
            new_cart_item = CartItem(product=product, quantity=quantity)
            self.items[product_id] = new_cart_item

    def remove_item(self, product_id: int):
        """ลบสินค้าออกจากตะกร้า"""
        # เช็คก่อนว่ามี key นี้อยู่จริงไหม ป้องกัน error
        if product_id in self.items:
            del self.items[product_id] # ลบ key นั้นออกจาก dict

    def update_quantity(self, product_id: int, quantity: int):
        """อัพเดทจำนวนสินค้า"""
        # เช็คก่อนว่ามี key นี้อยู่จริงไหม
        if product_id in self.items:
            if quantity > 0:
                # ถ้าจำนวนใหม่มากกว่า 0 ก็อัพเดทค่า quantity
                self.items[product_id].quantity = quantity
            else:
                # ถ้าจำนวนใหม่เป็น 0 หรือติดลบ ก็ลบทิ้งไปเลย
                self.remove_item(product_id)

    def get_items(self) -> List[CartItem]:
        """คืนค่าเป็น List ของ CartItem object ทั้งหมดในตะกร้า"""
        # self.items.values() จะได้ object CartItem ทั้งหมดออกมา
        return list(self.items.values()) 

    def get_total_price(self) -> float:
        """คำนวณราคารวมทั้งตะกร้า"""
        total = 0.0
        # วนลูป CartItem แต่ละอันในตะกร้า
        for item in self.get_items(): 
            total += item.get_total_price() # เรียกใช้ get_total_price() ของ CartItem
        return total
    
    def format_total_price(self) -> str:
        """จัดรูปแบบราคารวมทั้งตะกร้า"""
        total = self.get_total_price()
        return f"฿{total:,.2f}"
        
    def clear(self):
        """ล้างตะกร้า (ทำให้ dict ว่างเปล่า)"""
        self.items = {}