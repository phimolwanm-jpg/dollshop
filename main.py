# M:/doll_shop/main.py (Added load_profile_image function)

import customtkinter as ctk
from PIL import Image
import os
from database import Database
from models import Session, User, Cart
# --- UI Imports ---
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
from ui_product_detail import ProductDetailWindow
from ui_admin_users import AdminUsersWindow

class MainApplication(ctk.CTk):
    """
    คลาสหลักสำหรับหน้าต่างโปรแกรม
    """
    def __init__(self):
        super().__init__()
        self.title("🎀 Dollie Shop 🎀")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        ctk.set_appearance_mode("light")

        self.db = Database()
        self.session = Session()
        self.cart = Cart()
        self.base_path = os.path.dirname(__file__)

        container_frame = ctk.CTkFrame(self, fg_color="transparent")
        container_frame.pack(side="top", fill="both", expand=True)
        container_frame.grid_rowconfigure(0, weight=1)
        container_frame.grid_columnconfigure(0, weight=1)

        self.all_app_frames = {}

        # --- Create all UI Frames ---
        # (เขียนสร้าง Frame ทุกหน้าตรงๆ)
        login_page = LoginWindow(parent=container_frame, main_app=self)
        self.all_app_frames["LoginWindow"] = login_page
        login_page.grid(row=0, column=0, sticky="nsew")

        home_page = HomeWindow(parent=container_frame, main_app=self)
        self.all_app_frames["HomeWindow"] = home_page
        home_page.grid(row=0, column=0, sticky="nsew")

        admin_page = AdminWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminWindow"] = admin_page
        admin_page.grid(row=0, column=0, sticky="nsew")

        admin_dashboard_page = AdminDashboardWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminDashboardWindow"] = admin_dashboard_page
        admin_dashboard_page.grid(row=0, column=0, sticky="nsew")

        cart_page = CartWindow(parent=container_frame, main_app=self)
        self.all_app_frames["CartWindow"] = cart_page
        cart_page.grid(row=0, column=0, sticky="nsew")

        checkout_page = CheckoutWindow(parent=container_frame, main_app=self)
        self.all_app_frames["CheckoutWindow"] = checkout_page
        checkout_page.grid(row=0, column=0, sticky="nsew")

        order_history_page = OrderHistoryWindow(parent=container_frame, main_app=self)
        self.all_app_frames["OrderHistoryWindow"] = order_history_page
        order_history_page.grid(row=0, column=0, sticky="nsew")

        product_list_page = ProductListWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ProductListWindow"] = product_list_page
        product_list_page.grid(row=0, column=0, sticky="nsew")

        thank_you_page = ThankYouWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ThankYouWindow"] = thank_you_page
        thank_you_page.grid(row=0, column=0, sticky="nsew")

        admin_orders_page = AdminOrdersWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminOrdersWindow"] = admin_orders_page
        admin_orders_page.grid(row=0, column=0, sticky="nsew")

        profile_page = ProfileWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ProfileWindow"] = profile_page
        profile_page.grid(row=0, column=0, sticky="nsew")

        receipt_page = ReceiptWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ReceiptWindow"] = receipt_page
        receipt_page.grid(row=0, column=0, sticky="nsew")

        about_page = AboutWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AboutWindow"] = about_page
        about_page.grid(row=0, column=0, sticky="nsew")

        sales_history_page = SalesHistoryWindow(parent=container_frame, main_app=self)
        self.all_app_frames["SalesHistoryWindow"] = sales_history_page
        sales_history_page.grid(row=0, column=0, sticky="nsew")

        product_detail_page = ProductDetailWindow(parent=container_frame, main_app=self)
        self.all_app_frames["ProductDetailWindow"] = product_detail_page
        product_detail_page.grid(row=0, column=0, sticky="nsew")

        admin_users_page = AdminUsersWindow(parent=container_frame, main_app=self)
        self.all_app_frames["AdminUsersWindow"] = admin_users_page
        admin_users_page.grid(row=0, column=0, sticky="nsew")

        print("สร้าง Frame ทุกหน้าเสร็จแล้ว")

        self.navigate_to("LoginWindow")

    # --- Image Loading Functions ---
    def load_image(self, image_filename, size):
        image_path = os.path.join(self.base_path, "assets", image_filename)
        try:
            pil_image = Image.open(image_path)
            ctk_image = ctk.CTkImage(pil_image, size=size)
            return ctk_image
        except Exception as e:
            print(f"เกิด Error ตอนโหลดรูป '{image_filename}': {e}")
            placeholder_image = Image.new('RGB', size, color = 'lightgray')
            ctk_placeholder = ctk.CTkImage(placeholder_image, size=size)
            return ctk_placeholder

    def get_product_image(self, product_image_filename, size=(200, 200)):
        placeholder_img = self.load_image("placeholder.png", size)
        if not product_image_filename:
            return placeholder_img
        product_image_path = os.path.join(self.base_path, "assets", "images", product_image_filename)
        try:
            pil_product_image = Image.open(product_image_path)
            ctk_product_image = ctk.CTkImage(pil_product_image, size=size)
            return ctk_product_image
        except:
            return placeholder_img

    # --- vvvv ฟังก์ชันใหม่สำหรับโหลดรูปโปรไฟล์ vvvv ---
    def load_profile_image(self, profile_image_filename, size=(100, 100)):
        """
        ฟังก์ชันช่วยโหลดรูปโปรไฟล์จาก assets/profile_pics
        ถ้าไม่เจอ หรือ filename เป็น None/ว่างเปล่า จะใช้รูป default
        """
        # ชื่อไฟล์รูปโปรไฟล์ default (ต้องมีไฟล์นี้ใน assets นะคะ!)
        default_icon = "default_profile.png"

        # ถ้าไม่มีชื่อไฟล์รูปโปรไฟล์มา หรือเป็นสตริงว่าง
        if not profile_image_filename:
            # โหลดรูป default
            return self.load_image(default_icon, size)

        # สร้าง path ไปยังไฟล์รูปโปรไฟล์ใน assets/profile_pics
        profile_image_path = os.path.join(self.base_path, "assets", "profile_pics", profile_image_filename)
        try:
            # ลองเปิดรูปโปรไฟล์
            pil_profile_image = Image.open(profile_image_path)
            # --- Make sure image has an alpha channel for masking ---
            pil_profile_image = pil_profile_image.convert("RGBA")
            ctk_profile_image = ctk.CTkImage(pil_profile_image, size=size)
            return ctk_profile_image
        except FileNotFoundError:
            # ถ้าหาไฟล์รูปโปรไฟล์ที่ระบุไม่เจอ ก็ใช้รูป default
            print(f"ไม่พบรูปโปรไฟล์ '{profile_image_filename}', ใช้รูป default แทน")
            return self.load_image(default_icon, size)
        except Exception as e:
            # ถ้าเกิด error อื่นๆ ตอนเปิดรูป ก็ใช้รูป default
            print(f"เกิด Error ตอนโหลดรูปโปรไฟล์ '{profile_image_filename}': {e}, ใช้รูป default แทน")
            return self.load_image(default_icon, size)
    # --- ^^^^ สิ้นสุดฟังก์ชันใหม่ ^^^^ ---

    # --- Navigation and Callbacks ---
    def navigate_to(self, target_page_name, **extra_data):
        print(f"กำลังจะไปหน้า: {target_page_name}, ข้อมูลแนบ: {extra_data}")
        target_frame = self.all_app_frames.get(target_page_name)
        if not target_frame:
            print(f"Error: ไม่เจอ Frame ชื่อ '{target_page_name}'!")
            return
        try:
            target_frame.on_show(**extra_data)
            print(f"เรียก on_show() ของ {target_page_name} สำเร็จ")
        except AttributeError:
            print(f"หน้า {target_page_name} ไม่มี on_show()")
            pass
        except Exception as e:
            print(f"เกิด Error ตอนเรียก on_show() ของ {target_page_name}: {e}")
        target_frame.tkraise()

    def on_login_success(self, user_data_dict):
        user_object = User.from_dict(user_data_dict)
        self.session.login(user_object)
        print(f"Login สำเร็จ: {user_object.username}, Role: {user_object.role}")
        self.navigate_to("HomeWindow")

    def on_logout(self):
        self.session.logout()
        self.cart.clear()
        print("User ออกจากระบบแล้ว")
        self.navigate_to("LoginWindow")

# --- Start the Application ---
if __name__ == "__main__":
    app = MainApplication()
    app.mainloop()