import customtkinter as ctk
from models import Product 
from tkinter import messagebox 

class ProductListWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.cart = main_app.cart
        
        # ตัวแปรเก็บค่าต่างๆ
        self.category_filter = None
        self.product_list = []
        self.search_text = ctk.StringVar()
        self.sort_by = ctk.StringVar(value="ล่าสุด")

        self.create_ui()

    def on_show(self, category=None, search_term=None):
        """เปิดหน้านี้ - รับหมวดหมู่หรือคำค้นหา"""
        # เก็บค่าหมวดหมู่
        self.category_filter = category
        
        # ล้างช่องค้นหา
        self.search_text.set("")
        
        # ถ้ามีคำค้นหาส่งมา
        if search_term:
            self.category_filter = None
            self.search_text.set(search_term)
        
        # ล้างหน้าจอเก่า
        for widget in self.winfo_children():
            widget.destroy()
        
        # สร้างหน้าจอใหม่
        self.create_ui()
        
        # โหลดสินค้า
        self.load_products()

    def create_ui(self):
        """สร้างหน้าจอแสดงสินค้า"""
        # ตั้งค่าให้ขยายเต็มหน้าจอ
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        # สร้างส่วนบนสุด
        self.create_header()
        
        # สร้างส่วนแสดงสินค้า
        self.create_product_area()

    def create_header(self):
        """สร้างส่วนหัวด้านบน"""
        # กรอบหัว
        header = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, 
                             height=90, border_width=1, border_color="#FFEBEE")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(1, weight=1)

        # ส่วนซ้าย - ปุ่มกลับและชื่อ
        left_side = ctk.CTkFrame(header, fg_color="transparent")
        left_side.pack(side="left", padx=20, pady=20)
        
        # ปุ่มกลับ
        back_btn = ctk.CTkButton(left_side, text="<", width=40, height=40,
                                corner_radius=10, fg_color="#FFB6C1",
                                hover_color="#FFC0CB",
                                font=ctk.CTkFont(size=18, weight="bold"),
                                command=self.go_back)
        back_btn.pack(side="left")
        
        # แสดงชื่อหมวดหมู่หรือคำค้นหา
        title_text = self.get_title_text()
        title_label = ctk.CTkLabel(left_side, text=title_text,
                                   font=ctk.CTkFont(size=26, weight="bold"),
                                   text_color="#FFB6C1")
        title_label.pack(side="left", padx=15)

        # ส่วนขวา - ช่องค้นหาและเรียงลำดับ
        right_side = ctk.CTkFrame(header, fg_color="transparent")
        right_side.pack(side="right", padx=20, pady=20)

        # ช่องค้นหา
        search_box = ctk.CTkEntry(right_side, textvariable=self.search_text,
                                 placeholder_text="🔍 ค้นหาชื่อสินค้า...",
                                 width=250, height=40, corner_radius=15,
                                 border_width=1, border_color="#FFEBEE",
                                 fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        search_box.pack(side="left", padx=5)
        search_box.bind("<Return>", lambda e: self.load_products())

        # เมนูเรียงลำดับ
        sort_menu = ctk.CTkOptionMenu(right_side, variable=self.sort_by,
                                      values=["ล่าสุด", "ราคา: ต่ำ-สูง", 
                                             "ราคา: สูง-ต่ำ", "ชื่อ: A-Z"],
                                      command=self.sort_and_show,
                                      width=150, height=40, corner_radius=15,
                                      fg_color="#FFB6C1", button_color="#FF6B9D",
                                      button_hover_color="#FF8FB3",
                                      font=ctk.CTkFont(size=14))
        sort_menu.pack(side="left", padx=5)

    def create_product_area(self):
        """สร้างพื้นที่แสดงสินค้า"""
        # กรอบหลัก
        container = ctk.CTkFrame(self, fg_color="transparent")
        container.grid(row=1, column=0, sticky="nsew")
        container.grid_rowconfigure(1, weight=1)
        container.grid_columnconfigure(0, weight=1)
        
        # แสดงจำนวนสินค้า
        self.count_label = ctk.CTkLabel(container, text="กำลังโหลด...",
                                       font=ctk.CTkFont(size=14),
                                       text_color="#6D4C41")
        self.count_label.grid(row=0, column=0, sticky="w", padx=30, pady=10)
        
        # พื้นที่เลื่อนได้สำหรับแสดงสินค้า
        self.product_scroll = ctk.CTkScrollableFrame(container,
                                                    fg_color="transparent",
                                                    scrollbar_button_color="#FFB6C1")
        self.product_scroll.grid(row=1, column=0, sticky="nsew", padx=20, pady=5)
        
        # ตั้งค่าคอลัมน์ 4 คอลัมน์
        for i in range(4):
            self.product_scroll.grid_columnconfigure(i, weight=1, uniform="col")

    def get_title_text(self):
        """หาข้อความที่จะแสดงในหัวเรื่อง"""
        if self.category_filter:
            return f"🛍️ {self.category_filter}"
        elif self.search_text.get():
            return f"🔍 ผลการค้นหา: '{self.search_text.get()}'"
        else:
            return "🛍️ สินค้าทั้งหมด"

    def go_back(self):
        """กลับไปหน้าหลัก"""
        self.main_app.navigate_to('HomeWindow')

    def load_products(self):
        """โหลดสินค้าจากฐานข้อมูล"""
        # เอาคำค้นหา
        keyword = self.search_text.get().strip().lower()
        
        # ดึงข้อมูลจากฐานข้อมูล
        products = self.db.get_all_products(category=self.category_filter,
                                           search_term=keyword)
        self.product_list = products
        
        # เรียงลำดับและแสดงผล
        sort_option = self.sort_by.get()
        self.sort_and_show(sort_option)

    def sort_and_show(self, sort_option):
        """เรียงลำดับสินค้าและแสดงผล"""
        # แปลง dict เป็น Product object
        products = []
        for p_dict in self.product_list:
            product = Product.from_dict(p_dict)
            products.append(product)
        
        # เรียงตามที่เลือก
        if sort_option == "ล่าสุด":
            products.sort(key=lambda p: p.created_at or '', reverse=True)
        elif sort_option == "ราคา: ต่ำ-สูง":
            products.sort(key=lambda p: p.price)
        elif sort_option == "ราคา: สูง-ต่ำ":
            products.sort(key=lambda p: p.price, reverse=True)
        elif sort_option == "ชื่อ: A-Z":
            products.sort(key=lambda p: p.name)
        
        # แสดงสินค้า
        self.show_products(products)

    def show_products(self, products):
        """แสดงสินค้าบนหน้าจอ"""
        # ลบของเก่า
        for widget in self.product_scroll.winfo_children():
            widget.destroy()

        # แสดงจำนวน
        count = len(products)
        self.count_label.configure(text=f"📦 พบ {count} รายการ")
        
        # ถ้าไม่มีสินค้า
        if not products:
            self.show_no_products()
            return

        # แสดงสินค้าทีละชิ้น
        for i, product in enumerate(products):
            row = i // 4  # หาแถว
            col = i % 4   # หาคอลัมน์
            self.create_product_card(product, row, col)

    def show_no_products(self):
        """แสดงข้อความเมื่อไม่มีสินค้า"""
        empty_box = ctk.CTkFrame(self.product_scroll, fg_color="#FFFFFF",
                                corner_radius=20, border_width=2,
                                border_color="#FFEBEE")
        empty_box.grid(row=0, column=0, columnspan=4, pady=50, padx=20, sticky="ew")
        
        empty_text = ctk.CTkLabel(empty_box,
                                 text="😢 ไม่พบสินค้าที่ตรงกับเงื่อนไข",
                                 font=ctk.CTkFont(size=18, weight="bold"),
                                 text_color="#FFB6C1")
        empty_text.pack(pady=40)

    def create_product_card(self, product, row, col):
        """สร้างการ์ดสินค้า 1 ชิ้น"""
        # กรอบการ์ด
        card = ctk.CTkFrame(self.product_scroll, fg_color="#FFFFFF",
                           corner_radius=15, border_width=2,
                           border_color="#FFEBEE")
        
        # รูปภาพ
        img = self.main_app.get_product_image(product.image_url)
        img_label = ctk.CTkLabel(card, text="", image=img, bg_color="transparent")
        img_label.pack(pady=(15, 10))

        # ชื่อสินค้า
        name_label = ctk.CTkLabel(card, text=product.name,
                                 font=ctk.CTkFont(size=16, weight="bold"),
                                 text_color="#6D4C41")
        name_label.pack(padx=10, fill="x")
        
        # สถานะสต็อก
        stock_text, stock_color = product.get_stock_status()
        stock_box = ctk.CTkFrame(card, fg_color="#FFF0F5", corner_radius=8)
        stock_box.pack(pady=5)
        stock_label = ctk.CTkLabel(stock_box, text=stock_text,
                                   font=ctk.CTkFont(size=12, weight="bold"),
                                   text_color=stock_color)
        stock_label.pack(padx=10, pady=3)
        
        # ราคา
        price_label = ctk.CTkLabel(card, text=product.format_price(),
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   text_color="#FF6B9D")
        price_label.pack(pady=5)
        
        # ปุ่มหยิบใส่ตะกร้า
        btn_state = "normal" if product.is_available() else "disabled"
        add_btn = ctk.CTkButton(card, text="🛒 หยิบใส่ตะกร้า",
                               height=40, corner_radius=10,
                               font=ctk.CTkFont(size=14, weight="bold"),
                               fg_color="#FFB6C1", hover_color="#FFC0CB",
                               text_color="white", state=btn_state,
                               command=lambda p=product: self.add_to_cart(p))
        add_btn.pack(pady=10, padx=15, fill="x")

        # วางการ์ดลงตาราง
        card.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")

    def add_to_cart(self, product):
        """เพิ่มสินค้าลงตะกร้า"""
        # ตรวจสอบว่า login หรือยัง
        if not self.main_app.session.is_logged_in():
            messagebox.showwarning("กรุณาเข้าสู่ระบบ",
                                  "คุณต้องเข้าสู่ระบบก่อนเพิ่มสินค้าลงตะกร้า",
                                  parent=self)
            return
        
        # เพิ่มลงตะกร้า
        self.cart.add_item(product)
        messagebox.showinfo("ตะกร้าสินค้า",
                           f"เพิ่ม '{product.name}' ลงในตะกร้าแล้ว!",
                           parent=self)