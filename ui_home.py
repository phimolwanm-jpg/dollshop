import customtkinter as ctk
from tkinter import messagebox
from models import Product

class HomeWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.session = main_app.session
        self.cart = main_app.cart
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
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # --- 2. สร้างส่วนหัว (Header) ---
        header = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=1,
            border_color="#FFEBEE"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 5))
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

        # ---  เพิ่มการตรวจสอบ ---
        # --- 2.3 แสดงข้อความต้อนรับ (ถ้า Login แล้ว) ---
        if self.session.is_logged_in(): # เช็คว่า login หรือยัง
            user_full_name = self.session.current_user.full_name
            welcome_text = f"สวัสดี, {user_full_name}"
            welcome_label = ctk.CTkLabel(
                right_header_frame,
                text=welcome_text,
                font=("IBM Plex Sans Thai", 14),
                text_color="#6D4C41"
            )
            welcome_label.pack(side="left", padx=10)

            # --- 2.4 ตรวจสอบว่าเป็น Admin หรือไม่ (ถ้า Login แล้ว) ---
            is_current_user_admin = self.session.is_admin()
            if is_current_user_admin:
                # --- ถ้าเป็น Admin: สร้างปุ่มสำหรับ Admin ---
                admin_dashboard_btn = ctk.CTkButton(
                    right_header_frame,
                    text="📊 Dashboard",
                    fg_color="#4CAF50", hover_color="#66BB6A", text_color="white",
                    font=("IBM Plex Sans Thai", 14, "bold"),
                    corner_radius=15, height=35,
                    command=lambda: self.main_app.navigate_to('AdminDashboardWindow')
                )
                admin_dashboard_btn.pack(side="left", padx=5)

                admin_orders_btn = ctk.CTkButton(
                    right_header_frame,
                    text="📦 คำสั่งซื้อ",
                    fg_color="#2196F3", hover_color="#42A5F5", text_color="white",
                    font=("IBM Plex Sans Thai", 14, "bold"),
                    corner_radius=15, height=35,
                    command=lambda: self.main_app.navigate_to('AdminOrdersWindow')
                )
                admin_orders_btn.pack(side="left", padx=5)

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

            # --- 2.5 สร้างปุ่มสำหรับผู้ใช้ทุกคน (ถ้า Login แล้ว) ---
            profile_btn = ctk.CTkButton(
                right_header_frame,
                text="โปรไฟล์",
                fg_color="transparent", hover_color="#FFE4E1", text_color="#6D4C41",
                font=("IBM Plex Sans Thai", 14),
                command=lambda: self.main_app.navigate_to('ProfileWindow')
            )
            profile_btn.pack(side="left", padx=5)

            history_btn = ctk.CTkButton(
                right_header_frame,
                text="ประวัติการซื้อ",
                fg_color="transparent", hover_color="#FFE4E1", text_color="#6D4C41",
                font=("IBM Plex Sans Thai", 14),
                command=lambda: self.main_app.navigate_to('OrderHistoryWindow')
            )
            history_btn.pack(side="left", padx=5)

            cart_icon_image = self.main_app.load_image("cart_icon.png", size=(20, 20))
            cart_btn = ctk.CTkButton(
                right_header_frame,
                text="", image=cart_icon_image, width=30,
                fg_color="transparent", hover_color="#FFE4E1",
                command=lambda: self.main_app.navigate_to('CartWindow')
            )
            cart_btn.pack(side="left", padx=5)

            logout_btn = ctk.CTkButton(
                right_header_frame,
                text="ออกจากระบบ",
                width=100, corner_radius=15,
                font=("IBM Plex Sans Thai", 14, "bold"),
                fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                command=self.main_app.on_logout
            )
            logout_btn.pack(side="left", padx=10)
        # --- จบการตรวจสอบ if self.session.is_logged_in()---
        # --- (ถ้ายังไม่ได้ Login ส่วน Header ด้านขวาก็จะว่างไป) ---
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (เลื่อนได้) ---
        main_content_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        main_content_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=0)
        main_content_frame.grid_columnconfigure(0, weight=1)

        # --- 4. สร้างส่วน Banner ---
        banner_image = self.main_app.load_image("banner.png", size=(2100, 250)) # ใช้ขนาดเดิมไปก่อน
        banner_label = ctk.CTkLabel(
            main_content_frame,
            text="",
            image=banner_image,
            corner_radius=20
        )
        banner_label.grid(row=0, column=0, sticky="ew", pady=(10, 20))

        # --- 5. สร้างส่วน หมวดหมู่ ---
        category_section_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        category_section_frame.grid(row=1, column=0, sticky="ew", pady=20, padx=10)

        category_title_label = ctk.CTkLabel(
            category_section_frame,
            text="หมวดหมู่ตุ๊กตา",
            font=("IBM Plex Sans Thai", 20, "bold"),
            text_color="#6D4C41"
        )
        category_title_label.pack(anchor="w")

        category_buttons_frame = ctk.CTkFrame(category_section_frame, fg_color="transparent")
        category_buttons_frame.pack(fill="x", pady=10)

        categories_list = self.db.get_categories()
        category_icons = {
            'ตุ๊กตาหมี': '🧸', 'ตุ๊กตากระต่าย': '🐰', 'ตุ๊กตาแมว': '🐱',
            'ตุ๊กตาช้าง': '🐘', 'ตุ๊กตายูนิคอร์น': '🦄', 'ตุ๊กตาสุนัข': '🐶',
            'ตุ๊กตาไดโนเสาร์': '🦕'
        }

        for category_name in categories_list:
            icon = category_icons.get(category_name, '🎀')
            category_button = ctk.CTkButton(
                category_buttons_frame,
                text=f"{icon} {category_name}",
                height=40, corner_radius=20,
                font=("IBM Plex Sans Thai", 14, "bold"),
                fg_color="#FFFFFF", border_width=1, border_color="#FFEBEE",
                text_color="#6D4C41", hover_color="#FFE4E1",
                command=lambda c=category_name: self.main_app.navigate_to('ProductListWindow', category=c)
            )
            category_button.pack(side="left", padx=5)

        # --- 6. สร้างส่วน สินค้าแนะนำ ---
        recommended_section_container = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        recommended_section_container.grid(row=2, column=0, sticky="nsew", pady=10)

        recommended_title_label = ctk.CTkLabel(
            recommended_section_container,
            text="สินค้าแนะนำ ✨",
            font=("IBM Plex Sans Thai", 20, "bold"),
            text_color="#6D4C41"
        )
        recommended_title_label.pack(anchor="w", padx=10)

        products_grid_frame = ctk.CTkFrame(recommended_section_container, fg_color="transparent")
        products_grid_frame.pack(fill="both", expand=True, pady=10)

        recommended_products_data = self.db.get_all_products(limit=8)
        cols = 4

        for i, product_dict in enumerate(recommended_products_data):
            row, col = divmod(i, cols)
            products_grid_frame.grid_columnconfigure(col, weight=1, uniform="prod_card")

            product_object = Product.from_dict(product_dict)
            product_card = ctk.CTkFrame(products_grid_frame,
                                        fg_color="#FFFFFF", corner_radius=15,
                                        border_width=1, border_color="#FFEBEE")

            product_card_image = self.main_app.get_product_image(product_object.image_url)
            image_label_card = ctk.CTkLabel(product_card, text="", image=product_card_image, bg_color="transparent")
            image_label_card.pack(pady=(15, 10))

            name_label_card = ctk.CTkLabel(
                product_card, text=product_object.name,
                font=("IBM Plex Sans Thai", 16, "bold"), text_color="#6D4C41"
            )
            name_label_card.pack(padx=10)

            price_label_card = ctk.CTkLabel(
                product_card, text=product_object.format_price(),
                font=("IBM Plex Sans Thai", 14), text_color="#FFB6C1"
            )
            price_label_card.pack(pady=5)

            add_cart_button_card = ctk.CTkButton(
                product_card, text="หยิบใส่ตะกร้า",
                height=35, corner_radius=10,
                font=("IBM Plex Sans Thai", 14, "bold"),
                fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                command=lambda p=product_object: self.add_to_cart(p)
            )
            add_cart_button_card.pack(pady=10, padx=15, fill="x")

            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

        # --- 7. สร้างส่วน Footer ---
        footer_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        footer_frame.grid(row=3, column=0, sticky="ew", pady=20)

        about_button = ctk.CTkButton(
            footer_frame, text="ℹ️ เกี่ยวกับเรา / ผู้พัฒนา",
            fg_color="transparent", text_color="#FFB6C1", hover_color="#FFE4E1",
            border_width=1, border_color="#FFB6C1", corner_radius=15, height=40,
            font=("IBM Plex Sans Thai", 14),
            command=lambda: self.main_app.navigate_to('AboutWindow')
        )
        about_button.pack(pady=10)

    def add_to_cart(self, product):
        """เพิ่มสินค้าลงตะกร้า แล้วแสดง popup"""
        # --- เพิ่มการตรวจสอบก่อน add_to_cart (ถ้ายังไม่ login) ---
        if not self.session.is_logged_in():
             messagebox.showwarning("กรุณาเข้าสู่ระบบ", "คุณต้องเข้าสู่ระบบก่อนเพิ่มสินค้าลงตะกร้า", parent=self)
             # อาจจะพาไปหน้า login เลยก็ได้
             # self.main_app.navigate_to("LoginWindow")
             return # หยุดทำงานถ้ายังไม่ login
        # --- สิ้นสุดการตรวจสอบ---

        self.cart.add_item(product)
        messagebox.showinfo("ตะกร้าสินค้า", f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!", parent=self)