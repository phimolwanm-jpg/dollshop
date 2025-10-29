import customtkinter as ctk
# --- เพิ่ม import ที่จำเป็นสำหรับการโหลดรูป ---
from PIL import Image 
import os 
# --- จบส่วน import เพิ่ม ---

# --- Import ส่วนประกอบหลัก ---
from database import Database
# ใช้ Session, User, Cart จาก models.py (ที่ปรับให้ง่ายแล้ว)
from models import Session, User, Cart 
# --- ลบ import Assets ---
# from assets_loader import Assets 

# --- Import หน้าจอ UI ทั้งหมด ---
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
    คลาสหลักสำหรับหน้าต่างโปรแกรม
    ทำหน้าที่เหมือน "บ้าน" ที่เก็บหน้าจอต่างๆ (Frame) ไว้
    แล้วสลับแสดงผลทีละหน้า
    """
    def __init__(self):
        # --- 1. สร้างหน้าต่างหลัก ---
        super().__init__() # เรียก init ของ CTk

        self.title("🎀 Dollie Shop 🎀") # ชื่อบน title bar
        self.geometry("1280x800")      # ขนาดเริ่มต้น
        self.minsize(1024, 768)       # ขนาดเล็กสุดที่อนุญาต
        ctk.set_appearance_mode("light") # ใช้โหมดสว่าง

        # --- 2. สร้าง object ที่ใช้ร่วมกันทั้งโปรแกรม ---
        # สร้าง object สำหรับคุยกับ database (ไฟล์ dollshop.db)
        self.db = Database() 
        # สร้าง object สำหรับเก็บข้อมูล user ที่ login อยู่ (ตอนแรกยังไม่มี)
        self.session = Session() 
        # สร้าง object สำหรับเก็บตะกร้าสินค้า (ตอนแรกยังว่าง)
        self.cart = Cart()       
        # --- ลบ self.assets ออก ---
        # self.assets = Assets() 

        # --- เก็บ path หลักของโปรเจกต์ ---
        # os.path.dirname(__file__) คือ path ของโฟลเดอร์ที่ไฟล์ main.py นี้อยู่
        self.base_path = os.path.dirname(__file__) 

        # --- 3. สร้าง "เวที" หลัก (Container Frame) ---
        # สร้าง Frame ใสๆ ที่จะขยายเต็มหน้าต่างเสมอ
        container_frame = ctk.CTkFrame(self, fg_color="transparent") 
        # .pack() เป็นวิธีวาง widget แบบง่ายๆ
        # side="top" ชิดบน, fill="both" ขยายเต็ม, expand=True อนุญาตให้ขยาย
        container_frame.pack(side="top", fill="both", expand=True) 
        # กำหนดให้แถว 0 และ คอลัมน์ 0 ใน container ขยายได้ (จำเป็นสำหรับ .grid() ข้างใน)
        container_frame.grid_rowconfigure(0, weight=1)    
        container_frame.grid_columnconfigure(0, weight=1) 

        # --- 4. สร้าง Dictionary (ที่เก็บ) สำหรับหน้าจอทั้งหมด ---
        # เราจะเก็บ object ของแต่ละหน้าจอ (Frame) ไว้ในนี้
        # key คือ ชื่อคลาส (เช่น "LoginWindow"), value คือ object ของหน้านั้น
        self.all_app_frames = {} 

        # --- 5. สร้างหน้าจอ UI ทุกหน้าเก็บไว้เลย (เขียนตรงๆ ทีละหน้า) ---
        # สร้าง object ของ LoginWindow
        login_page = LoginWindow(parent=container_frame, main_app=self) 
        # เก็บใน dictionary
        self.all_app_frames["LoginWindow"] = login_page 
        # วางหน้าจอ login ลงใน container (แถว 0, คอลัมน์ 0) และให้ยืดเต็ม (sticky="nsew")
        login_page.grid(row=0, column=0, sticky="nsew") 

        # สร้าง object ของ HomeWindow
        home_page = HomeWindow(parent=container_frame, main_app=self)
        self.all_app_frames["HomeWindow"] = home_page
        home_page.grid(row=0, column=0, sticky="nsew")

        # สร้าง object ของ AdminWindow
        admin_page = AdminWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminWindow"] = admin_page
        admin_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ AdminDashboardWindow
        admin_dashboard_page = AdminDashboardWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminDashboardWindow"] = admin_dashboard_page
        admin_dashboard_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ CartWindow
        cart_page = CartWindow(parent=container_frame, main_app=self)
        self.all_app_frames["CartWindow"] = cart_page
        cart_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ CheckoutWindow
        checkout_page = CheckoutWindow(parent=container_frame, main_app=self)
        self.all_app_frames["CheckoutWindow"] = checkout_page
        checkout_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ OrderHistoryWindow
        order_history_page = OrderHistoryWindow(parent=container_frame, main_app=self)
        self.all_app_frames["OrderHistoryWindow"] = order_history_page
        order_history_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ ProductListWindow
        product_list_page = ProductListWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ProductListWindow"] = product_list_page
        product_list_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ ThankYouWindow
        thank_you_page = ThankYouWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ThankYouWindow"] = thank_you_page
        thank_you_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ AdminOrdersWindow
        admin_orders_page = AdminOrdersWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminOrdersWindow"] = admin_orders_page
        admin_orders_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ ProfileWindow
        profile_page = ProfileWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ProfileWindow"] = profile_page
        profile_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ ReceiptWindow
        receipt_page = ReceiptWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ReceiptWindow"] = receipt_page
        receipt_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ AboutWindow
        about_page = AboutWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AboutWindow"] = about_page
        about_page.grid(row=0, column=0, sticky="nsew")
        
        # สร้าง object ของ SalesHistoryWindow
        sales_history_page = SalesHistoryWindow(parent=container_frame, main_app=self)
        self.all_app_frames["SalesHistoryWindow"] = sales_history_page
        sales_history_page.grid(row=0, column=0, sticky="nsew")
        
        print("สร้าง Frame ทุกหน้าเสร็จแล้ว")
        
        # --- 6. แสดงหน้า Login เป็นหน้าแรก ---
        self.navigate_to("LoginWindow") 

    # --- ฟังก์ชันสำหรับโหลดรูปภาพ (ย้ายมาจาก assets_loader) ---
    def load_image(self, image_filename, size_tuple):
        """
        ฟังก์ชันช่วยโหลดรูปภาพจากโฟลเดอร์ assets
        (จะถูกเรียกใช้โดยหน้า UI ต่างๆ)
        """
        # สร้าง path เต็มไปยังไฟล์รูป
        image_path = os.path.join(self.base_path, "assets", image_filename) 
        try:
            # ใช้ PIL เปิดรูป
            pil_image = Image.open(image_path) 
            # สร้าง CTkImage object พร้อมปรับขนาด
            ctk_image = ctk.CTkImage(pil_image, size=size_tuple) 
            return ctk_image
        except Exception as e: # ดักจับ error ถ้าหาไฟล์ไม่เจอ หรือไฟล์เสีย
            print(f"เกิด Error ตอนโหลดรูป '{image_filename}': {e}")
            # ถ้าโหลดไม่ได้ สร้างรูปสีเทาแทน
            placeholder_image = Image.new('RGB', size_tuple, color = 'lightgray')
            ctk_placeholder = ctk.CTkImage(placeholder_image, size=size_tuple)
            return ctk_placeholder
            
    def get_product_image(self, product_image_filename, size_tuple=(200, 200)):
        """
        ฟังก์ชันช่วยโหลดรูปสินค้าจาก assets/images
        ถ้าไม่เจอ จะใช้รูป placeholder แทน
        """
        # โหลดรูป placeholder เตรียมไว้ก่อน (จาก assets)
        placeholder_img = self.load_image("placeholder.png", size_tuple) 

        # ถ้าไม่มีชื่อไฟล์รูปสินค้ามา ก็คืน placeholder เลย
        if not product_image_filename:
            return placeholder_img

        # สร้าง path ไปยังไฟล์รูปสินค้าใน assets/images
        product_image_path = os.path.join(self.base_path, "assets", "images", product_image_filename)
        try:
            # ลองเปิดรูปสินค้า
            pil_product_image = Image.open(product_image_path)
            ctk_product_image = ctk.CTkImage(pil_product_image, size=size_tuple)
            return ctk_product_image
        except: # ถ้าหาไม่เจอ หรือเปิดไม่ได้
            # คืนค่า placeholder ที่โหลดไว้ตอนแรก
            return placeholder_img 
    # --- จบฟังก์ชันโหลดรูปภาพ ---

    def navigate_to(self, target_page_name, **extra_data):
        """
        ฟังก์ชันสำหรับสลับไปแสดงหน้าจอ (Frame) อื่น
        target_page_name: ชื่อคลาสของหน้าจอที่จะไป (เช่น "HomeWindow")
        extra_data: ข้อมูลเพิ่มเติมที่จะส่งไปให้หน้าจอเป้าหมาย (ถ้ามี)
        """
        print(f"กำลังจะไปหน้า: {target_page_name}, ข้อมูลแนบ: {extra_data}")
        
        # ดึง object ของหน้าจอเป้าหมายจาก dictionary
        target_frame = self.all_app_frames.get(target_page_name) 
        
        # เช็คว่าหาหน้าจอเจอหรือไม่
        if not target_frame:
            print(f"Error: ไม่เจอ Frame ชื่อ '{target_page_name}'!")
            return # หยุดทำงาน

        # --- เรียกฟังก์ชัน on_show ของหน้าจอเป้าหมาย (ถ้ามี) ---
        # เพื่อให้หน้านั้นๆ refresh ข้อมูลก่อนแสดงผล
        # (ใช้ try-except แบบง่าย แทน hasattr/callable)
        try:
            # เรียก target_frame.on_show(...) โดยส่ง extra_data เข้าไปด้วย
            target_frame.on_show(**extra_data) 
            print(f"เรียก on_show() ของ {target_page_name} สำเร็จ")
        except AttributeError:
            # ถ้าหน้านั้นไม่มีฟังก์ชัน on_show ก็ไม่เป็นไร
            print(f"หน้า {target_page_name} ไม่มี on_show()") 
            pass 
        except Exception as e:
            # ถ้าเกิด error อื่นๆ ตอนเรียก on_show
            print(f"เกิด Error ตอนเรียก on_show() ของ {target_page_name}: {e}")

        # --- คำสั่งสำคัญ: ดึงหน้าจอเป้าหมายขึ้นมาแสดงทับหน้าจออื่น ---
        target_frame.tkraise() 

    def on_login_success(self, user_data_dict):
        """
        ฟังก์ชันนี้จะถูกเรียกโดย LoginWindow เมื่อ login สำเร็จ
        """
        # แปลงข้อมูล user (dict) เป็น User object (จาก models.py)
        user_object = User.from_dict(user_data_dict) 
        # สั่งให้ session เก็บข้อมูล user ที่ login
        self.session.login(user_object) 
        print(f"Login สำเร็จ: {user_object.username}, Role: {user_object.role}")
        # สั่งเปลี่ยนไปหน้า Home
        self.navigate_to("HomeWindow") 

    def on_logout(self):
        """
        ฟังก์ชันนี้จะถูกเรียกเมื่อกดปุ่มออกจากระบบ
        """
        # สั่งให้ session ล้างข้อมูล user
        self.session.logout() 
        # สั่งให้ cart ล้างข้อมูลสินค้า
        self.cart.clear() 
        print("User ออกจากระบบแล้ว")
        # สั่งเปลี่ยนกลับไปหน้า Login
        self.navigate_to("LoginWindow") 

# --- จุดเริ่มต้นการทำงานของโปรแกรม ---
# โค้ดส่วนนี้จะทำงานเมื่อเรารันไฟล์ main.py โดยตรง
if __name__ == "__main__":
    # 1. สร้าง object ของ MainApplication (ซึ่งจะไปเรียก __init__ ข้างบน)
    app = MainApplication() 
    # 2. สั่งให้หน้าต่างโปรแกรมเริ่มทำงาน (Event Loop)
    app.mainloop()