import customtkinter as ctk
from tkinter import messagebox
from models import Product


class HomeWindow(ctk.CTkFrame):
    """หน้าจอหลักของร้าน"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.session = main_app.session
        self.cart = main_app.cart
        
        # ตัวแปรสำหรับช่องค้นหา
        self.search_text = ctk.StringVar()
        
        # สร้าง UI
        self.create_page()
    
    
    def on_show(self):
        """ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เปิดหน้านี้"""
        # ล้าง UI เดิม
        for widget in self.winfo_children():
            widget.destroy()
        
        # ล้างคำค้นหาเก่า
        self.search_text = ctk.StringVar()
        
        # สร้าง UI ใหม่
        self.create_page()
    
    
    def create_page(self):
        """สร้างโครงสร้างหน้าจอ"""
        # ตั้งค่าการขยาย
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # สร้างส่วนต่างๆ
        self.create_header_bar()      # แถบด้านบน
        self.create_main_content()    # เนื้อหาหลัก
    
    
    # ==================== แถบด้านบน ====================
    def create_header_bar(self):
        """สร้างแถบด้านบน"""
        # กรอบแถบบน
        header = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=1,
            border_color="#FFEBEE"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        
        # โลโก้ร้าน (ซ้ายสุด)
        logo = ctk.CTkLabel(
            header,
            text="🎀 Dollie Shop",
            font=("IBM Plex Sans Thai", 24, "bold"),
            text_color="#FFB6C1"
        )
        logo.pack(side="left", padx=30)
        
        # ช่องค้นหา (ตรงกลาง)
        self.create_search_box(header)
        
        # ปุ่มต่างๆ (ขวาสุด)
        self.create_header_buttons(header)
    
    
    def create_search_box(self, parent):
        """สร้างช่องค้นหา"""
        search_area = ctk.CTkFrame(parent, fg_color="transparent")
        search_area.pack(side="left", padx=20, pady=10, fill="x", expand=True)
        
        # ช่องพิมพ์ค้นหา
        search_input = ctk.CTkEntry(
            search_area,
            textvariable=self.search_text,
            placeholder_text="🔍 ค้นหาตุ๊กตาทุกหมวดหมู่...",
            height=35,
            corner_radius=15,
            border_width=1,
            border_color="#FFEBEE",
            fg_color="#FFF0F5",
            font=("IBM Plex Sans Thai", 14)
        )
        search_input.bind("<Return>", self.do_search)  # กด Enter = ค้นหา
        search_input.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # ปุ่มค้นหา
        search_btn = ctk.CTkButton(
            search_area,
            text="ค้นหา",
            width=80,
            height=35,
            corner_radius=15,
            font=("IBM Plex Sans Thai", 14, "bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white",
            command=self.do_search
        )
        search_btn.pack(side="left")
    
    
    def create_header_buttons(self, parent):
        """สร้างปุ่มด้านขวาของแถบบน"""
        button_area = ctk.CTkFrame(parent, fg_color="transparent")
        button_area.pack(side="right", padx=20, pady=10)
        
        # ตรวจสอบว่า Login แล้วหรือยัง
        if self.session.is_logged_in():
            # ดึงชื่อผู้ใช้
            user_name = self.session.current_user.full_name
            
            # แสดงข้อความต้อนรับ
            welcome = ctk.CTkLabel(
                button_area,
                text=f"สวัสดี, {user_name}",
                font=("IBM Plex Sans Thai", 14),
                text_color="#6D4C41"
            )
            welcome.pack(side="left", padx=10)
            
            # ถ้าเป็น Admin แสดงปุ่มพิเศษ
            if self.session.is_admin():
                self.create_admin_buttons(button_area)
            
            # ปุ่มสำหรับผู้ใช้ทั่วไป
            self.create_user_buttons(button_area)
    
    
    def create_admin_buttons(self, parent):
        """สร้างปุ่มสำหรับแอดมิน"""
        # ปุ่ม Dashboard
        btn_dashboard = ctk.CTkButton(
            parent,
            text="📊 Dashboard",
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            text_color="white",
            font=("IBM Plex Sans Thai", 14, "bold"),
            corner_radius=15,
            height=35,
            command=self.go_to_dashboard
        )
        btn_dashboard.pack(side="left", padx=5)
        
        # ปุ่มคำสั่งซื้อ
        btn_orders = ctk.CTkButton(
            parent,
            text="📦 คำสั่งซื้อ",
            fg_color="#2196F3",
            hover_color="#42A5F5",
            text_color="white",
            font=("IBM Plex Sans Thai", 14, "bold"),
            corner_radius=15,
            height=35,
            command=self.go_to_admin_orders
        )
        btn_orders.pack(side="left", padx=5)
        
        # ปุ่มจัดการสินค้า
        btn_products = ctk.CTkButton(
            parent,
            text="⚙️ จัดการสินค้า",
            fg_color="#FF6B9D",
            hover_color="#FF8FB3",
            text_color="white",
            font=("IBM Plex Sans Thai", 14, "bold"),
            corner_radius=15,
            height=35,
            command=self.go_to_admin_products
        )
        btn_products.pack(side="left", padx=5)
    
    
    def create_user_buttons(self, parent):
        """สร้างปุ่มสำหรับผู้ใช้ทั่วไป"""
        # ปุ่มเกี่ยวกับเรา
        btn_about = ctk.CTkButton(
            parent,
            text="ℹ️ เกี่ยวกับเรา",
            fg_color="transparent",
            hover_color="#FFE4E1",
            text_color="#6D4C41",
            font=("IBM Plex Sans Thai", 14),
            command=self.go_to_about
        )
        btn_about.pack(side="left", padx=5)
        
        # ปุ่มโปรไฟล์
        btn_profile = ctk.CTkButton(
            parent,
            text="โปรไฟล์",
            fg_color="transparent",
            hover_color="#FFE4E1",
            text_color="#6D4C41",
            font=("IBM Plex Sans Thai", 14),
            command=self.go_to_profile
        )
        btn_profile.pack(side="left", padx=5)
        
        # ปุ่มประวัติการซื้อ
        btn_history = ctk.CTkButton(
            parent,
            text="ประวัติการซื้อ",
            fg_color="transparent",
            hover_color="#FFE4E1",
            text_color="#6D4C41",
            font=("IBM Plex Sans Thai", 14),
            command=self.go_to_history
        )
        btn_history.pack(side="left", padx=5)
        
        # ปุ่มตะกร้า (ไอคอน)
        cart_icon = self.main_app.load_image("cart_icon.png", size=(20, 20))
        btn_cart = ctk.CTkButton(
            parent,
            text="",
            image=cart_icon,
            width=30,
            fg_color="transparent",
            hover_color="#FFE4E1",
            command=self.go_to_cart
        )
        btn_cart.pack(side="left", padx=5)
        
        # ปุ่มออกจากระบบ
        btn_logout = ctk.CTkButton(
            parent,
            text="ออกจากระบบ",
            width=100,
            corner_radius=15,
            font=("IBM Plex Sans Thai", 14, "bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white",
            command=self.main_app.on_logout
        )
        btn_logout.pack(side="left", padx=10)
    
    
    # ฟังก์ชันไปหน้าต่างๆ
    def go_to_dashboard(self):
        self.main_app.navigate_to('AdminDashboardWindow')
    
    def go_to_admin_orders(self):
        self.main_app.navigate_to('AdminOrdersWindow')
    
    def go_to_admin_products(self):
        self.main_app.navigate_to('AdminWindow')
    
    def go_to_about(self):
        self.main_app.navigate_to('AboutWindow')
    
    def go_to_profile(self):
        self.main_app.navigate_to('ProfileWindow')
    
    def go_to_history(self):
        self.main_app.navigate_to('OrderHistoryWindow')
    
    def go_to_cart(self):
        self.main_app.navigate_to('CartWindow')
    
    
    # ==================== เนื้อหาหลัก ====================
    def create_main_content(self):
        """สร้างพื้นที่เนื้อหาหลัก (เลื่อนได้)"""
        scroll_area = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        scroll_area.grid(row=1, column=0, sticky="nsew", padx=30, pady=0)
        scroll_area.grid_columnconfigure(0, weight=1)
        
        # สร้างส่วนต่างๆ
        self.create_banner(scroll_area)           # แบนเนอร์
        self.create_categories(scroll_area)       # หมวดหมู่
        self.create_products(scroll_area)         # สินค้าแนะนำ
        self.create_footer(scroll_area)           # ท้ายหน้า
    
    
    # ==================== แบนเนอร์ ====================
    def create_banner(self, parent):
        """สร้างภาพแบนเนอร์"""
        banner_img = self.main_app.load_image("banner.png", size=(2100, 250))
        
        banner = ctk.CTkLabel(
            parent,
            text="",
            image=banner_img,
            corner_radius=20
        )
        banner.grid(row=0, column=0, sticky="ew", pady=(10, 20))
    
    
    # ==================== หมวดหมู่สินค้า ====================
    def create_categories(self, parent):
        """สร้างส่วนหมวดหมู่สินค้า"""
        # กรอบหมวดหมู่
        category_box = ctk.CTkFrame(parent, fg_color="transparent")
        category_box.grid(row=1, column=0, sticky="ew", pady=20, padx=10)
        
        # หัวข้อ
        title = ctk.CTkLabel(
            category_box,
            text="หมวดหมู่ตุ๊กตา",
            font=("IBM Plex Sans Thai", 20, "bold"),
            text_color="#6D4C41"
        )
        title.pack(anchor="w")
        
        # พื้นที่ปุ่มหมวดหมู่
        button_area = ctk.CTkFrame(category_box, fg_color="transparent")
        button_area.pack(fill="x", pady=10)
        
        # ดึงรายชื่อหมวดหมู่จาก database
        categories = self.db.get_categories()
        
        # ไอคอนสำหรับแต่ละหมวดหมู่
        icons = {
            'ตุ๊กตาหมี': '🧸',
            'ตุ๊กตากระต่าย': '🐰',
            'ตุ๊กตาแมว': '🐱',
            'ตุ๊กตาช้าง': '🐘',
            'ตุ๊กตายูนิคอร์น': '🦄',
            'ตุ๊กตาสุนัข': '🐶',
            'ตุ๊กตาไดโนเสาร์': '🦕'
        }
        
        # สร้างปุ่มแต่ละหมวดหมู่
        for category_name in categories:
            icon = icons.get(category_name, '🎀')  # ถ้าไม่เจอใช้ 🎀
            
            btn = ctk.CTkButton(
                button_area,
                text=f"{icon} {category_name}",
                height=40,
                corner_radius=20,
                font=("IBM Plex Sans Thai", 14, "bold"),
                fg_color="#FFFFFF",
                border_width=1,
                border_color="#FFEBEE",
                text_color="#6D4C41",
                hover_color="#FFE4E1",
                command=lambda c=category_name: self.open_category(c)
            )
            btn.pack(side="left", padx=5)
    
    
    def open_category(self, category_name):
        """เปิดหน้ารายการสินค้าตามหมวดหมู่"""
        self.main_app.navigate_to('ProductListWindow', category=category_name)
    
    
    # ==================== สินค้าแนะนำ ====================
    def create_products(self, parent):
        """สร้างส่วนสินค้าแนะนำ"""
        # กรอบสินค้าแนะนำ
        product_box = ctk.CTkFrame(parent, fg_color="transparent")
        product_box.grid(row=2, column=0, sticky="nsew", pady=10)
        
        # หัวข้อ
        title = ctk.CTkLabel(
            product_box,
            text="สินค้าแนะนำ ✨",
            font=("IBM Plex Sans Thai", 20, "bold"),
            text_color="#6D4C41"
        )
        title.pack(anchor="w", padx=10)
        
        # พื้นที่วางการ์ดสินค้า
        grid_area = ctk.CTkFrame(product_box, fg_color="transparent")
        grid_area.pack(fill="both", expand=True, pady=10)
        
        # ดึงสินค้า 8 รายการจาก database
        products = self.db.get_all_products(limit=8)
        
        # จำนวนคอลัมน์ต่อแถว
        columns = 4
        
        # สร้างการ์ดสินค้าทีละใบ
        for index, product_data in enumerate(products):
            # คำนวณตำแหน่ง
            row = index // columns      # แถวที่
            col = index % columns        # คอลัมน์ที่
            
            # ตั้งค่าให้คอลัมน์กว้างเท่ากัน
            grid_area.grid_columnconfigure(col, weight=1, uniform="prod_card")
            
            # แปลง dict เป็น Product object
            product = Product.from_dict(product_data)
            
            # สร้างการ์ด
            card = self.make_product_card(grid_area, product)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    
    def make_product_card(self, parent, product):
        """สร้างการ์ดสินค้า 1 ใบ"""
        # กรอบการ์ด
        card = ctk.CTkFrame(
            parent,
            fg_color="#FFFFFF",
            corner_radius=15,
            border_width=1,
            border_color="#FFEBEE"
        )
        
        # ภาพสินค้า
        product_img = self.main_app.get_product_image(product.image_url)
        img = ctk.CTkLabel(
            card,
            text="",
            image=product_img,
            bg_color="transparent"
        )
        img.pack(pady=(15, 10))
        
        # ชื่อสินค้า
        name = ctk.CTkLabel(
            card,
            text=product.name,
            font=("IBM Plex Sans Thai", 16, "bold"),
            text_color="#6D4C41"
        )
        name.pack(padx=10)
        
        # ราคา
        price = ctk.CTkLabel(
            card,
            text=product.format_price(),
            font=("IBM Plex Sans Thai", 14),
            text_color="#FFB6C1"
        )
        price.pack(pady=5)
        
        # ปุ่มหยิบใส่ตะกร้า
        btn_add = ctk.CTkButton(
            card,
            text="หยิบใส่ตะกร้า",
            height=35,
            corner_radius=10,
            font=("IBM Plex Sans Thai", 14, "bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white",
            command=lambda p=product: self.add_to_cart(p)
        )
        btn_add.pack(pady=10, padx=15, fill="x")
        
        return card
    
    
    # ==================== ท้ายหน้า ====================
    def create_footer(self, parent):
        """สร้างส่วนท้ายหน้า"""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=20)
        
        # ข้อความลิขสิทธิ์
        copyright = ctk.CTkLabel(
            footer,
            text="© 2025 Dollie Shop by Phimonwan M.",
            font=("IBM Plex Sans Thai", 12),
            text_color="gray"
        )
        copyright.pack(pady=10)
    
    
    # ==================== ฟังก์ชันการทำงาน ====================
    def do_search(self, event=None):
        """ทำการค้นหาสินค้า"""
        # ดึงคำค้นหา
        keyword = self.search_text.get().strip()
        
        # ตรวจสอบว่าพิมพ์อะไรมาหรือไม่
        if not keyword:
            messagebox.showinfo(
                "ค้นหา",
                "กรุณาพิมพ์คำค้นหา",
                parent=self
            )
            return
        
        # ไปหน้ารายการสินค้าพร้อมคำค้นหา
        print(f"กำลังค้นหา: {keyword}")
        self.main_app.navigate_to('ProductListWindow', search_term=keyword)
    
    
    def add_to_cart(self, product):
        """เพิ่มสินค้าลงตะกร้า"""
        # ตรวจสอบว่า Login แล้วหรือยัง
        if not self.session.is_logged_in():
            messagebox.showwarning(
                "กรุณาเข้าสู่ระบบ",
                "คุณต้องเข้าสู่ระบบก่อนเพิ่มสินค้าลงตะกร้า",
                parent=self
            )
            return
        
        # เพิ่มสินค้าลงตะกร้า
        self.cart.add_item(product)
        
        # แสดงข้อความแจ้งเตือน
        messagebox.showinfo(
            "ตะกร้าสินค้า",
            f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!",
            parent=self
        )