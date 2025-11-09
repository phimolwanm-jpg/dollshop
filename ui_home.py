import customtkinter as ctk
from tkinter import messagebox
from models import Product


class HomeWindow(ctk.CTkFrame):
    """หน้าหลักของร้าน"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.session = main_app.session
        self.cart = main_app.cart
        self.search_text = ctk.StringVar()
        
        self.create_page()
    
    def on_show(self):
        """เปิดหน้านี้ - รีเฟรชทั้งหมด"""
        for widget in self.winfo_children():
            widget.destroy()
        
        self.search_text = ctk.StringVar()
        self.create_page()
    
    def create_page(self):
        """สร้างหน้าจอ"""
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        self.create_top_bar()
        self.create_content()
    
    # === แถบด้านบน ===
    
    def create_top_bar(self):
        """สร้างแถบด้านบน"""
        bar = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0,
                          height=70, border_width=1, border_color="#FFEBEE")
        bar.grid(row=0, column=0, sticky="ew", pady=(0, 5))
        bar.grid_propagate(False)
        
        # โลโก้
        logo = ctk.CTkLabel(bar, text="🎀 Dollie Shop",
                           font=("IBM Plex Sans Thai", 24, "bold"),
                           text_color="#FFB6C1")
        logo.pack(side="left", padx=30, anchor="w")
        
        # --- 🛠️ (ปรับแก้) ---
        # ตรวจสอบว่าเป็น Admin หรือไม่
        # ถ้าเป็น User -> แสดงช่องค้นหา
        # ถ้าเป็น Admin -> ไม่แสดงช่องค้นหา (เพื่อเพิ่มที่ให้ปุ่ม)
        
        # (เราต้องเช็ค is_logged_in ก่อน เผื่อ session ยังไม่มี)
        is_admin = self.session.is_logged_in() and self.session.is_admin()
        
        if not is_admin:
            # (สำหรับ User หรือ Guest)
            # ช่องค้นหา
            self.create_search(bar)
        else:
            # (สำหรับ Admin)
            # สร้าง "ที่ว่าง" (Spacer) ที่ขยายได้
            # เพื่อดันปุ่มไปทางขวา (แทนที่ช่องค้นหา)
            spacer = ctk.CTkFrame(bar, fg_color="transparent")
            spacer.pack(side="left", padx=20, pady=10, fill="x", expand=True)
        # --- (สิ้นสุดการปรับแก้) ---

        # ปุ่มต่างๆ
        self.create_buttons(bar)
    
    def create_search(self, parent):
        """สร้างช่องค้นหา"""
        search_box = ctk.CTkFrame(parent, fg_color="transparent")
        search_box.pack(side="left", padx=20, pady=10, fill="x", expand=True)
        
        # ช่องพิมพ์
        entry = ctk.CTkEntry(search_box,
                            textvariable=self.search_text,
                            placeholder_text="🔍 ค้นหาตุ๊กตาทุกหมวดหมู่...",
                            height=35, corner_radius=15,
                            border_width=1, border_color="#FFEBEE",
                            fg_color="#FFF0F5",
                            font=("IBM Plex Sans Thai", 14))
        entry.bind("<Return>", self.search)
        entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        # ปุ่มค้นหา
        btn = ctk.CTkButton(search_box, text="ค้นหา",
                           width=80, height=35, corner_radius=15,
                           font=("IBM Plex Sans Thai", 14, "bold"),
                           fg_color="#FFB6C1", hover_color="#FFC0CB",
                           text_color="white", command=self.search)
        btn.pack(side="left")
    
    def create_buttons(self, parent):
        """สร้างปุ่มด้านขวา"""
        btn_area = ctk.CTkFrame(parent, fg_color="transparent")
        btn_area.pack(side="right", padx=20, pady=10, anchor="e")
        
        if self.session.is_logged_in():
            # แสดงชื่อ
            name = self.session.current_user.full_name
            welcome = ctk.CTkLabel(btn_area,
                                  text=f"สวัสดี, {name}",
                                  font=("IBM Plex Sans Thai", 14),
                                  text_color="#6D4C41")
            welcome.pack(side="left", padx=10)
            
            # ถ้าเป็น Admin
            if self.session.is_admin():
                self.add_admin_buttons(btn_area)
            
            # ปุ่มผู้ใช้ทั่วไป
            self.add_user_buttons(btn_area)
    
    def add_admin_buttons(self, parent):
        """เพิ่มปุ่มสำหรับ Admin"""
        # Dashboard
        btn1 = ctk.CTkButton(parent, text="📊 Dashboard",
                            fg_color="#4CAF50", hover_color="#66BB6A",
                            text_color="white",
                            font=("IBM Plex Sans Thai", 14, "bold"),
                            corner_radius=15, height=35,
                            command=self.go_dashboard)
        btn1.pack(side="left", padx=5)
        
        # คำสั่งซื้อ
        btn2 = ctk.CTkButton(parent, text="📦 คำสั่งซื้อ",
                            fg_color="#2196F3", hover_color="#42A5F5",
                            text_color="white",
                            font=("IBM Plex Sans Thai", 14, "bold"),
                            corner_radius=15, height=35,
                            command=self.go_orders)
        btn2.pack(side="left", padx=5)
        
        # จัดการสินค้า
        btn3 = ctk.CTkButton(parent, text="⚙️ จัดการสินค้า",
                            fg_color="#FF6B9D", hover_color="#FF8FB3",
                            text_color="white",
                            font=("IBM Plex Sans Thai", 14, "bold"),
                            corner_radius=15, height=35,
                            command=self.go_products)
        btn3.pack(side="left", padx=5)
    
    def add_user_buttons(self, parent):
        """เพิ่มปุ่มสำหรับผู้ใช้"""
        # เกี่ยวกับเรา
        btn_about = ctk.CTkButton(parent, text="เกี่ยวกับเรา",
                                 fg_color="transparent", 
                                 hover_color="#FFE4E1",
                                 text_color="#6D4C41",
                                 font=("IBM Plex Sans Thai", 14),
                                 command=self.go_about)
        btn_about.pack(side="left", padx=5)
        
        # โปรไฟล์
        btn_profile = ctk.CTkButton(parent, text="โปรไฟล์",
                                   fg_color="transparent", 
                                   hover_color="#FFE4E1",
                                   text_color="#6D4C41",
                                   font=("IBM Plex Sans Thai", 14),
                                   command=self.go_profile)
        btn_profile.pack(side="left", padx=5)
        
        # ประวัติการซื้อ
        btn_history = ctk.CTkButton(parent, text="ประวัติการซื้อ",
                                   fg_color="transparent", 
                                   hover_color="#FFE4E1",
                                   text_color="#6D4C41",
                                   font=("IBM Plex Sans Thai", 14),
                                   command=self.go_history)
        btn_history.pack(side="left", padx=5)
        
        # ปุ่มตะกร้า (ไอคอน)
        cart_icon = self.main_app.load_image("cart_icon.png", size=(20, 20))
        btn_cart = ctk.CTkButton(parent, 
                                text="",
                                image=cart_icon,
                                width=30,
                                fg_color="transparent",
                                hover_color="#FFE4E1",
                                command=self.go_cart)
        btn_cart.pack(side="left", padx=5)
        
        # ปุ่มออกจากระบบ
        btn_logout = ctk.CTkButton(parent, 
                                  text="ออกจากระบบ",
                                  width=100,
                                  corner_radius=15,
                                  font=("IBM Plex Sans Thai", 14, "bold"),
                                  fg_color="#FFB6C1",
                                  hover_color="#FFC0CB",
                                  text_color="white",
                                  command=self.main_app.on_logout)
        btn_logout.pack(side="left", padx=10)
    
    # === เนื้อหาหลัก ===
    
    def create_content(self):
        """สร้างเนื้อหาหลัก"""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color="#FFB6C1")
        scroll.grid(row=1, column=0, sticky="nsew", padx=30, pady=0)
        scroll.grid_columnconfigure(0, weight=1)
        
        self.create_banner(scroll)
        self.create_categories(scroll)
        self.create_products(scroll)
        self.create_footer(scroll)
    
    def create_banner(self, parent):
        """สร้างแบนเนอร์"""
        img = self.main_app.load_image("banner.png", size=(2100, 250))
        banner = ctk.CTkLabel(parent, text="", image=img,
                             corner_radius=20)
        banner.grid(row=0, column=0, sticky="ew", pady=(10, 20))
    
    def create_categories(self, parent):
        """สร้างหมวดหมู่สินค้า"""
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=1, column=0, sticky="ew", pady=20, padx=10)
        
        # หัวข้อ
        title = ctk.CTkLabel(box, text="หมวดหมู่ตุ๊กตา",
                            font=("IBM Plex Sans Thai", 20, "bold"),
                            text_color="#6D4C41")
        title.pack(anchor="w")
        
        # พื้นที่ปุ่ม
        btn_area = ctk.CTkFrame(box, fg_color="transparent")
        btn_area.pack(fill="x", pady=10)
        
        # ดึงหมวดหมู่
        categories = self.db.get_categories()
        
        # ไอคอน
        icons = {
            'ตุ๊กตาหมี': '🧸',
            'ตุ๊กตากระต่าย': '🐰',
            'ตุ๊กตาแมว': '🐱',
            'ตุ๊กตาช้าง': '🐘',
            'ตุ๊กตายูนิคอร์น': '🦄',
            'ตุ๊กตาสุนัข': '🐶',
            'ตุ๊กตาไดโนเสาร์': '🦕'
        }
        
        # สร้างปุ่มแต่ละหมวด
        for cat in categories:
            icon = icons.get(cat, '🎀')
            
            btn = ctk.CTkButton(btn_area,
                               text=f"{icon} {cat}",
                               height=40, corner_radius=20,
                               font=("IBM Plex Sans Thai", 14, "bold"),
                               fg_color="#FFFFFF",
                               border_width=1, border_color="#FFEBEE",
                               text_color="#6D4C41",
                               hover_color="#FFE4E1",
                               command=lambda c=cat: self.open_category(c))
            btn.pack(side="left", padx=5)
    
    def create_products(self, parent):
        """สร้างสินค้าแนะนำ"""
        box = ctk.CTkFrame(parent, fg_color="transparent")
        box.grid(row=2, column=0, sticky="nsew", pady=10)
        
        # หัวข้อ
        title = ctk.CTkLabel(box, text="สินค้าแนะนำ ✨",
                            font=("IBM Plex Sans Thai", 20, "bold"),
                            text_color="#6D4C41")
        title.pack(anchor="w", padx=10)
        
        # พื้นที่การ์ด
        grid = ctk.CTkFrame(box, fg_color="transparent")
        grid.pack(fill="both", expand=True, pady=10)
        
        # ดึงสินค้า 8 รายการ
        products = self.db.get_all_products(limit=8)
        
        # จำนวนคอลัมน์
        cols = 4
        
        # สร้างการ์ดทีละใบ
        for i, p_data in enumerate(products):
            row = i // cols
            col = i % cols
            
            grid.grid_columnconfigure(col, weight=1, uniform="card")
            
            product = Product.from_dict(p_data)
            card = self.make_card(grid, product)
            card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
    
    def make_card(self, parent, product):
        """สร้างการ์ดสินค้า 1 ใบ"""
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF",
                           corner_radius=15,
                           border_width=1, border_color="#FFEBEE")
        
        # รูป
        img = self.main_app.get_product_image(product.image_url)
        img_label = ctk.CTkLabel(card, text="", image=img,
                                bg_color="transparent")
        img_label.pack(pady=(15, 10))
        
        # ชื่อ
        name = ctk.CTkLabel(card, text=product.name,
                           font=("IBM Plex Sans Thai", 16, "bold"),
                           text_color="#6D4C41")
        name.pack(padx=10)
        
        # ราคา
        price = ctk.CTkLabel(card, text=product.format_price(),
                            font=("IBM Plex Sans Thai", 14),
                            text_color="#FFB6C1")
        price.pack(pady=5)
        
        # ปุ่มหยิบ
        btn = ctk.CTkButton(card, text="หยิบใส่ตะกร้า",
                           height=35, corner_radius=10,
                           font=("IBM Plex Sans Thai", 14, "bold"),
                           fg_color="#FFB6C1", hover_color="#FFC0CB",
                           text_color="white",
                           command=lambda p=product: self.add_to_cart(p))
        btn.pack(pady=10, padx=15, fill="x")
        
        return card
    
    def create_footer(self, parent):
        """สร้างท้ายหน้า"""
        footer = ctk.CTkFrame(parent, fg_color="transparent")
        footer.grid(row=3, column=0, sticky="ew", pady=20)
        
        text = ctk.CTkLabel(footer,
                           text="© 2025 Dollie Shop by Phimonwan M.",
                           font=("IBM Plex Sans Thai", 12),
                           text_color="gray")
        text.pack(pady=10)
    
    # === ฟังก์ชันการทำงาน ===
    
    def search(self, event=None):
        """ค้นหาสินค้า"""
        keyword = self.search_text.get().strip()
        
        if not keyword:
            messagebox.showinfo("ค้นหา", "กรุณาพิมพ์คำค้นหา",
                              parent=self)
            return
        
        self.main_app.navigate_to('ProductListWindow', search_term=keyword)
    
    def open_category(self, category):
        """เปิดหมวดหมู่"""
        self.main_app.navigate_to('ProductListWindow', category=category)
    
    def add_to_cart(self, product):
        """เพิ่มลงตะกร้า"""
        if not self.session.is_logged_in():
            messagebox.showwarning("กรุณาเข้าสู่ระบบ",
                                  "คุณต้องเข้าสู่ระบบก่อนเพิ่มสินค้าลงตะกร้า",
                                  parent=self)
            return
        
        self.cart.add_item(product)
        messagebox.showinfo("ตะกร้าสินค้า",
                           f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!",
                           parent=self)
    
    # === ไปหน้าอื่นๆ ===
    
    def go_dashboard(self):
        self.main_app.navigate_to('AdminDashboardWindow')
    
    def go_orders(self):
        self.main_app.navigate_to('AdminOrdersWindow')
    
    def go_products(self):
        self.main_app.navigate_to('AdminWindow')
    
    def go_about(self):
        self.main_app.navigate_to('AboutWindow')
    
    def go_profile(self):
        self.main_app.navigate_to('ProfileWindow')
    
    def go_history(self):
        self.main_app.navigate_to('OrderHistoryWindow')
    
    def go_cart(self):
        self.main_app.navigate_to('CartWindow')