import customtkinter as ctk
# CartItem ไม่ได้ถูก *ใช้* โดยตรงใน UI แล้ว แต่ import ไว้เผื่อ (ตามสไตล์พื้นฐาน)
from models import CartItem 
from tkinter import messagebox

class CartWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        self.cart = main_app.cart

        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้รายการสินค้าและยอดรวมอัปเดตเสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบทั้งหมดของหน้าตะกร้าสินค้า"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # คอลัมน์ 0 (รายการสินค้า) กว้าง 3 ส่วน
        self.grid_columnconfigure(0, weight=3) 
        # คอลัมน์ 1 (สรุปยอด) กว้าง 1 ส่วน
        self.grid_columnconfigure(1, weight=1) 
        # แถวที่ 1 (เนื้อหาหลัก) ให้ขยายตามแนวตั้ง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        # วาง header แถวบนสุด (row=0) กินพื้นที่ 2 คอลัมน์ (columnspan=2) ยืดเต็มกว้าง (sticky="ew")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันปุ่มไปขวา)
        header_frame.grid_columnconfigure(1, weight=1) 
        
        # Label ชื่อหน้า
        header_title = ctk.CTkLabel(
            header_frame, 
            text="🛒 ตะกร้าสินค้าของคุณ", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # ปุ่ม "< กลับไปช้อปต่อ"
        back_btn = ctk.CTkButton(
            header_frame,
            text="< กลับไปช้อปต่อ",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow') # กดแล้วกลับหน้า Home
        )
        back_btn.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Panel ด้านซ้าย (รายการสินค้า) ---
        left_panel = ctk.CTkFrame(self, fg_color="transparent")
        # วาง left_panel ในแถว 1, คอลัมน์ 0 ยืดเต็มพื้นที่
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(30, 10), pady=10) 

        # --- 3.1 สร้าง Frame ที่เลื่อนได้สำหรับใส่รายการสินค้า ---
        items_frame_scrollable = ctk.CTkScrollableFrame(
            left_panel, # ใส่ใน left_panel
            fg_color="transparent", 
            corner_radius=15,
            scrollbar_button_color="#FFB6C1"
        )
        items_frame_scrollable.pack(expand=True, fill="both") # ให้ขยายเต็ม left_panel

        # --- 3.2 ดึงข้อมูลสินค้าในตะกร้า ---
        cart_items_list = self.cart.get_items() 

        # --- 3.3 ตรวจสอบว่าตะกร้าว่างหรือไม่ ---
        if not cart_items_list:
            # --- ถ้าตะกร้าว่าง: แสดงข้อความ ---
            empty_frame = ctk.CTkFrame(items_frame_scrollable, # ใส่ใน frame ที่เลื่อนได้
                                       fg_color="#FFFFFF", 
                                       corner_radius=20, 
                                       border_width=2, 
                                       border_color="#FFEBEE")
            empty_frame.pack(expand=True, fill="both", padx=10, pady=10)
            
            empty_label = ctk.CTkLabel(
                empty_frame, 
                text="🛍️ ตะกร้าของคุณว่างเปล่า", 
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFB6C1"
            )
            # expand=True ให้ label อยู่กลาง frame
            empty_label.pack(expand=True, pady=40) 
            # --- จบกรณีตะกร้าว่าง ---
        else:
            # --- ถ้าตะกร้าไม่ว่าง: วนลูปสร้างการ์ดสินค้า ---
            for item_data in cart_items_list: # item_data คือ CartItem object
                # --- สร้าง Widget สำหรับสินค้า 1 ชิ้น---
                
                # การ์ดหลักสำหรับสินค้า 1 ชิ้น
                item_card = ctk.CTkFrame(
                    items_frame_scrollable, # ใส่การ์ดลงใน frame ที่เลื่อนได้
                    fg_color="#FFFFFF", 
                    corner_radius=15, 
                    height=120, # กำหนดความสูงของการ์ด
                    border_width=2,
                    border_color="#FFEBEE"
                )

                # --- ส่วนรูปภาพ (ซ้ายสุด) ---
                # ใช้ main_app.get_product_image 
                product_image = self.main_app.get_product_image(item_data.product.image_url, size=(100,100)) 
                image_label = ctk.CTkLabel(item_card, text="", image=product_image)
                image_label.pack(side="left", padx=15, pady=15)

                # --- ส่วนรายละเอียด (ชื่อ, ราคา) (ถัดจากรูป) ---
                details_frame = ctk.CTkFrame(item_card, fg_color="transparent")
                # fill="x" ให้ยืดตามแนวนอน, expand=True ให้กินพื้นที่ที่เหลือ
                details_frame.pack(side="left", fill="x", expand=True, padx=10) 
                
                # ชื่อสินค้า
                name_label = ctk.CTkLabel(
                    details_frame, 
                    text=item_data.product.name, # ดึงชื่อจาก product object ใน item_data
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#6D4C41",
                    anchor="w" # ชิดซ้าย
                )
                name_label.pack(fill="x") # ยืดเต็มความกว้างของ details_frame
                
                # ราคาต่อชิ้น
                price_label = ctk.CTkLabel(
                    details_frame, 
                    text=item_data.product.format_price(), # เรียกใช้ format_price() จาก product object
                    font=ctk.CTkFont(size=14), 
                    text_color="#FFB6C1", 
                    anchor="w"
                )
                price_label.pack(fill="x", pady=(5, 0))

                # --- ส่วนควบคุมจำนวน (+/-) (ถัดจากรายละเอียด) ---
                quantity_frame = ctk.CTkFrame(item_card, fg_color="#FFF0F5", corner_radius=10)
                quantity_frame.pack(side="left", padx=15)
                
                # ปุ่มลด (-)
                minus_button = ctk.CTkButton(
                    quantity_frame, 
                    text="-", 
                    width=35, height=35, corner_radius=10,
                    fg_color="#FFB6C1", hover_color="#FFC0CB",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    # ใช้ lambda capture เพื่อส่ง item_data และ -1 ไปให้ change_quantity
                    command=lambda current_item=item_data: self.change_quantity(current_item, -1) 
                )
                minus_button.pack(side="left", padx=5, pady=5)
                
                # Label แสดงจำนวนปัจจุบัน
                quantity_label = ctk.CTkLabel(
                    quantity_frame, 
                    text=f"{item_data.quantity}", # แสดงจำนวนจาก item_data
                    width=40, 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#6D4C41"
                )
                quantity_label.pack(side="left", padx=5)
                
                # ปุ่มเพิ่ม (+)
                plus_button = ctk.CTkButton(
                    quantity_frame, 
                    text="+", 
                    width=35, height=35, corner_radius=10,
                    fg_color="#FFB6C1", hover_color="#FFC0CB",
                    font=ctk.CTkFont(size=18, weight="bold"),
                     # ใช้ lambda capture เพื่อส่ง item_data และ +1 ไปให้ change_quantity
                    command=lambda current_item=item_data: self.change_quantity(current_item, 1)
                )
                plus_button.pack(side="left", padx=5, pady=5)

                # --- ส่วนราคารวม และ ปุ่มลบ (ขวาสุด) ---
                total_remove_frame = ctk.CTkFrame(item_card, fg_color="transparent", width=150)
                # fill="y" ให้ยืดตามแนวตั้ง
                total_remove_frame.pack(side="right", fill="y", padx=20, pady=15) 

                # Label แสดงราคารวมของรายการนี้
                item_total_label = ctk.CTkLabel(
                    total_remove_frame, 
                    text=item_data.format_total_price(), # เรียก format_total_price() ของ CartItem
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#FF6B9D"
                )
                # expand=True เพื่อให้ label นี้อยู่ตรงกลางแนวตั้ง (ถ้ามีพื้นที่เหลือ)
                item_total_label.pack(expand=True) 
                
                # ปุ่มลบ (ถังขยะ)
                remove_button = ctk.CTkButton(
                    total_remove_frame, 
                    text="🗑️", 
                    width=40, height=40, corner_radius=10,
                    fg_color="#FFEBEE", hover_color="#FFB6C1",
                    text_color="#F44336", # สีแดง
                    font=ctk.CTkFont(size=18),
                    # ใช้ lambda capture เพื่อส่ง product_id ไปให้ remove_item
                    command=lambda prod_id=item_data.product.product_id: self.remove_item(prod_id) 
                )
                remove_button.pack(expand=True, pady=(5, 0))
                # --- จบการสร้าง Widget สำหรับสินค้า 1 ชิ้น ---

                # วางการ์ดสินค้าที่สร้างเสร็จ ลงใน frame ที่เลื่อนได้
                item_card.pack(fill="x", padx=10, pady=8) 
            # --- จบ Loop สร้างการ์ดสินค้า ---
        # --- จบ Panel ด้านซ้าย ---

        # --- 4. สร้าง Panel ด้านขวา (สรุปยอด) ---
        right_panel = ctk.CTkFrame(self, fg_color="transparent")
        # วาง right_panel ในแถว 1, คอลัมน์ 1 ยืดเต็มพื้นที่
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10) 

        # --- 4.1 สร้างการ์ดสรุปยอด ---
        summary_card = ctk.CTkFrame(
            right_panel, # ใส่ใน right_panel
            fg_color="#FFFFFF", 
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        # ให้การ์ดขยายเต็ม right_panel
        summary_card.pack(fill="both", expand=True) 

        # --- 4.2 สร้าง Header ของการ์ดสรุป ---
        summary_header = ctk.CTkFrame(summary_card, fg_color="#FFE4E1", corner_radius=15)
        summary_header.pack(fill="x", padx=20, pady=20)
        
        summary_title = ctk.CTkLabel(
            summary_header, 
            text="💰 สรุปยอด", 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#6D4C41"
        )
        summary_title.pack(pady=15)

        # --- 4.3 แสดงราคารวม (Subtotal) ---
        subtotal_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        subtotal_frame.pack(fill="x", padx=25, pady=10)
        
        subtotal_text_label = ctk.CTkLabel(
            subtotal_frame, 
            text="ราคารวม (Subtotal)",
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        subtotal_text_label.pack(side="left")
        
        # Label ที่จะแสดงราคารวม (เก็บไว้ใน self เพื่ออัปเดต ถ้าต้องการ)
        # ดึงราคาจาก self.cart.format_total_price()
        self.subtotal_value_label = ctk.CTkLabel( 
            subtotal_frame, 
            text=self.cart.format_total_price(), 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#6D4C41"
        )
        self.subtotal_value_label.pack(side="right")

        # --- 4.4 เส้นคั่น ---
        separator = ctk.CTkFrame(summary_card, height=2, fg_color="#FFEBEE")
        separator.pack(fill="x", padx=25, pady=15)

        # --- 4.5 แสดงยอดสุทธิ (Total) ---
        total_frame = ctk.CTkFrame(summary_card, fg_color="transparent")
        total_frame.pack(fill="x", padx=25, pady=10)
        
        total_text_label = ctk.CTkLabel(
            total_frame, 
            text="ยอดสุทธิ (Total)", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6D4C41"
        )
        total_text_label.pack(side="left")
        
        # Label ที่จะแสดงยอดสุทธิ (เก็บไว้ใน self เพื่ออัปเดต ถ้าต้องการ)
        self.total_value_label = ctk.CTkLabel( 
            total_frame, 
            text=self.cart.format_total_price(), # ยอดรวมกับยอดสุทธิเท่ากันในกรณีนี้
            font=ctk.CTkFont(size=22, weight="bold"), 
            text_color="#FF6B9D"
        )
        self.total_value_label.pack(side="right")

        # --- 4.6 Spacer (ตัวเว้นวรรคแนวตั้ง) ---
        # ใช้ Label ว่างๆ แล้ว pack(expand=True) เพื่อดันปุ่มลงไปข้างล่าง
        spacer = ctk.CTkLabel(summary_card, text="")
        spacer.pack(expand=True) 

        # --- 4.7 ปุ่มดำเนินการ ---
        # ปุ่ม "ดำเนินการชำระเงิน"
        checkout_button = ctk.CTkButton(
            summary_card, 
            text="💳 ดำเนินการชำระเงิน", 
            height=50, 
            corner_radius=15, 
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white",
            command=lambda: self.main_app.navigate_to('CheckoutWindow') # กดแล้วไปหน้า Checkout
        )
        checkout_button.pack(fill="x", padx=20, pady=(10, 10))

        # ปุ่ม "เลือกซื้อสินค้าต่อ"
        continue_button = ctk.CTkButton(
            summary_card, 
            text="< เลือกซื้อสินค้าต่อ", 
            fg_color="transparent", 
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow') # กดแล้วกลับหน้า Home
        )
        continue_button.pack(pady=(0, 20))
        
        # --- 4.8 ปิดการใช้งานปุ่มชำระเงิน ถ้าตะกร้าว่าง ---
        if not cart_items_list: # ใช้ cart_items_list ที่ดึงมาตอนแรก
            checkout_button.configure(state="disabled") # ทำให้ปุ่มเป็นสีเทา กดไม่ได้
        # --- จบ Panel ด้านขวา ---

    
    # --- ฟังก์ชันจัดการ Logic (เหมือนเดิม) ---
    def change_quantity(self, item, amount: int):
        """เพิ่ม/ลด จำนวนสินค้า แล้ว refresh หน้าจอ"""
        new_quantity = item.quantity + amount
        product_id = item.product.product_id
        
        if new_quantity > 0:
            # สั่งอัปเดตจำนวนใน Cart object
            self.cart.update_quantity(product_id, new_quantity) 
        else:
            # ถ้าจำนวน <= 0 ให้ลบออก (แต่ต้องถามยืนยันก่อน)
            self.remove_item(product_id) 
            # การเรียก on_show() จะถูกทำใน remove_item ถ้าลบสำเร็จ
            return # ออกจากฟังก์ชันนี้เลย เพราะ remove_item จะ refresh ให้เอง

        # ถ้าแค่ update จำนวน (ไม่ได้ลบ) ให้ refresh หน้าจอ
        self.on_show() 

    def remove_item(self, product_id: int):
        """ลบสินค้าออกจากตะกร้า (หลังจากยืนยัน) แล้ว refresh หน้าจอ"""
        # แสดง popup ถามยืนยัน
        user_confirmed = messagebox.askyesno("ยืนยัน", "คุณต้องการลบสินค้านี้ออกจากตะกร้าหรือไม่?", parent=self)
        
        if user_confirmed: # ถ้าผู้ใช้กด Yes
            # สั่งลบ item ใน Cart object
            self.cart.remove_item(product_id) 
            # Refresh หน้าจอเพื่อให้ UI อัปเดต
            self.on_show()