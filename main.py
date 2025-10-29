import customtkinter as ctk
from database import Database
from models import Session, User, Cart
from assets_loader import Assets
from ui_login import LoginWindow
from ui_home import HomeWindow
from ui_admin import AdminWindow
from ui_admin_dashboard import AdminDashboardWindow
from ui_cart import CartWindow
from ui_checkout import CheckoutWindow
from ui_order_history import OrderHistoryWindow
from ui_product_list import ProductListWindow
from ui_admin_orders import AdminOrdersWindow 
from ui_profile import ProfileWindow
from ui_thankyou import ThankYouWindow
from ui_receipt import ReceiptWindow
from ui_about import AboutWindow  
from ui_sales_history import SalesHistoryWindow

class MainApplication(ctk.CTk):
    """
    คลาสหลักของโปรแกรม ทำหน้าที่เป็น "บ้าน"
    ที่คอยควบคุมการแสดงผลของหน้าจอ (Frame) ต่างๆ
    ใช้สถาปัตยกรรมแบบ Single-Window Application ที่มีประสิทธิภาพ
    """
    def __init__(self):
        super().__init__()

        self.title("🎀 Dollie Shop 🎀")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        ctk.set_appearance_mode("light")

        # --- 1. โหลดส่วนประกอบหลักที่ต้องใช้ทั้งโปรแกรมเพียงครั้งเดียว ---
        self.db = Database()
        self.session = Session()
        self.cart = Cart()
        # โหลด Assets (รูปภาพ, ไอคอน) ทั้งหมดล่วงหน้าเพื่อประสิทธิภาพสูงสุด
        self.assets = Assets() 

        # --- 2. สร้าง Container หลักสำหรับวาง Frame ทั้งหมด ---
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)

        self.frames = {} # Dictionary สำหรับเก็บ Frame (หน้าจอ) ทั้งหมด

        # --- 3. สร้าง Instance ของแต่ละหน้าจอและเก็บไว้ใน Dictionary ---
        # เราสร้างทุกหน้าจอเตรียมไว้ตั้งแต่แรก และจะใช้ .tkraise() เพื่อสลับแสดงผล
        # ซึ่งเร็วกว่าการสร้าง-ทำลาย Frame ใหม่ทุกครั้ง
        all_windows = (
            LoginWindow, 
            HomeWindow, 
            AdminWindow, 
            AdminDashboardWindow,
            CartWindow, 
            CheckoutWindow, 
            OrderHistoryWindow, 
            ProductListWindow, 
            ThankYouWindow,
            AdminOrdersWindow, 
            ProfileWindow,
            ReceiptWindow,
            AboutWindow,
            SalesHistoryWindow
        )
        
        for F in all_windows:
            page_name = F.__name__
            frame = F(parent=container, main_app=self)
            self.frames[page_name] = frame
            frame.grid(row=0, column=0, sticky="nsew")
        
        print("All frames initialized successfully.")
        
        # --- 4. เริ่มต้นด้วยการแสดงหน้า Login ---
        self.navigate_to("LoginWindow")

    def navigate_to(self, page_name, **kwargs):
        """
        ฟังก์ชันหัวใจหลักในการสลับหน้าจอ (Frame)
        สามารถรับและส่งต่อ arguments (kwargs) ไปยังหน้าจอเป้าหมายได้
        """
        print(f"Navigating to: {page_name} with args: {kwargs}")
        frame = self.frames.get(page_name)
        if not frame:
            print(f"Error: Frame '{page_name}' not found!")
            return

        # ตรวจสอบว่า Frame นั้นๆ มีฟังก์ชัน on_show หรือไม่
        # เราจะใช้ on_show เพื่อ "รีเฟรช" ข้อมูลให้เป็นปัจจุบันทุกครั้งที่กลับมาหน้านั้นๆ
        if hasattr(frame, 'on_show') and callable(getattr(frame, 'on_show')):
            frame.on_show(**kwargs) # ส่ง kwargs เข้าไปใน on_show

        # ดึง Frame ที่ต้องการขึ้นมาแสดงผลทับอันอื่น
        frame.tkraise() 

    def on_login_success(self, user_data):
        """
        Callback function นี้จะถูกเรียกใช้โดย LoginWindow เมื่อล็อกอินสำเร็จ
        """
        # แปลง dict เป็น User object ก่อนเก็บใน session
        user = User.from_dict(user_data) 
        self.session.login(user)
        print(f"Login successful for user: {user.username}, Role: {user.role}")
        self.navigate_to("HomeWindow")

    def on_logout(self):
        """
        Callback function นี้จะถูกเรียกใช้โดย HomeWindow (หรือหน้าอื่นๆ) เมื่อกดออกจากระบบ
        """
        self.session.logout()
        self.cart.clear() # ล้างตะกร้าสินค้าเมื่อออกจากระบบ
        print("User logged out.")
        self.navigate_to("LoginWindow")

# --- จุดเริ่มต้นการทำงานของโปรแกรม ---
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()