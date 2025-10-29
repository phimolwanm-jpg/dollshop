import customtkinter as ctk
from models import Product 
from tkinter import messagebox 

class ProductListWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        self.db = main_app.db
        self.cart = main_app.cart
        self.category_filter = None 
        self.current_product_list = [] 
        self.search_term_var = ctk.StringVar() 
        self.sort_option_var = ctk.StringVar(value="ล่าสุด") 

        self.setup_ui() 

    # --- (EDITED) แก้ไข on_show ให้รับ search_term ได้ ---
    def on_show(self, category=None, search_term=None):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: รับ category, ล้าง UI เก่า, สร้าง UI ใหม่, โหลดข้อมูล
        """
        # 1. รับค่า category ที่ส่งมา (ถ้ามี)
        self.category_filter = category 
        
        # 2. ล้างค่าในช่องค้นหา (เป็นค่าว่าง)
        self.search_term_var.set("") 
        
        # --- (NEW) 2.5 ตรวจสอบว่ามี search_term ส่งมาหรือไม่ ---
        if search_term:
            print(f"ProductList received search_term: {search_term}")
            self.category_filter = None # บังคับให้เป็น None (ค้นหาโดยรวม)
            self.search_term_var.set(search_term) # ตั้งค่าในช่องค้นหาของหน้านี้
        # --- (จบส่วน NEW) ---
        
        # 3. ลบ widget เก่าทั้งหมดทิ้ง
        for widget in self.winfo_children():
            widget.destroy()
        
        # 4. สร้างโครงสร้าง UI ใหม่ทั้งหมด
        self.setup_ui() 
        
        # 5. สั่งโหลดข้อมูลสินค้า (จะใช้ค่า search_term_var ที่ตั้งไว้)
        self.load_products() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้าแสดงรายการสินค้า"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        self.grid_rowconfigure(1, weight=1) 
        self.grid_columnconfigure(0, weight=1) 

        # --- 2. สร้างส่วนหัว (Header), Search, และ Filter ---
        header_frame = ctk.CTkFrame(self, 
                                    fg_color="#FFFFFF", 
                                    corner_radius=0, 
                                    height=90, 
                                    border_width=1, 
                                    border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        header_frame.grid_columnconfigure(1, weight=1) 

        # --- 2.1 Frame ด้านซ้าย (ปุ่มกลับ และ ชื่อหมวดหมู่) ---
        left_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header_frame.pack(side="left", padx=20, pady=20)
        
        # ปุ่มกลับ "<"
        back_button = ctk.CTkButton(
            left_header_frame,
            text="<",
            width=40, height=40, corner_radius=10, 
            fg_color="#FFB6C1", hover_color="#FFC0CB", 
            font=ctk.CTkFont(size=18, weight="bold"),
            command=lambda: self.main_app.navigate_to('HomeWindow') 
        )
        back_button.pack(side="left")
        
        # --- (EDITED) Label แสดงชื่อหมวดหมู่ (หรือ "สินค้าทั้งหมด") ---
        # ตรวจสอบ self.category_filter ที่ได้จาก on_show
        if self.category_filter:
            title_display_text = f"🛍️ {self.category_filter}" 
        # (NEW) ตรวจสอบว่ากำลังค้นหาหรือไม่ (โดยดูจาก search_term_var)
        elif self.search_term_var.get(): 
            title_display_text = f"🔍 ผลการค้นหา: '{self.search_term_var.get()}'"
        else:
            title_display_text = "🛍️ สินค้าทั้งหมด"
            
        category_title_label = ctk.CTkLabel(
            left_header_frame,
            text=title_display_text,
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#FFB6C1"
        )
        category_title_label.pack(side="left", padx=15)

        # --- 2.2 Frame ด้านขวา (ช่องค้นหา และ เมนูจัดเรียง) ---
        right_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        right_header_frame.pack(side="right", padx=20, pady=20)

        # ช่องค้นหา
        search_entry = ctk.CTkEntry(
            right_header_frame,
            textvariable=self.search_term_var, # ผูกกับตัวแปร search_term_var
            placeholder_text="🔍 ค้นหาชื่อสินค้า...",
            width=250, height=40, corner_radius=15,
            border_width=1, border_color="#FFEBEE",
            fg_color="#FFF0F5", 
            font=ctk.CTkFont(size=14)
        )
        search_entry.pack(side="left", padx=5)
        search_entry.bind("<Return>", lambda event: self.load_products()) 

        # เมนูตัวเลือกสำหรับจัดเรียง (Dropdown)
        sort_option_menu = ctk.CTkOptionMenu(
            right_header_frame,
            variable=self.sort_option_var, 
            values=["ล่าสุด", "ราคา: ต่ำ-สูง", "ราคา: สูง-ต่ำ", "ชื่อ: A-Z"], 
            command=self.sort_products, 
            width=150, height=40, corner_radius=15,
            fg_color="#FFB6C1", 
            button_color="#FF6B9D", 
            button_hover_color="#FF8FB3",
            font=ctk.CTkFont(size=14)
        )
        sort_option_menu.pack(side="left", padx=5)
        # --- จบส่วน Header ---
        
        # --- ( ... โค้ดส่วนที่เหลือของ setup_ui, load_products, 
        #           sort_products, display_products, add_to_cart 
        #           เหมือนเดิมทั้งหมด ... ) ---
        
        # --- 3. สร้าง Frame หลักสำหรับแสดงผล Grid สินค้า ---
        product_grid_container = ctk.CTkFrame(self, fg_color="transparent")
        product_grid_container.grid(row=1, column=0, sticky="nsew") 
        product_grid_container.grid_rowconfigure(1, weight=1) 
        product_grid_container.grid_columnconfigure(0, weight=1) 
        
        # --- 3.1 Label แสดงจำนวนผลลัพธ์ (จะ update ทีหลัง) ---
        self.results_count_label = ctk.CTkLabel(
            product_grid_container,
            text="กำลังโหลด...", 
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        self.results_count_label.grid(row=0, column=0, sticky="w", padx=30, pady=10) 
        
        # --- 3.2 สร้าง Frame ที่เลื่อนได้สำหรับวาง Grid สินค้า ---
        self.products_frame_scrollable = ctk.CTkScrollableFrame(
            product_grid_container, 
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        self.products_frame_scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=5) 
        for i in range(4):
            self.products_frame_scrollable.grid_columnconfigure(i, weight=1, uniform="col") 

    def load_products(self):
        """โหลดสินค้าจากฐานข้อมูลตาม category และ search term"""
        # (ฟังก์ชันนี้ไม่ต้องแก้ เพราะมันอ่านค่าจาก self.search_term_var และ
        # self.category_filter ซึ่งถูกตั้งค่าไว้ใน on_show แล้ว)
        search_keyword = self.search_term_var.get().strip().lower() 
        
        product_data_from_db = self.db.get_all_products(
            category=self.category_filter, 
            search_term=search_keyword
        )
        self.current_product_list = product_data_from_db 
        
        current_sort_option = self.sort_option_var.get()
        self.sort_products(current_sort_option) 

    def sort_products(self, sort_option):
        """จัดเรียงรายการสินค้า (self.current_product_list)"""
        # (ฟังก์ชันนี้ไม่ต้องแก้)
        product_object_list = []
        for product_dict in self.current_product_list:
            product_obj = Product.from_dict(product_dict)
            product_object_list.append(product_obj)
        
        if sort_option == "ล่าสุด":
            product_object_list.sort(key=lambda product: product.created_at or '', reverse=True) 
        elif sort_option == "ราคา: ต่ำ-สูง":
            product_object_list.sort(key=lambda product: product.price) 
        elif sort_option == "ราคา: สูง-ต่ำ":
            product_object_list.sort(key=lambda product: product.price, reverse=True) 
        elif sort_option == "ชื่อ: A-Z":
            product_object_list.sort(key=lambda product: product.name) 
        
        self.display_products(product_object_list) 

    def display_products(self, sorted_product_objects):
        """แสดงผลสินค้า (List ของ Product Object) ลงบน Grid"""
        # (ฟังก์ชันนี้ไม่ต้องแก้)
        for widget in self.products_frame_scrollable.winfo_children():
            widget.destroy()

        number_of_products = len(sorted_product_objects)
        self.results_count_label.configure(text=f"📦 พบ {number_of_products} รายการ")
        
        if not sorted_product_objects:
            empty_frame = ctk.CTkFrame(self.products_frame_scrollable, 
                                       fg_color="#FFFFFF", 
                                       corner_radius=20, 
                                       border_width=2, 
                                       border_color="#FFEBEE")
            empty_frame.grid(row=0, column=0, columnspan=4, pady=50, padx=20, sticky="ew") 
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="😢 ไม่พบสินค้าที่ตรงกับเงื่อนไข",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#FFB6C1"
            )
            empty_label.pack(pady=40)
            return 

        cols = 4 
        for i, product_object in enumerate(sorted_product_objects):
            row, col = divmod(i, cols) 
            
            product_card = ctk.CTkFrame(self.products_frame_scrollable, 
                                        fg_color="#FFFFFF", 
                                        corner_radius=15, 
                                        border_width=2, 
                                        border_color="#FFEBEE")
            
            product_card_image = self.main_app.get_product_image(product_object.image_url) 
            image_label_card = ctk.CTkLabel(product_card, text="", image=product_card_image, bg_color="transparent")
            image_label_card.pack(pady=(15, 10))

            name_label_card = ctk.CTkLabel(
                product_card,
                text=product_object.name, 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#6D4C41"
            )
            name_label_card.pack(padx=10, fill="x") 
            
            stock_display_text, stock_text_color = product_object.get_stock_status() 
            stock_status_frame = ctk.CTkFrame(product_card, fg_color="#FFF0F5", corner_radius=8)
            stock_status_frame.pack(pady=5)
            stock_status_label = ctk.CTkLabel(
                stock_status_frame,
                text=stock_display_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=stock_text_color 
            )
            stock_status_label.pack(padx=10, pady=3)
            
            price_label_card = ctk.CTkLabel(
                product_card,
                text=product_object.format_price(), 
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FF6B9D"
            )
            price_label_card.pack(pady=5)
            
            add_cart_button_card = ctk.CTkButton(
                product_card,
                text="🛒 หยิบใส่ตะกร้า",
                height=40, corner_radius=10,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                state="normal" if product_object.is_available() else "disabled", 
                command=lambda p=product_object: self.add_to_cart(p) 
            )
            add_cart_button_card.pack(pady=10, padx=15, fill="x")

            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew") 

    def add_to_cart(self, product): 
        """เพิ่มสินค้าลงตะกร้า แล้วแสดง popup"""
        # (ฟังก์ชันนี้ไม่ต้องแก้)
        
        # --- (NEW) ตรวจสอบการ Login ก่อนเพิ่ม ---
        # (โค้ดใน ui_home.py มีส่วนนี้ แต่ใน ui_product_list.py ไม่มี
        # ผมขอเพิ่มให้ เพื่อความปลอดภัย)
        if not self.main_app.session.is_logged_in():
             messagebox.showwarning("กรุณาเข้าสู่ระบบ", "คุณต้องเข้าสู่ระบบก่อนเพิ่มสินค้าลงตะกร้า", parent=self)
             return
        # --- (จบส่วน NEW) ---
        
        self.cart.add_item(product) 
        messagebox.showinfo("ตะกร้าสินค้า", f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!", parent=self)