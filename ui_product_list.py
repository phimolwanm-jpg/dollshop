import customtkinter as ctk
from models import Product 
from tkinter import messagebox 

class ProductListWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.db = main_app.db
        self.cart = main_app.cart
        # --- ตัวแปรสำหรับเก็บสถานะของหน้านี้ ---
        self.category_filter = None # หมวดหมู่ที่กำลังแสดง (None = ทั้งหมด)
        self.current_product_list = [] # List ของ product (dict) ที่แสดงอยู่ตอนนี้
        # ตัวแปร StringVar ของ tkinter สำหรับผูกกับช่องค้นหา
        self.search_term_var = ctk.StringVar() 
        # ตัวแปร StringVar ของ tkinter สำหรับผูกกับเมนูจัดเรียง
        self.sort_option_var = ctk.StringVar(value="ล่าสุด") # ค่าเริ่มต้น

        # สร้างหน้าจอ UI ทันที (แต่ยังไม่มีข้อมูล)
        self.setup_ui() 
        # โหลดข้อมูลสินค้าครั้งแรก (จะถูกเรียกอีกครั้งใน on_show)

    def on_show(self, category=None):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: รับ category, ล้าง UI เก่า, สร้าง UI ใหม่, โหลดข้อมูล
        """
        # 1. รับค่า category ที่ส่งมา (ถ้ามี)
        self.category_filter = category 
        # 2. ล้างค่าในช่องค้นหา
        self.search_term_var.set("") 
        
        # 3. ลบ widget เก่าทั้งหมดทิ้ง
        for widget in self.winfo_children():
            widget.destroy()
        
        # 4. สร้างโครงสร้าง UI ใหม่ทั้งหมด
        self.setup_ui() 
        # 5. สั่งโหลดข้อมูลสินค้า (ซึ่งจะไปเรียก display_products ต่อ)
        self.load_products() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้าแสดงรายการสินค้า"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # ให้แถวที่ 1 (container) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1) 
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 

        # --- 2. สร้างส่วนหัว (Header), Search, และ Filter ---
        header_frame = ctk.CTkFrame(self, # ใส่ header ใน ProductListWindow (self)
                                    fg_color="#FFFFFF", 
                                    corner_radius=0, 
                                    height=90, # กำหนดความสูง header
                                    border_width=1, 
                                    border_color="#FFEBEE")
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันส่วน search/sort ไปขวา)
        header_frame.grid_columnconfigure(1, weight=1) 

        # --- 2.1 Frame ด้านซ้าย (ปุ่มกลับ และ ชื่อหมวดหมู่) ---
        left_header_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        left_header_frame.pack(side="left", padx=20, pady=20)
        
        # ปุ่มกลับ "<"
        back_button = ctk.CTkButton(
            left_header_frame,
            text="<",
            width=40, height=40, corner_radius=10, # ปุ่มสี่เหลี่ยมเล็กๆ
            fg_color="#FFB6C1", hover_color="#FFC0CB", # สีชมพู
            font=ctk.CTkFont(size=18, weight="bold"),
            command=lambda: self.main_app.navigate_to('HomeWindow') # กดแล้วกลับหน้า Home
        )
        back_button.pack(side="left")
        
        # Label แสดงชื่อหมวดหมู่ (หรือ "สินค้าทั้งหมด")
        # ตรวจสอบ self.category_filter ที่ได้จาก on_show
        if self.category_filter:
            title_display_text = f"🛍️ {self.category_filter}" 
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
            fg_color="#FFF0F5", # สีพื้นหลังช่องค้นหา
            font=ctk.CTkFont(size=14)
        )
        search_entry.pack(side="left", padx=5)
        # ผูก event: ถ้ากด Enter ในช่องค้นหา ให้เรียก load_products()
        search_entry.bind("<Return>", lambda event: self.load_products()) 

        # เมนูตัวเลือกสำหรับจัดเรียง (Dropdown)
        sort_option_menu = ctk.CTkOptionMenu(
            right_header_frame,
            variable=self.sort_option_var, # ผูกกับตัวแปร sort_option_var
            values=["ล่าสุด", "ราคา: ต่ำ-สูง", "ราคา: สูง-ต่ำ", "ชื่อ: A-Z"], # ตัวเลือก
            command=self.sort_products, # เมื่อเลือก ให้เรียก sort_products
            width=150, height=40, corner_radius=15,
            fg_color="#FFB6C1", # สีพื้นหลังเมนู
            button_color="#FF6B9D", # สีปุ่ม dropdown
            button_hover_color="#FF8FB3",
            font=ctk.CTkFont(size=14)
        )
        sort_option_menu.pack(side="left", padx=5)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับแสดงผล Grid สินค้า ---
        product_grid_container = ctk.CTkFrame(self, fg_color="transparent")
        # วาง container ในแถว 1 (ใต้ header) ยืดเต็มพื้นที่
        product_grid_container.grid(row=1, column=0, sticky="nsew") 
        # ให้แถวที่ 1 (products_frame_scrollable) ขยายเต็มความสูง
        product_grid_container.grid_rowconfigure(1, weight=1) 
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        product_grid_container.grid_columnconfigure(0, weight=1) 
        
        # --- 3.1 Label แสดงจำนวนผลลัพธ์ (จะ update ทีหลัง) ---
        self.results_count_label = ctk.CTkLabel(
            product_grid_container,
            text="กำลังโหลด...", # ข้อความเริ่มต้น
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        # วาง label ชิดซ้ายบน
        self.results_count_label.grid(row=0, column=0, sticky="w", padx=30, pady=10) 
        
        # --- 3.2 สร้าง Frame ที่เลื่อนได้สำหรับวาง Grid สินค้า ---
        self.products_frame_scrollable = ctk.CTkScrollableFrame(
            product_grid_container, # ใส่ใน container
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        # วาง frame ที่เลื่อนได้ ในแถว 1 ยืดเต็มพื้นที่
        self.products_frame_scrollable.grid(row=1, column=0, sticky="nsew", padx=20, pady=5) 
        # กำหนดให้มี 4 คอลัมน์ และให้กว้างเท่ากัน (uniform="col")
        for i in range(4):
            self.products_frame_scrollable.grid_columnconfigure(i, weight=1, uniform="col") 
        # --- จบส่วนสร้าง Grid ---
        # --- จบ setup_ui ---

    def load_products(self):
        """โหลดสินค้าจากฐานข้อมูลตาม category และ search term"""
        # 1. อ่านคำค้นหาจากตัวแปร StringVar (แปลงเป็นตัวเล็ก ตัดช่องว่าง)
        search_keyword = self.search_term_var.get().strip().lower() 
        
        # 2. เรียก DB เพื่อดึงข้อมูล (ส่ง category และ keyword ไปกรอง)
        # ผลลัพธ์ที่ได้จะเป็น List ของ Dictionary
        product_data_from_db = self.db.get_all_products(
            category=self.category_filter, 
            search_term=search_keyword
        )
        # 3. เก็บข้อมูลดิบนี้ไว้ในตัวแปรของคลาส
        self.current_product_list = product_data_from_db 
        
        # 4. ส่งต่อไปให้ฟังก์ชัน sort_products (พร้อม option ที่เลือกไว้)
        current_sort_option = self.sort_option_var.get()
        self.sort_products(current_sort_option) 

    def sort_products(self, sort_option):
        """จัดเรียงรายการสินค้า (self.current_product_list)"""
        
        # --- 1. แปลง List ของ Dictionary เป็น List ของ Product Object ---
        # (เพื่อให้ sort โดยใช้ attribute ของ object ได้ง่าย)
        product_object_list = []
        for product_dict in self.current_product_list:
            product_obj = Product.from_dict(product_dict)
            product_object_list.append(product_obj)
        
        # --- 2. ทำการจัดเรียง List ของ Object ตามเงื่อนไข ---
        if sort_option == "ล่าสุด":
            # เรียงตาม created_at (ใหม่ -> เก่า)
            # lambda x: x.created_at คือ บอกให้ sort ใช้ค่า created_at เป็น key
            # or '' เพื่อป้องกัน error ถ้า created_at เป็น None
            # reverse=True คือเรียงจากมากไปน้อย (วันที่ใหม่กว่าค่ามากกว่า)
            product_object_list.sort(key=lambda product: product.created_at or '', reverse=True) 
        elif sort_option == "ราคา: ต่ำ-สูง":
            # เรียงตาม price (น้อย -> มาก)
            product_object_list.sort(key=lambda product: product.price) 
        elif sort_option == "ราคา: สูง-ต่ำ":
            # เรียงตาม price (มาก -> น้อย)
            product_object_list.sort(key=lambda product: product.price, reverse=True) 
        elif sort_option == "ชื่อ: A-Z":
            # เรียงตาม name (A -> Z)
            product_object_list.sort(key=lambda product: product.name) 
        
        # --- 3. (Optional) แปลง List ของ Object กลับเป็น List ของ Dictionary ---
        
        # --- ใช้ List ของ Object ไปแสดงผลเลย ---
        # ส่ง List ของ Product Object ที่เรียงแล้วไปให้ display_products
        self.display_products(product_object_list) 

    def display_products(self, sorted_product_objects):
        """แสดงผลสินค้า (List ของ Product Object) ลงบน Grid"""
        
        # --- 1. ล้างการ์ดสินค้าเก่าใน Grid ทิ้ง ---
        # self.products_frame_scrollable คือ frame ที่เลื่อนได้
        for widget in self.products_frame_scrollable.winfo_children():
            widget.destroy()

        # --- 2. อัปเดต Label แสดงจำนวนผลลัพธ์ ---
        number_of_products = len(sorted_product_objects)
        self.results_count_label.configure(text=f"📦 พบ {number_of_products} รายการ")
        
        # --- 3. ตรวจสอบว่ามีสินค้าแสดงหรือไม่ ---
        if not sorted_product_objects:
            # --- ถ้าไม่มี: แสดงข้อความแจ้ง ---
            empty_frame = ctk.CTkFrame(self.products_frame_scrollable, # ใส่ใน frame ที่เลื่อนได้
                                       fg_color="#FFFFFF", 
                                       corner_radius=20, 
                                       border_width=2, 
                                       border_color="#FFEBEE")
            # columnspan=4 ให้ frame นี้กินพื้นที่ 4 คอลัมน์
            empty_frame.grid(row=0, column=0, columnspan=4, pady=50, padx=20, sticky="ew") 
            
            empty_label = ctk.CTkLabel(
                empty_frame,
                text="😢 ไม่พบสินค้าที่ตรงกับเงื่อนไข",
                font=ctk.CTkFont(size=18, weight="bold"),
                text_color="#FFB6C1"
            )
            empty_label.pack(pady=40)
            return # หยุดทำงาน ไม่ต้องสร้างการ์ด

        # --- 4. ถ้ามีสินค้า: วนลูปสร้างการ์ดสินค้าและวางลง Grid ---
        cols = 4 # กำหนด 4 คอลัมน์
        for i, product_object in enumerate(sorted_product_objects):
            # คำนวณแถว (row) และคอลัมน์ (col)
            row, col = divmod(i, cols) 
            
            # --- สร้างการ์ดสินค้า 1 ใบ (โค้ดจาก create_product_card เดิม) --- 
            # สร้าง Frame ของการ์ด
            product_card = ctk.CTkFrame(self.products_frame_scrollable, # ใส่การ์ดลงใน frame ที่เลื่อนได้
                                        fg_color="#FFFFFF", 
                                        corner_radius=15, 
                                        border_width=2, 
                                        border_color="#FFEBEE")
            
            # โหลดและแสดงรูปภาพสินค้า
            # ใช้ main_app.get_product_image 
            product_card_image = self.main_app.get_product_image(product_object.image_url) 
            image_label_card = ctk.CTkLabel(product_card, text="", image=product_card_image, bg_color="transparent")
            image_label_card.pack(pady=(15, 10))

            # แสดงชื่อสินค้า
            name_label_card = ctk.CTkLabel(
                product_card,
                text=product_object.name, # ใช้ .name จาก object
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#6D4C41"
            )
            name_label_card.pack(padx=10, fill="x") # fill="x" ให้ข้อความเต็มบรรทัด (ถ้าชื่อยาว)
            
            # แสดงสถานะสต็อก
            # เรียก get_stock_status() จาก Product object
            stock_display_text, stock_text_color = product_object.get_stock_status() 
            # สร้าง Frame เล็กๆ สำหรับใส่สถานะ
            stock_status_frame = ctk.CTkFrame(product_card, fg_color="#FFF0F5", corner_radius=8)
            stock_status_frame.pack(pady=5)
            # Label แสดงสถานะ (ใช้สีที่ได้จาก get_stock_status)
            stock_status_label = ctk.CTkLabel(
                stock_status_frame,
                text=stock_display_text,
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color=stock_text_color 
            )
            stock_status_label.pack(padx=10, pady=3)
            
            # แสดงราคา
            price_label_card = ctk.CTkLabel(
                product_card,
                text=product_object.format_price(), # ใช้ format_price() จาก object
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FF6B9D"
            )
            price_label_card.pack(pady=5)
            
            # ปุ่ม "หยิบใส่ตะกร้า"
            add_cart_button_card = ctk.CTkButton(
                product_card,
                text="🛒 หยิบใส่ตะกร้า",
                height=40, corner_radius=10,
                font=ctk.CTkFont(size=14, weight="bold"),
                fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                # ตั้งค่า state (normal/disabled) โดยเรียก is_available() จาก object
                state="normal" if product_object.is_available() else "disabled", 
                # ใช้ lambda capture (p=product_object)
                command=lambda p=product_object: self.add_to_cart(p) 
            )
            add_cart_button_card.pack(pady=10, padx=15, fill="x")
            # --- จบการสร้างการ์ดสินค้า 1 ใบ ---

            # วางการ์ดลงใน Grid ตามแถวและคอลัมน์ที่คำนวณไว้
            product_card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew") 
        # --- จบ Loop สร้างการ์ด ---

    def add_to_cart(self, product): # รับ Product object เข้ามา
        """เพิ่มสินค้าลงตะกร้า แล้วแสดง popup"""
        # สั่งให้ Cart object (ที่ main_app ถืออยู่) เพิ่มสินค้านี้
        self.cart.add_item(product) 
        # แสดง popup ยืนยัน
        messagebox.showinfo("ตะกร้าสินค้า", f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!", parent=self)