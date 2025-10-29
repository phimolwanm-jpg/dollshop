# M:/doll_shop/models.py (Updated User dataclass)

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List

# --- Data Classes ---
@dataclass
class User:
    user_id: int
    username: str
    email: str
    full_name: str
    phone: Optional[str] = None
    address: Optional[str] = None
    profile_image_url: Optional[str] = None # <--- เพิ่ม field นี้
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
            phone=data.get('phone'),
            address=data.get('address'),
            profile_image_url=data.get('profile_image_url'), # <--- เพิ่มการดึงค่านี้
            role=data.get('role', 'customer'),
            created_at=data.get('created_at')
        )

    def is_admin(self) -> bool:
        # เช็คว่าเป็น admin หรือไม่
        return self.role == 'admin'

# --- Product, Order, CartItem dataclasses remain the same ---
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
        return self.stock > 0

    def format_price(self) -> str:
        return f"฿{self.price:,.2f}"

    def get_stock_status(self) -> tuple[str, str]:
        if self.stock > 10:
            return f"📦 คงเหลือ {self.stock}", "#32CD32"
        elif self.stock > 0:
            return f"📦 เหลือเพียง {self.stock} ชิ้น", "#FFA500"
        else:
            return "❌ สินค้าหมด", "#D22B2B"

@dataclass
class Order:
    order_id: int
    user_id: int
    # Buyer Info (added based on database changes)
    buyer_name: Optional[str] = None
    buyer_phone: Optional[str] = None
    buyer_address: Optional[str] = None
    # Order Info
    total_amount: float
    status: str
    payment_method: Optional[str] = None
    # Shipping Info
    shipping_address: Optional[str] = None
    # Payment Info
    slip_image_url: Optional[str] = None
    # Timestamp
    created_at: str
    # Items (comes from JOIN)
    items: Optional[str] = None

    @classmethod
    def from_dict(cls, data):
        return cls(
            order_id=data['order_id'],
            user_id=data.get('user_id'), # Use get for user_id too for safety
            # Buyer
            buyer_name=data.get('buyer_name'),
            buyer_phone=data.get('buyer_phone'),
            buyer_address=data.get('buyer_address'),
            # Order
            total_amount=data['total_amount'],
            status=data.get('status', 'pending'),
            payment_method=data.get('payment_method'),
            # Shipping
            shipping_address=data.get('shipping_address', ''),
            # Payment
            slip_image_url=data.get('slip_image_url'),
            # Timestamp
            created_at=data['created_at'],
            # Items
            items=data.get('items')
        )

    def format_date(self) -> str:
        try:
            dt_object = datetime.fromisoformat(self.created_at)
            return dt_object.strftime("%d/%m/%Y %H:%M")
        except:
            return self.created_at

    def format_total(self) -> str:
        return f"฿{self.total_amount:,.2f}"

    def get_status_text(self) -> str:
        status_map = {
            "pending": "⏳ รอดำเนินการ", "confirmed": "✅ ยืนยันแล้ว",
            "shipped": "🚚 กำลังจัดส่ง", "delivered": "✔️ จัดส่งสำเร็จ",
            "cancelled": "❌ ยกเลิก"
        }
        return status_map.get(self.status, "❓ ไม่ทราบสถานะ")

    def get_status_color(self) -> str:
        color_map = {
            "pending": "#FFC107", "confirmed": "#28A745", "shipped": "#17A2B8",
            "delivered": "#28A745", "cancelled": "#DC3545"
        }
        return color_map.get(self.status, "gray")

@dataclass
class CartItem:
    product: Product
    quantity: int

    def get_total_price(self) -> float:
        return self.product.price * self.quantity

    def format_total_price(self) -> str:
        total = self.get_total_price()
        return f"฿{total:,.2f}"

# --- Session Management (Simple Version) ---
class Session:
    def __init__(self):
        self.current_user = None

    def login(self, user: User):
        self.current_user = user

    def logout(self):
        self.current_user = None

    def is_logged_in(self) -> bool:
        return self.current_user is not None

    def is_admin(self) -> bool:
        return self.is_logged_in() and self.current_user.is_admin()

# --- Cart Management (Simple Version) ---
class Cart:
    def __init__(self):
        self.items = {}

    def add_item(self, product: Product, quantity: int = 1):
        product_id = product.product_id
        if product_id in self.items:
            self.items[product_id].quantity += quantity
        else:
            new_cart_item = CartItem(product=product, quantity=quantity)
            self.items[product_id] = new_cart_item

    def remove_item(self, product_id: int):
        if product_id in self.items:
            del self.items[product_id]

    def update_quantity(self, product_id: int, quantity: int):
        if product_id in self.items:
            if quantity > 0:
                self.items[product_id].quantity = quantity
            else:
                self.remove_item(product_id)

    def get_items(self) -> List[CartItem]:
        return list(self.items.values())

    def get_total_price(self) -> float:
        total = 0.0
        for item in self.get_items():
            total += item.get_total_price()
        return total

    def format_total_price(self) -> str:
        total = self.get_total_price()
        return f"฿{total:,.2f}"

    def clear(self):
        self.items = {}