import customtkinter as ctk
from models import CartItem 
from tkinter import messagebox
from functools import partial # (1) Import ตัวช่วยสำหรับปุ่ม

class CartWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.cart = main_app.cart

        # (2) ประกาศตัวแปร UI ที่ต้อง "อัปเดต" บ่อยๆ
        self.items_frame_scrollable = None
        self.subtotal_value_label = None
        self.total_value_label = None
        self.checkout_button = None

        # (3) สร้าง "โครงสร้าง" UI หลัก (แค่ครั้งเดียว)
        self.setup_ui_structure() 
        # (4) โหลด "เนื้อหา" (รายการสินค้า) ครั้งแรก
        self.update_cart_display()

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้:
        (ปรับปรุง) ไม่สร้าง UI ใหม่! แค่ "อัปเดต" เนื้อหา
        """
        self.update_cart_display() 

    # ============================================
    # ===== 1. "ผู้จัดการ" สร้างโครงสร้าง UI =====
    # ============================================

    def setup_ui_structure(self):
        """
        สร้าง "โครงสร้าง" ของหน้า (Header, Panel ซ้าย/ขวา)
        ฟังก์ชันนี้จะถูกเรียกแค่ "ครั้งเดียว" ตอนสร้างคลาส
        """
        # --- 1. กำหนด Grid หลัก ---
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=1) 
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้าง Header ---
        self.create_header()
        
        # --- 3. สร้าง Panel ซ้าย (สำหรับรายการสินค้า) ---
        self.create_left_panel()
        
        # --- 4. สร้าง Panel ขวา (สำหรับสรุปยอด) ---
        self.create_right_panel()
        
    def create_header(self):
        """(ผู้ช่วย) สร้างแถบ Header ด้านบน"""
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20)) 
        header_frame.grid_columnconfigure(1, weight=1) 
        
        ctk.CTkLabel(
            header_frame, 
            text="🛒 ตะกร้าสินค้าของคุณ", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        ).pack(side="left", padx=30, pady=20)
        
        ctk.CTkButton(
            header_frame,
            text="< กลับไปช้อปต่อ",
            fg_color="transparent", text_color="#FFB6C1", hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow')
        ).pack(side="right", padx=30, pady=20)

    def create_left_panel(self):
        """(ผู้ช่วย) สร้างโครง Panel ซ้าย และ ScrollableFrame"""
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(30, 10), pady=10) 

        # (5) สร้าง ScrollableFrame และเก็บไว้ใน self
        # เราจะ "ลบของข้างใน" Frame นี้ ไม่ใช่ลบ Frame นี้
        self.items_frame_scrollable = ctk.CTkScrollableFrame(
            left_panel,
            fg_color="transparent", 
            corner_radius=15,
            scrollbar_button_color="#FFB6C1"
        )
        self.items_frame_scrollable.pack(expand=True, fill="both")

    def create_right_panel(self):
        """(ผู้ช่วย) สร้างโครง Panel ขวา (สรุปยอด)"""
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10) 

        summary_card = ctk.CTkFrame(
            right_panel, 
            fg_color="#FFFFFF", 
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        summary_card.pack(fill="both", expand=True) 

        # --- Header สรุปยอด ---
        summary_header = ctk.CTkFrame(summary_card, fg_color="#FFE4E1", corner_radius=15)
        summary_header.pack(fill="x", padx=20, pady=20)
        ctk.CTkLabel(
            summary_header, 
            text="💰 สรุปยอด", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)

        # --- ราคารวม (Subtotal) ---
        subtotal_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        subtotal_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(
            subtotal_frame, 
            text="ราคารวม (Subtotal)",
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        ).pack(side="left")
        
        # (6) สร้าง Label และเก็บไว้ใน self
        self.subtotal_value_label = ctk.CTkLabel( 
            subtotal_frame, 
            text="฿0.00", # (ค่าเริ่มต้น)
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#6D4C41"
        )
        self.subtotal_value_label.pack(side="right")

        # --- เส้นคั่น ---
        ctk.CTkFrame(summary_card, height=2, fg_color="#FFEBEE").pack(fill="x", padx=25, pady=15)

        # --- ยอดสุทธิ (Total) ---
        total_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        total_frame.pack(fill="x", padx=25, pady=10)
        ctk.CTkLabel(
            total_frame, 
            text="ยอดสุทธิ (Total)", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6D4C41"
        ).pack(side="left")
        
        # (7) สร้าง Label และเก็บไว้ใน self
        self.total_value_label = ctk.CTkLabel( 
            total_frame, 
            text="฿0.00", # (ค่าเริ่มต้น)
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color="#FF6B9D"
        )
        self.total_value_label.pack(side="right")

        # --- Spacer ---
        ctk.CTkLabel(summary_card, text="").pack(expand=True) 

        # (8) สร้างปุ่มและเก็บไว้ใน self
        self.checkout_button = ctk.CTkButton(
            summary_card, 
            text="💳 ดำเนินการชำระเงิน", 
            height=50, corner_radius=15, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
            command=lambda: self.main_app.navigate_to('CheckoutWindow')
        )
        self.checkout_button.pack(fill="x", padx=20, pady=(10, 10))

        ctk.CTkButton(
            summary_card, 
            text="< เลือกซื้อสินค้าต่อ", 
            fg_color="transparent", text_color="#FFB6C1", hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow')
        ).pack(pady=(0, 20))
        
    # ============================================
    # ===== 2. ฟังก์ชัน "อัปเดต" เนื้อหา (Dynamic) =====
    # ============================================

    def update_cart_display(self):
        """
        (ฟังก์ชันใหม่) ล้าง "เนื้อหา" เก่าในตะกร้า และสร้างใหม่
        รวมถึงอัปเดตยอดรวม
        """
        
        # --- 1. ล้าง "เนื้อหา" เก่า (ลบ widget ลูกทั้งหมดใน ScrollableFrame) ---
        for widget in self.items_frame_scrollable.winfo_children():
            widget.destroy()

        # --- 2. ดึงข้อมูลใหม่ ---
        cart_items_list = self.cart.get_items() 

        # --- 3. สร้างรายการสินค้าใหม่ (หรือแสดงว่า "ว่างเปล่า") ---
        if not cart_items_list:
            self.show_empty_cart_message()
        else:
            for item_data in cart_items_list:
                self.create_cart_item_card(item_data)
        
        # --- 4. อัปเดตยอดรวม และ สถานะปุ่ม ---
        self.update_summary_panel(cart_items_list)
        
    def show_empty_cart_message(self):
        """(ผู้ช่วย) สร้าง UI เมื่อตะกร้าว่าง"""
        empty_frame = ctk.CTkFrame(
            self.items_frame_scrollable,
            fg_color="#FFFFFF", corner_radius=20, 
            border_width=2, border_color="#FFEBEE"
        )
        empty_frame.pack(expand=True, fill="both", padx=10, pady=10)
        
        ctk.CTkLabel(
            empty_frame, 
            text="🛍️ ตะกร้าของคุณว่างเปล่า", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFB6C1"
        ).pack(expand=True, pady=40) 

    def create_cart_item_card(self, item_data: CartItem):
        """(ผู้ช่วย) สร้างการ์ดสินค้า 1 ชิ้น"""
        
        item_card = ctk.CTkFrame(
            self.items_frame_scrollable,
            fg_color="#FFFFFF", corner_radius=15, height=120,
            border_width=2, border_color="#FFEBEE"
        )

        # --- รูปภาพ ---
        product_image = self.main_app.get_product_image(item_data.product.image_url, size=(100,100)) 
        ctk.CTkLabel(item_card, text="", image=product_image).pack(side="left", padx=15, pady=15)

        # --- รายละเอียด (ชื่อ, ราคา) ---
        details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
        details_frame.pack(side="left", fill="x", expand=True, padx=10) 
        ctk.CTkLabel(
            details_frame, 
            text=item_data.product.name, 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#6D4C41", anchor="w"
        ).pack(fill="x")
        ctk.CTkLabel(
            details_frame, 
            text=item_data.product.format_price(), 
            font=ctk.CTkFont(size=14), 
            text_color="#FFB6C1", anchor="w"
        ).pack(fill="x", pady=(5, 0))

        # --- ส่วนควบคุมจำนวน (+/-) ---
        quantity_frame = ctk.CTkFrame(item_card, fg_color="#FFF0F5", corner_radius=10)
        quantity_frame.pack(side="left", padx=15)
        
        
        minus_button = ctk.CTkButton(
            quantity_frame, text="-", width=35, height=35,
            fg_color="#FFB6C1", hover_color="#FFC0CB",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=partial(self.change_quantity, item_data, -1) 
        )
        minus_button.pack(side="left", padx=5, pady=5)
        
        ctk.CTkLabel(
            quantity_frame, text=f"{item_data.quantity}", width=40,
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#6D4C41"
        ).pack(side="left", padx=5)
        
        plus_button = ctk.CTkButton(
            quantity_frame, text="+", width=35, height=35,
            fg_color="#FFB6C1", hover_color="#FFC0CB",
            font=ctk.CTkFont(size=18, weight="bold"),
            command=partial(self.change_quantity, item_data, 1)
        )
        plus_button.pack(side="left", padx=5, pady=5)

        # --- ราคารวม และ ปุ่มลบ ---
        total_remove_frame = ctk.CTkFrame(item_card, fg_color="transparent", width=150)
        total_remove_frame.pack(side="right", fill="y", padx=20, pady=15) 

        ctk.CTkLabel(
            total_remove_frame, 
            text=item_data.format_total_price(),
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF6B9D"
        ).pack(expand=True) 
        
        remove_button = ctk.CTkButton(
            total_remove_frame, text="🗑️", width=40, height=40,
            fg_color="#FFEBEE", hover_color="#FFB6C1", text_color="#F44336",
            font=ctk.CTkFont(size=18),
            command=partial(self.remove_item, item_data.product.product_id)
        )
        remove_button.pack(expand=True, pady=(5, 0))
        
        item_card.pack(fill="x", padx=10, pady=8) 

    def update_summary_panel(self, cart_items_list):
        """(ผู้ช่วย) อัปเดต Label ยอดรวม และสถานะปุ่ม Checkout"""
        
        # 1. อัปเดตข้อความราคารวม
        total_price_str = self.cart.format_total_price()
        self.subtotal_value_label.configure(text=total_price_str)
        self.total_value_label.configure(text=total_price_str)
        
        # 2. อัปเดตสถานะปุ่ม
        if not cart_items_list:
            self.checkout_button.configure(state="disabled")
        else:
            self.checkout_button.configure(state="normal")
            
    # ============================================
    # ===== 3. ฟังก์ชันจัดการ Logic (Actions) =====
    # ============================================

    def change_quantity(self, item: CartItem, amount: int):
        """เพิ่ม/ลด จำนวนสินค้า แล้ว refresh หน้าจอ"""
        new_quantity = item.quantity + amount
        product_id = item.product.product_id
        
        if new_quantity > 0:
            self.cart.update_quantity(product_id, new_quantity) 
        else:
            # ถ้าจำนวน <= 0 ให้ลบออก
            self.remove_item(product_id) 
            # (remove_item จะเรียก update_cart_display() ให้เอง)
            return 

        # เรียก update_cart_display
        self.update_cart_display() 

    def remove_item(self, product_id: int):
        """ลบสินค้าออกจากตะกร้า (หลังจากยืนยัน) แล้ว refresh หน้าจอ"""
        user_confirmed = messagebox.askyesno("ยืนยัน", "คุณต้องการลบสินค้านี้ออกจากตะกร้าหรือไม่?", parent=self)
        
        if user_confirmed: 
            self.cart.remove_item(product_id) 
        
            self.update_cart_display()