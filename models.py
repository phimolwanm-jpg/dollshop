from datetime import datetime
from typing import Optional, List

# --- Data Classes ---

class User:
    """
    เก็บข้อมูลผู้ใช้ 1 คน (แทน @dataclass)
    """
    def __init__(self, 
                 user_id: int, 
                 username: str, 
                 email: str, 
                 full_name: str, 
                 phone: Optional[str] = None, 
                 address: Optional[str] = None, 
                 profile_image_url: Optional[str] = None, 
                 role: str = 'customer', 
                 created_at: Optional[str] = None):
        
        self.user_id = user_id
        self.username = username
        self.email = email
        self.full_name = full_name
        self.phone = phone
        self.address = address
        self.profile_image_url = profile_image_url
        self.role = role
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict):
        """
        [Factory] สร้าง User object จาก dict ที่ได้จากฐานข้อมูล
        'cls' ในที่นี้คือคลาส User
        """
        return cls(
            user_id=data['user_id'],
            username=data['username'],
            email=data['email'],
            full_name=data['full_name'],
            phone=data.get('phone'),
            address=data.get('address'),
            profile_image_url=data.get('profile_image_url'),
            role=data.get('role', 'customer'),
            created_at=data.get('created_at')
        )

    def is_admin(self) -> bool:
        """ตรวจสอบว่าผู้ใช้นี้เป็นแอดมินหรือไม่"""
        return self.role == 'admin'

# ---------------------------------------------------------------------

class Product:
    """
    เก็บข้อมูลสินค้า 1 ชิ้น (แทน @dataclass)
    """
    def __init__(self, 
                 product_id: int, 
                 name: str, 
                 description: str, 
                 price: float, 
                 stock: int, 
                 category: str, 
                 image_url: Optional[str] = None, 
                 created_at: Optional[str] = None):
        
        self.product_id = product_id
        self.name = name
        self.description = description
        self.price = price
        self.stock = stock
        self.category = category
        self.image_url = image_url
        self.created_at = created_at

    @classmethod
    def from_dict(cls, data: dict):
        """
        [Factory] สร้าง Product object จาก dict ที่ได้จากฐานข้อมูล
        """
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
        """ตรวจสอบว่าสินค้ามีในสต็อกหรือไม่"""
        return self.stock > 0

    def format_price(self) -> str:
        """คืนค่าราคาในรูปแบบ ฿1,234.50"""
        return f"฿{self.price:,.2f}"

    def get_stock_status(self) -> tuple[str, str]:
        """คืนค่าข้อความและสีสำหรับแสดงสถานะสต็อก"""
        if self.stock > 10:
            return f"📦 คงเหลือ {self.stock}", "#32CD32" # Green
        elif self.stock > 0:
            return f"📦 เหลือเพียง {self.stock} ชิ้น", "#FFA500" # Orange
        else:
            return "❌ สินค้าหมด", "#D22B2B" # Red

# ---------------------------------------------------------------------

class Order:
    """
    เก็บข้อมูลคำสั่งซื้อ 1 รายการ (แทน @dataclass)
    """
    def __init__(self, 
                 order_id: int, 
                 user_id: int, 
                 total_amount: float, 
                 status: str, 
                 created_at: str,
                 buyer_name: Optional[str] = None,
                 buyer_phone: Optional[str] = None,
                 buyer_address: Optional[str] = None,
                 payment_method: Optional[str] = None,
                 shipping_address: Optional[str] = None,
                 slip_image_url: Optional[str] = None,
                 items: Optional[str] = None):
        
        self.order_id = order_id
        self.user_id = user_id
        self.total_amount = total_amount
        self.status = status
        self.created_at = created_at
        self.buyer_name = buyer_name
        self.buyer_phone = buyer_phone
        self.buyer_address = buyer_address
        self.payment_method = payment_method
        self.shipping_address = shipping_address
        self.slip_image_url = slip_image_url
        self.items = items

    @classmethod
    def from_dict(cls, data: dict):
        """
        [Factory] สร้าง Order object จาก dict ที่ได้จากฐานข้อมูล
        """
        user_id_val = data.get('user_id')
        if user_id_val is None:
             # กรณีที่ user อาจถูกลบออกจากระบบ
             user_id_val = -1 

        return cls(
            order_id=data['order_id'],
            user_id=user_id_val,
            total_amount=data['total_amount'],
            status=data.get('status', 'pending'),
            created_at=data['created_at'],
            buyer_name=data.get('buyer_name'),
            buyer_phone=data.get('buyer_phone'),
            buyer_address=data.get('buyer_address'),
            payment_method=data.get('payment_method'),
            shipping_address=data.get('shipping_address', ''),
            slip_image_url=data.get('slip_image_url'),
            items=data.get('items')
        )

    def format_date(self) -> str:
        """แปลงข้อความเวลา (ISO) เป็นรูปแบบที่อ่านง่าย"""
        try:
            if isinstance(self.created_at, str):
                dt_object = datetime.fromisoformat(self.created_at.split('.')[0])
                return dt_object.strftime("%d/%m/%Y %H:%M")
            return "Invalid Date"
        except Exception as e:
             return self.created_at if isinstance(self.created_at, str) else "Invalid Date"

    def format_total(self) -> str:
        """คืนค่าราคารวมในรูปแบบ ฿1,234.50"""
        return f"฿{self.total_amount:,.2f}"

    def get_status_text(self) -> str:
        """แปลงสถานะ (เช่น 'pending') เป็นข้อความภาษาไทย"""
        status_map = {
            "pending": "⏳ รอดำเนินการ", "confirmed": "✅ ยืนยันแล้ว",
            "shipped": "🚚 กำลังจัดส่ง", "delivered": "✔️ จัดส่งสำเร็จ",
            "cancelled": "❌ ยกเลิก"
        }
        return status_map.get(self.status, "❓ ไม่ทราบสถานะ")

    def get_status_color(self) -> str:
        """คืนค่าสีสำหรับสถานะนั้นๆ"""
        color_map = {
            "pending": "#FFC107", "confirmed": "#28A745", "shipped": "#17A2B8",
            "delivered": "#28A745", "cancelled": "#DC3545"
        }
        return color_map.get(self.status, "gray")

# ---------------------------------------------------------------------

class CartItem:
    """
    เก็บ "สินค้า 1 ชนิด" + "จำนวน" ที่อยู่ในตะกร้า
    """
    def __init__(self, product: Product, quantity: int):
        self.product = product 
        self.quantity = quantity

    def get_total_price(self) -> float:
        """คำนวณราคารวมของแถวนี้ (ราคา x จำนวน)"""
        return self.product.price * self.quantity

    def format_total_price(self) -> str:
        """คืนค่าราคารวมของแถวนี้ในรูปแบบ ฿..."""
        total = self.get_total_price()
        return f"฿{total:,.2f}"

# ---------------------------------------------------------------------

class Session:
    """
    คลาสนี้ใช้เก็บข้อมูลว่า "ใคร" กำลังเข้าระบบอยู่
    """
    def __init__(self):
        self.current_user: Optional[User] = None 

    def login(self, user: User):
        """เก็บ User object เมื่อ login"""
        self.current_user = user

    def logout(self):
        """ลบข้อมูล User เมื่อ logout"""
        self.current_user = None

    def is_logged_in(self) -> bool:
        """ตรวจสอบว่ามี user login อยู่หรือไม่"""
        return self.current_user is not None

    def is_admin(self) -> bool:
        """ตรวจสอบว่าเป็นแอดมินหรือไม่"""
        return self.is_logged_in() and self.current_user.is_admin()

# ---------------------------------------------------------------------

class Cart:
    """
    คลาสนี้ใช้จัดการตะกร้าสินค้าของผู้ใช้ปัจจุบัน
    """
    def __init__(self):
        # โครงสร้าง: { product_id: CartItem_object }
        # เช่น: { 101: CartItem(product=..., quantity=2) }
        self.items: dict[int, CartItem] = {}

    def add_item(self, product: Product, quantity: int = 1):
        """เพิ่มสินค้าเข้าตะกร้า หรือบวกจำนวนถ้ามีอยู่แล้ว"""
        product_id = product.product_id
        
        if product_id in self.items:
            self.items[product_id].quantity += quantity
        else:
            new_cart_item = CartItem(product=product, quantity=quantity)
            self.items[product_id] = new_cart_item

    def remove_item(self, product_id: int):
        """ลบสินค้า (ทั้งแถว) ออกจากตะกร้า"""
        if product_id in self.items:
            del self.items[product_id]

    def update_quantity(self, product_id: int, quantity: int):
        """เปลี่ยนจำนวนสินค้าในตะกร้า"""
        if product_id in self.items:
            if quantity > 0:
                self.items[product_id].quantity = quantity
            else:
                self.remove_item(product_id) # ลบ ถ้าจำนวน <= 0

    def get_items(self) -> List[CartItem]:
        """ดึงรายการ CartItem ทั้งหมดในตะกร้า (เป็น list)"""
        return list(self.items.values())

    def get_total_price(self) -> float:
        """คำนวณราคารวมของทุกอย่างในตะกร้า"""
        total = 0.0
        for item in self.get_items():
            total += item.get_total_price() 
        return total

    def format_total_price(self) -> str:
        """คืนค่าราคารวมในรูปแบบ ฿..."""
        total = self.get_total_price()
        return f"฿{total:,.2f}"

    def clear(self):
        """ล้างตะกร้า (เมื่อ logout หรือสั่งซื้อสำเร็จ)"""
        self.items = {}