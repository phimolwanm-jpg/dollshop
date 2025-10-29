import customtkinter as ctk
from tkinter import messagebox
# Product ไม่ได้ถูก *ใช้* โดยตรงใน UI แล้ว (แต่ยังใช้ใน add_to_cart)
# แต่ import ไว้เผื่อ (ตามสไตล์พื้นฐาน)
from models import Product 

class HomeWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.db = main_app.db
        self.session = main_app.session
        self.cart = main_app.cart
        # --- ไม่ต้องมี self.assets ถ้าใช้ main_app.load_image ---
        # self.assets = main_app.assets 

        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ Header (ชื่อ user, ปุ่ม admin) และรายการสินค้าอัปเดตเสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 

    def setup_ui(self):
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # ให้แถวที่ 1 (main_frame) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1) 
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 

        # --- 2. สร้างส่วนหัว (Header) ---
        # (ย้ายโค้ดจาก create_header มาไว้ตรงนี้)
        header = ctk.CTkFrame(
            self, # ใส่ header ลงใน HomeWindow (self)
            fg_color="#FFFFFF", 
            corner_radius=0, 
            height=70, 
            border_width=1, 
            border_color="#FFEBEE"
        )
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดัน widget ทางขวาไปชิดขวา)
        header.grid_columnconfigure(1, weight=1) 

        # --- 2.1 ใส่ Logo และชื่อร้าน (ชิดซ้าย) ---
        shop_title_label = ctk.CTkLabel(
            header, 
            text="🎀 Dollie Shop", 
            font=("IBM Plex Sans Thai", 24, "bold"), 
            text_color="#FFB6C1"
        )
        shop_title_label.pack(side="left", padx=30)

        # --- 2.2 สร้าง Frame สำหรับ widget ทางขวา ---
        right_header_frame = ctk.CTkFrame(header, fg_color="transparent")
        right_header_frame.pack(side="right", padx=20, pady=10)

        # --- 2.3 แสดงข้อความต้อนรับ ---
        # ดึงชื่อ user จาก session
        user_full_name = self.session.current_user.full_name 
        welcome_text = f"สวัสดี, {user_full_name}"
        welcome_label = ctk.CTkLabel(
            right_header_frame, 
            text=welcome_text, 
            font=("IBM Plex Sans Thai", 14), 
            text_color="#6D4C41"
        )
        welcome_label.pack(side="left", padx=10)
        
        # --- 2.4 ตรวจสอบว่าเป็น Admin หรือไม่ ---
        # เพื่อแสดงปุ่มเฉพาะ Admin
        is_current_user_admin = self.session.is_admin() 
        if is_current_user_admin:
            # --- ถ้าเป็น Admin: สร้างปุ่มสำหรับ Admin ---
            # ปุ่ม Dashboard
            admin_dashboard_btn = ctk.CTkButton(
                right_header_frame, 
                text="📊 Dashboard", 
                fg_color="#4CAF50", hover_color="#66BB6A", text_color="white", 
                font=("IBM Plex Sans Thai", 14, "bold"),
                corner_radius=15, height=35,
                command=lambda: self.main_app.navigate_to('AdminDashboardWindow')
            )
            admin_dashboard_btn.pack(side="left", padx=5)
            
            # ปุ่ม คำสั่งซื้อ (Admin)
            admin_orders_btn = ctk.CTkButton(
                right_header_frame, 
                text="📦 คำสั่งซื้อ", 
                fg_color="#2196F3", hover_color="#42A5F5", text_color="white", 
                font=("IBM Plex Sans Thai", 14, "bold"),
                corner_radius=15, height=35,
                command=lambda: self.main_app.navigate_to('AdminOrdersWindow')
            )
            admin_orders_btn.pack(side="left", padx=5)
            
            # ปุ่ม จัดการสินค้า
            admin_product_btn = ctk.CTkButton(
                right_header_frame, 
                text="⚙️ จัดการสินค้า", 
                fg_color="#FF6B9D", hover_color="#FF8FB3", text_color="white", 
                font=("IBM Plex Sans Thai", 14, "bold"),
                corner_radius=15, height=35,
                command=lambda: self.main_app.navigate_to('AdminWindow')
            )
            admin_product_btn.pack(side="left", padx=5)
        # --- จบเงื่อนไข if is_admin ---
        
        # --- 2.5 สร้างปุ่มสำหรับผู้ใช้ทุกคน ---
        # ปุ่ม โปรไฟล์
        profile_btn = ctk.CTkButton(
            right_header_frame, 
            text="โปรไฟล์", 
            fg_color="transparent", hover_color="#FFE4E1", text_color="#6D4C41", 
            font=("IBM Plex Sans Thai", 14), 
            command=lambda: self.main_app.navigate_to('ProfileWindow')
        )
        profile_btn.pack(side="left", padx=5)
        
        # ปุ่ม ประวัติการซื้อ
        history_btn = ctk.CTkButton(
            right_header_frame, 
            text="ประวัติการซื้อ", 
            fg_color="transparent", hover_color="#FFE4E1", text_color="#6D4C41", 
            font=("IBM Plex Sans Thai", 14), 
            command=lambda: self.main_app.navigate_to('OrderHistoryWindow')
        )
        history_btn.pack(side="left", padx=5)
        
        # ปุ่ม ตะกร้า (ใช้รูปภาพ)
        # โหลดรูปตะกร้า (สมมติว่า main.py มี load_image แล้ว)
        cart_icon_image = self.main_app.load_image("cart_icon.png", size=(20, 20)) 
        cart_btn = ctk.CTkButton(
            right_header_frame, 
            text="", # ไม่มีข้อความ
            image=cart_icon_image, # ใส่รูปภาพ
            width=30, # กำหนดความกว้างเล็กๆ
            fg_color="transparent", hover_color="#FFE4E1", 
            command=lambda: self.main_app.navigate_to('CartWindow')
        )
        cart_btn.pack(side="left", padx=5)

        # ปุ่ม ออกจากระบบ
        logout_btn = ctk.CTkButton(
            right_header_frame, 
            text="ออกจากระบบ", 
            width=100, corner_radius=15, 
            font=("IBM Plex Sans Thai", 14, "bold"), 
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white", 
            command=self.main_app.on_logout # เรียกฟังก์ชัน on_logout ของ main_app โดยตรง
        )
        logout_btn.pack(side="left", padx=10)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (เลื่อนได้) ---
        main_content_frame = ctk.CTkScrollableFrame(
            self, # ใส่ใน HomeWindow (self)
            fg_color="transparent", 
            scrollbar_button_color="#FFB6C1"
        )
        # วางในแถว 1 (ใต้ header) ยืดเต็มพื้นที่
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=0) 
        # ให้คอลัมน์ 0 ใน frame นี้ขยายเต็มความกว้าง
        main_content_frame.grid_columnconfigure(0, weight=1) 

        # --- 4. สร้างส่วน Banner ---
        # (ย้ายโค้ดจาก create_banner มาไว้ตรงนี้)
        # โหลดรูป banner (สมมติว่า main.py มี load_image แล้ว)
        banner_image = self.main_app.load_image("banner.png", size=(2100, 250)) 
        banner_label = ctk.CTkLabel(
            main_content_frame, # ใส่ใน frame ที่เลื่อนได้
            text="", 
            image=banner_image, 
            corner_radius=20 # ทำให้มุมมน
        )
        # ใช้ grid วาง banner ใน main_content_frame แถว 0
        banner_label.grid(row=0, column=0, sticky="ew", pady=(10, 20)) 
        # --- จบส่วน Banner ---

        # --- 5. สร้างส่วน หมวดหมู่ ---
        # (ย้ายโค้ดจาก create_categories มาไว้ตรงนี้)
        category_section_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง section นี้ใน main_content_frame แถว 1
        category_section_frame.grid(row=1, column=0, sticky="ew", pady=20, padx=10) 
        
        # Label หัวข้อ "หมวดหมู่ตุ๊กตา"
        category_title_label = ctk.CTkLabel(
            category_section_frame, 
            text="หมวดหมู่ตุ๊กตา", 
            font=("IBM Plex Sans Thai", 20, "bold"), 
            text_color="#6D4C41"
        )
        category_title_label.pack(anchor="w") # anchor="w" ชิดซ้าย
        
        # Frame สำหรับวางปุ่มหมวดหมู่เรียงกัน
        category_buttons_frame = ctk.CTkFrame(category_section_frame, fg_color="transparent")
        category_buttons_frame.pack(fill="x", pady=10) # fill="x" ยืดเต็มกว้าง

        # ดึงรายชื่อหมวดหมู่จาก DB
        categories_list = self.db.get_categories() 
        # เตรียม Emoji สำหรับแต่ละหมวดหมู่
        category_icons = {
            'ตุ๊กตาหมี': '🧸', 
            'ตุ๊กตากระต่าย': '🐰', 
            'ตุ๊กตาแมว': '🐱',
            'ตุ๊กตาช้าง': '🐘',
            'ตุ๊กตายูนิคอร์น': '🦄',
            'ตุ๊กตาสุนัข': '🐶',
            'ตุ๊กตาไดโนเสาร์': '🦕'
            # เพิ่มหมวดหมู่อื่นๆ พร้อม icon ที่นี่ได้
        }
        
        # วนลูปสร้างปุ่มสำหรับแต่ละหมวดหมู่
        for category_name in categories_list:
            # หา icon (ถ้าไม่เจอ ใช้ '🎀' เป็น default)
            icon = category_icons.get(category_name, '🎀') 
            # สร้างปุ่ม
            category_button = ctk.CTkButton(
                category_buttons_frame, # ใส่ปุ่มลงใน frame นี้
                text=f"{icon} {category_name}", # ข้อความบนปุ่ม (Icon + ชื่อ)
                height=40, corner_radius=20, 
                font=("IBM Plex Sans Thai", 14, "bold"),
                fg_color="#FFFFFF", border_width=1, border_color="#FFEBEE", # สีขาว ขอบชมพูอ่อน
                text_color="#6D4C41", hover_color="#FFE4E1", # สี hover ชมพูอ่อน
                # เมื่อกดปุ่ม ให้ไปหน้า ProductList พร้อมส่ง category_name ไปด้วย
                # ใช้ lambda capture (c=category_name) เพื่อให้ส่งค่าที่ถูกต้อง
                command=lambda c=category_name: self.main_app.navigate_to('ProductListWindow', category=c) 
            )
            # วางปุ่มเรียงไปทางซ้าย
            category_button.pack(side="left", padx=5) 
        # --- จบส่วน หมวดหมู่ ---

        # --- 6. สร้างส่วน สินค้าแนะนำ ---
        # (ย้ายโค้ดจาก create_product_display มาไว้ตรงนี้)
        recommended_section_container = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง section นี้ใน main_content_frame แถว 2
        recommended_section_container.grid(row=2, column=0, sticky="nsew", pady=10) 
        
        # Label หัวข้อ "สินค้าแนะนำ"
        recommended_title_label = ctk.CTkLabel(
            recommended_section_container, 
            text="สินค้าแนะนำ ✨", 
            font=("IBM Plex Sans Thai", 20, "bold"), 
            text_color="#6D4C41"
        )
        recommended_title_label.pack(anchor="w", padx=10)
        
        # Frame สำหรับวาง Grid ของการ์ดสินค้า
        products_grid_frame = ctk.CTkFrame(recommended_section_container, fg_color="transparent")
        products_grid_frame.pack(fill="both", expand=True, pady=10)
        
        # ดึงข้อมูลสินค้า 8 ชิ้นแรกจาก DB
        recommended_products_data = self.db.get_all_products(limit=8) 
        
        cols = 4 # กำหนดว่าจะแสดง 4 คอลัมน์
        
        # วนลูปสร้างการ์ดสินค้าและวางลงใน Grid
        for i, product_dict in enumerate(recommended_products_data):
            # คำนวณแถว (row) และคอลัมน์ (col) จาก index (i)
            row, col = divmod(i, cols) 
            # กำหนดให้คอลัมน์ใน grid ขยายเท่าๆ กัน
            products_grid_frame.grid_columnconfigure(col, weight=1, uniform="prod_card") 
            
            # --- สร้างการ์ดสินค้า 1 ใบ (โค้ดจาก create_product_card เดิม) ---
            # (ย้ายโค้ดสร้างการ์ดมาไว้ใน loop นี้)
            
            # แปลง dict เป็น Product object (เพื่อให้เรียกใช้ง่าย)
            product_object = Product.from_dict(product_dict) 
            
            # สร้าง Frame ของการ์ด
            product_card = ctk.CTkFrame(products_grid_frame, # ใส่การ์ดลงใน grid frame
                                        fg_color="#FFFFFF", 
                                        corner_radius=15, 
                                        border_width=1, 
                                        border_color="#FFEBEE")
            
            # โหลดและแสดงรูปภาพสินค้า
            # ใช้ main_app.get_product_image (สมมติว่าปรับ main.py แล้ว)
            product_card_image = self.main_app.get_product_image(product_object.image_url) 
            image_label_card = ctk.CTkLabel(product_card, text="", image=product_card_image, bg_color="transparent")
            image_label_card.pack(pady=(15, 10))

            # แสดงชื่อสินค้า
            name_label_card = ctk.CTkLabel(
                product_card, 
                text=product_object.name, 
                font=("IBM Plex Sans Thai", 16, "bold"), 
                text_color="#6D4C41"
            )
            name_label_card.pack(padx=10)
            
            # แสดงราคา
            price_label_card = ctk.CTkLabel(
                product_card, 
                text=product_object.format_price(), # ใช้ format_price() จาก Product object
                font=("IBM Plex Sans Thai", 14), 
                text_color="#FFB6C1"
            )
            price_label_card.pack(pady=5)
            
            # ปุ่ม "หยิบใส่ตะกร้า"
            add_cart_button_card = ctk.CTkButton(
                product_card, 
                text="หยิบใส่ตะกร้า", 
                height=35, corner_radius=10, 
                font=("IBM Plex Sans Thai", 14, "bold"), 
                fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                # ใช้ lambda capture (p=product_object) เพื่อส่ง object ที่ถูกต้องไป
                command=lambda p=product_object: self.add_to_cart(p) 
            )
            add_cart_button_card.pack(pady=10, padx=15, fill="x")
            # --- จบการสร้างการ์ดสินค้า 1 ใบ ---

            # วางการ์ดลงใน Grid ตามแถวและคอลัมน์ที่คำนวณไว้
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew") 
        # --- จบ Loop สร้างการ์ดสินค้า ---
        # --- จบส่วน สินค้าแนะนำ ---

        # --- 7. สร้างส่วน Footer ---
        footer_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง footer ใน main_content_frame แถว 3 (ใต้สินค้าแนะนำ)
        footer_frame.grid(row=3, column=0, sticky="ew", pady=20) 
        
        # ปุ่ม "เกี่ยวกับเรา"
        about_button = ctk.CTkButton(
            footer_frame,
            text="ℹ️ เกี่ยวกับเรา / ผู้พัฒนา",
            fg_color="transparent", text_color="#FFB6C1", hover_color="#FFE4E1",
            border_width=1, border_color="#FFB6C1",
            corner_radius=15, height=40,
            font=("IBM Plex Sans Thai", 14),
            command=lambda: self.main_app.navigate_to('AboutWindow') # กดแล้วไปหน้า About
        )
        about_button.pack(pady=10)
        # --- จบส่วน Footer ---

    # --- (ลบฟังก์ชัน create_header, create_banner, create_categories) ---
    # --- (ลบฟังก์ชัน create_product_display, create_product_card) ---

    def add_to_cart(self, product): # รับ product object เข้ามา
        """เพิ่มสินค้าลงตะกร้า แล้วแสดง popup"""
        # สั่งให้ Cart object (ที่ main_app ถืออยู่) เพิ่มสินค้านี้
        self.cart.add_item(product) 
        # แสดง popup ยืนยัน
        messagebox.showinfo("ตะกร้าสินค้า", f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!", parent=self)