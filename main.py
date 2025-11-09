import customtkinter as ctk
from PIL import Image
import os
import sys
import subprocess
from tkinter import messagebox

# นำเข้าฐานข้อมูลและโมเดล
from database import Database
from models import Session, User, Cart

# นำเข้าหน้าจอต่างๆ
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
from ui_admin_users import AdminUsersWindow


class MainApplication(ctk.CTk):
    """โปรแกรมหลักของร้านขายตุ๊กตา"""
    
    def __init__(self):
        super().__init__()
        
        # ตั้งค่าหน้าต่างหลัก
        self.title("🎀 Dollie Shop 🎀")
        self.geometry("1280x800")
        self.minsize(1024, 768)
        ctk.set_appearance_mode("light")
        
        # หาตำแหน่งโฟลเดอร์หลัก
        self.base_path = os.path.dirname(os.path.abspath(__file__))
        print(f"โฟลเดอร์หลัก: {self.base_path}")
        
        # เชื่อมต่อฐานข้อมูล
        self.connect_database()
        
        # สร้างระบบ session และตะกร้า
        self.session = Session()
        self.cart = Cart()
        
        # สร้างพื้นที่สำหรับแสดงหน้าจอ
        self.create_container()
        
        # สร้างหน้าจอทั้งหมด
        self.create_all_windows()
        
        # เริ่มที่หน้า Login
        self.go_to_login()
    
    def connect_database(self):
        """เชื่อมต่อฐานข้อมูล"""
        try:
            self.db = Database()
            print("เชื่อมต่อฐานข้อมูลสำเร็จ")
        except Exception as error:
            print(f"เชื่อมต่อฐานข้อมูลไม่สำเร็จ: {error}")
            messagebox.showerror("ข้อผิดพลาด", 
                               f"ไม่สามารถเชื่อมต่อฐานข้อมูล:\n{error}")
            sys.exit(1)
    
    def create_container(self):
        """สร้างพื้นที่สำหรับวางหน้าจอต่างๆ"""
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.pack(side="top", fill="both", expand=True)
        container.grid_rowconfigure(0, weight=1)
        container.grid_columnconfigure(0, weight=1)
        self.container = container
    
    def create_all_windows(self):
        """สร้างหน้าจอทั้งหมดของโปรแกรม"""
        # รายการหน้าจอทั้งหมด
        window_list = [
            LoginWindow, HomeWindow, AdminWindow, AdminDashboardWindow,
            CartWindow, CheckoutWindow, OrderHistoryWindow, ProductListWindow,
            AdminOrdersWindow, ProfileWindow, ThankYouWindow, ReceiptWindow,
            AboutWindow, SalesHistoryWindow, AdminUsersWindow
        ]
        
        # เก็บหน้าจอทั้งหมดไว้ในตัวแปร
        self.windows = {}
        
        # สร้างหน้าจอทีละหน้า
        for Window in window_list:
            window_name = Window.__name__
            try:
                window = Window(parent=self.container, main_app=self)
                self.windows[window_name] = window
                window.grid(row=0, column=0, sticky="nsew")
                print(f"สร้างหน้า {window_name} สำเร็จ")
            except Exception as error:
                print(f"สร้างหน้า {window_name} ไม่สำเร็จ: {error}")
    
    def go_to_login(self):
        """ไปหน้า Login"""
        if "LoginWindow" in self.windows:
            self.navigate_to("LoginWindow")
        else:
            print("ไม่พบหน้า Login")
            error_msg = ctk.CTkLabel(self, 
                                    text="ไม่สามารถเปิดหน้า Login ได้",
                                    text_color="red",
                                    font=("Arial", 16))
            error_msg.pack(expand=True)
    
    # === โหลดรูปภาพ ===
    
    def load_image(self, image_name, size):
        """โหลดรูปจากโฟลเดอร์ assets"""
        # ถ้าไม่มีชื่อรูป ให้รูปสีเทา
        if not image_name:
            return self.make_placeholder(size, (192, 192, 192))
        
        # หาตำแหน่งรูป
        image_path = os.path.join(self.base_path, "assets", image_name)
        
        try:
            # เปิดและแปลงรูป
            img = Image.open(image_path)
            img = img.convert("RGBA")
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            return ctk_img
        except FileNotFoundError:
            print(f"ไม่พบรูป: {image_path}")
            return self.make_placeholder(size, (192, 192, 192))
        except Exception as error:
            print(f"โหลดรูป {image_name} ไม่สำเร็จ: {error}")
            return self.make_placeholder(size, (255, 0, 0))
    
    def make_placeholder(self, size, color):
        """สร้างรูปสีทึบแทนรูปจริง"""
        img = Image.new('RGBA', size, color=color)
        ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
        return ctk_img
    
    def get_product_image(self, product_image_name, size=(200, 200)):
        """โหลดรูปสินค้าจากโฟลเดอร์ assets/images"""
        # โหลดรูป placeholder ก่อน
        placeholder = self.load_image("placeholder.png", size)
        
        # ถ้าไม่มีชื่อรูป ใช้ placeholder
        if not product_image_name:
            return placeholder
        
        # หาตำแหน่งรูปสินค้า
        image_path = os.path.join(self.base_path, "assets", "images", 
                                 product_image_name)
        
        try:
            img = Image.open(image_path)
            img = img.convert("RGBA")
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            return ctk_img
        except FileNotFoundError:
            print(f"ไม่พบรูปสินค้า: {product_image_name}")
            return placeholder
        except Exception as error:
            print(f"โหลดรูปสินค้า {product_image_name} ไม่สำเร็จ: {error}")
            return placeholder
    
    def load_profile_image(self, profile_image_name, size=(100, 100)):
        """โหลดรูปโปรไฟล์จากโฟลเดอร์ assets/profile_pics"""
        # โหลดรูปเริ่มต้นก่อน
        default_img = self.load_image("default_profile.png", size)
        
        # ถ้าไม่มีชื่อรูป ใช้รูปเริ่มต้น
        if not profile_image_name:
            return default_img
        
        # หาตำแหน่งรูปโปรไฟล์
        image_path = os.path.join(self.base_path, "assets", "profile_pics",
                                 profile_image_name)
        
        try:
            img = Image.open(image_path)
            img = img.convert("RGBA")
            ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=size)
            return ctk_img
        except FileNotFoundError:
            print(f"ไม่พบรูปโปรไฟล์: {profile_image_name}")
            return default_img
        except Exception as error:
            print(f"โหลดรูปโปรไฟล์ {profile_image_name} ไม่สำเร็จ: {error}")
            return default_img
    
    # === เปลี่ยนหน้า ===
    
    def navigate_to(self, page_name, **data):
        """เปลี่ยนไปหน้าที่ต้องการ"""
        print(f"กำลังไปหน้า: {page_name}")
        
        # หาหน้าที่ต้องการ
        page = self.windows.get(page_name)
        if not page:
            print(f"ไม่พบหน้า: {page_name}")
            # กลับไปหน้า Home แทน
            if "HomeWindow" in self.windows:
                self.navigate_to("HomeWindow")
            return
        
        # เรียก on_show ถ้ามี
        if hasattr(page, 'on_show'):
            try:
                page.on_show(**data)
                print(f"เรียก on_show() สำหรับ {page_name} สำเร็จ")
            except TypeError:
                # ลองเรียกแบบไม่มีพารามิเตอร์
                try:
                    page.on_show()
                except Exception as error:
                    print(f"เรียก on_show() ไม่สำเร็จ: {error}")
            except Exception as error:
                print(f"เรียก on_show() ไม่สำเร็จ: {error}")
        
        # แสดงหน้านั้น
        page.tkraise()
    
    def on_login_success(self, user_data):
        """เมื่อ Login สำเร็จ"""
        # ตรวจสอบข้อมูลที่จำเป็น
        need_keys = ['user_id', 'username', 'email', 'full_name']
        has_all = all(key in user_data for key in need_keys)
        
        if not user_data or not has_all:
            print(f"ข้อมูลผู้ใช้ไม่ครบ: {user_data}")
            messagebox.showerror("ข้อผิดพลาด", 
                               "ข้อมูลผู้ใช้ไม่ครบถ้วน")
            self.navigate_to("LoginWindow")
            return
        
        try:
            # แปลงข้อมูลเป็น User object
            user = User.from_dict(user_data)
            if not user:
                raise ValueError("แปลงข้อมูลผู้ใช้ไม่สำเร็จ")
            
            # บันทึก session
            self.session.login(user)
            print(f"Login สำเร็จ: {user.username} ({user.role})")
            
            # ไปหน้า Home
            self.navigate_to("HomeWindow")
            
        except Exception as error:
            print(f"Login ไม่สำเร็จ: {error}")
            messagebox.showerror("ข้อผิดพลาด", 
                               f"เกิดข้อผิดพลาด:\n{error}")
            self.navigate_to("LoginWindow")
    
    def on_logout(self):
        """เมื่อกด Logout"""
        self.session.logout()
        self.cart.clear()
        print("ออกจากระบบแล้ว")
        self.navigate_to("LoginWindow")


# === เริ่มโปรแกรม ===

def check_folders():
    """ตรวจสอบและสร้างโฟลเดอร์ที่จำเป็น"""
    base = os.path.dirname(os.path.abspath(__file__))
    
    folders = [
        os.path.join(base, "assets"),
        os.path.join(base, "assets", "profile_pics"),
        os.path.join(base, "assets", "images"),
        os.path.join(base, "assets", "slips")
    ]
    
    for folder in folders:
        if not os.path.isdir(folder):
            print(f"สร้างโฟลเดอร์: {folder}")
            os.makedirs(folder, exist_ok=True)
    
    # ตรวจสอบรูป default
    default_profile = os.path.join(base, "assets", "default_profile.png")
    if not os.path.exists(default_profile):
        print("ไม่พบ default_profile.png")


if __name__ == "__main__":
    try:
        # ตรวจสอบโฟลเดอร์
        check_folders()
        
        # เริ่มโปรแกรม
        app = MainApplication()
        app.mainloop()
        
    except Exception as error:
        print(f"เปิดโปรแกรมไม่สำเร็จ: {error}")
        
        # แสดงข้อความแจ้งเตือน
        import tkinter as tk
        root = tk.Tk()
        root.withdraw()
        messagebox.showerror("ข้อผิดพลาด", 
                           f"ไม่สามารถเปิดโปรแกรมได้:\n{error}")
        root.destroy()
        sys.exit(1)