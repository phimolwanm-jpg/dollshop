import customtkinter as ctk
from tkinter import messagebox
# Session และ Cart ไม่ได้ถูก *ใช้* โดยตรงใน UI แล้ว (แต่ยังใช้ใน place_order)
# from models import Session, Cart 
# Database ไม่ได้ถูก *ใช้* โดยตรงใน UI แล้ว (แต่ยังใช้ใน place_order)
# from database import Database 

class CheckoutWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app มาเก็บไว้
        self.session = main_app.session 
        self.cart = main_app.cart
        self.db = main_app.db
        # --- ไม่ต้องมี self.assets ถ้าใช้ main_app.load_image ---
        # self.assets = main_app.assets 
        # self.edit_window = None # ไม่ได้ใช้งาน

        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ข้อมูลที่อยู่ และสถานะตะกร้าสดใหม่เสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Checkout"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # คอลัมน์ 0 (ซ้าย: ที่อยู่/ชำระเงิน) กว้าง 2 ส่วน
        self.grid_columnconfigure(0, weight=2) 
        # คอลัมน์ 1 (ขวา: สรุปยอด) กว้าง 1 ส่วน
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
            text="💳 ยืนยันคำสั่งซื้อและชำระเงิน",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # ปุ่ม "< กลับไปตะกร้า"
        back_btn = ctk.CTkButton(
            header_frame,
            text="< กลับไปตะกร้า",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('CartWindow') # กดแล้วกลับไปหน้า Cart
        )
        back_btn.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Panel ด้านซ้าย (ที่อยู่ และ วิธีชำระเงิน) ---
        # (ย้ายโค้ดจาก create_shipping_payment_panel มาไว้ตรงนี้)
        left_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        # วาง left_panel ในแถว 1, คอลัมน์ 0 ยืดเต็มพื้นที่
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(30, 10), pady=10) 
        # pack_propagate(False) ป้องกัน panel หดตามเนื้อหา (อาจไม่จำเป็นถ้า grid layout ดี)
        # left_panel.pack_propagate(False) 

        # --- 3.1 ส่วนแสดงที่อยู่สำหรับจัดส่ง ---
        shipping_header_frame = ctk.CTkFrame(left_panel, fg_color="#FFE4E1", corner_radius=15)
        shipping_header_frame.pack(fill="x", padx=20, pady=(20, 10)) # fill="x" ให้ยืดเต็มความกว้าง
        
        shipping_title_label = ctk.CTkLabel(
            shipping_header_frame,
            text="📦 ที่อยู่สำหรับจัดส่ง",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        shipping_title_label.pack(pady=15, padx=20)
        
        # --- 3.1.1 Frame แสดงที่อยู่ ---
        address_display_frame = ctk.CTkFrame(left_panel, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        address_display_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        # ดึงที่อยู่จาก session
        current_user_address = self.session.current_user.address 
        # ถ้าไม่มีที่อยู่ ให้ใช้ข้อความเตือน
        address_display_text = current_user_address if current_user_address else "⚠️ ยังไม่มีที่อยู่\nกรุณาเพิ่มในหน้าโปรไฟล์" 
        
        # Label แสดงที่อยู่ (หรือข้อความเตือน)
        self.address_label = ctk.CTkLabel( # เก็บไว้ใน self เผื่อต้องการอ้างอิง (แต่ตอนนี้ไม่ได้ใช้)
            address_display_frame,
            text=address_display_text,
            justify="left", # จัดชิดซ้าย (ถ้ามีหลายบรรทัด)
            wraplength=400, # กำหนดความกว้างสูงสุดก่อนขึ้นบรรทัดใหม่
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        self.address_label.pack(padx=20, pady=20)
        
        # --- 3.1.2 ปุ่มแก้ไขที่อยู่ ---
        edit_address_button = ctk.CTkButton(
            left_panel,
            text="✏️ แก้ไขที่อยู่",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            border_width=1,
            border_color="#FFB6C1",
            corner_radius=10,
            # กดแล้วให้ไปหน้า Profile (เมื่อแก้เสร็จ กลับมาหน้านี้ on_show จะ refresh ให้เอง)
            command=lambda: self.main_app.navigate_to('ProfileWindow') 
        )
        edit_address_button.pack(padx=20, pady=(0, 20))
        
        # --- 3.2 ส่วนเลือกวิธีการชำระเงิน ---
        payment_header_frame = ctk.CTkFrame(left_panel, fg_color="#FFE4E1", corner_radius=15)
        payment_header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        payment_title_label = ctk.CTkLabel(
            payment_header_frame,
            text="💰 วิธีการชำระเงิน",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        payment_title_label.pack(pady=15, padx=20)
        
        # --- 3.2.1 Frame สำหรับวางตัวเลือก ---
        payment_options_frame = ctk.CTkFrame(left_panel, fg_color="transparent")
        payment_options_frame.pack(fill="x", padx=20, pady=10)
        
        # สร้างตัวแปร String เพื่อเก็บค่าที่เลือก (จำเป็นสำหรับ RadioButton)
        # กำหนดค่าเริ่มต้นเป็น "โอนเงินผ่านธนาคาร"
        self.payment_var = ctk.StringVar(value="โอนเงินผ่านธนาคาร") 
        
        # --- 3.2.2 ตัวเลือกที่ 1: โอนเงิน ---
        radio_bank_transfer = ctk.CTkRadioButton(
            payment_options_frame,
            text="🏦 โอนเงินผ่านธนาคาร",
            variable=self.payment_var, # ผูกกับตัวแปร payment_var
            value="โอนเงินผ่านธนาคาร",   # ค่าของตัวเลือกนี้
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio_bank_transfer.pack(anchor="w", padx=25, pady=8) # anchor="w" ให้ชิดซ้าย
        
        # --- 3.2.3 แสดงข้อมูลบัญชี (ใต้ตัวเลือกโอนเงิน) ---
        bank_info_frame = ctk.CTkFrame(payment_options_frame, fg_color="#FFF0F5", corner_radius=10, border_width=1, border_color="#FFEBEE")
        bank_info_frame.pack(fill="x", padx=25, pady=(5, 8))
        
        bank_info_label = ctk.CTkLabel(
            bank_info_frame,
            text="📋 เลขที่บัญชี: 123-4-56789-0\nธนาคารกสิกรไทย\nชื่อบัญชี: Dollie Shop",
            justify="left",
            font=ctk.CTkFont(size=13),
            text_color="#6D4C41"
        )
        bank_info_label.pack(padx=15, pady=10)
        
        # --- 3.2.4 ตัวเลือกที่ 2: เก็บเงินปลายทาง (COD) ---
        radio_cod = ctk.CTkRadioButton(
            payment_options_frame,
            text="📦 เก็บเงินปลายทาง (COD)",
            variable=self.payment_var, # ผูกกับตัวแปร payment_var เดียวกัน
            value="เก็บเงินปลายทาง",     # ค่าของตัวเลือกนี้
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio_cod.pack(anchor="w", padx=25, pady=8)
        # --- จบ Panel ด้านซ้าย ---

        # --- 4. สร้าง Panel ด้านขวา (สรุปรายการสินค้า และ ยอดรวม) ---
        # (ย้ายโค้ดจาก create_summary_panel มาไว้ตรงนี้)
        right_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        # วาง right_panel ในแถว 1, คอลัมน์ 1 ยืดเต็มพื้นที่
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10) 

        # --- 4.1 สร้าง Header ของ Panel สรุป ---
        summary_header_frame = ctk.CTkFrame(right_panel, fg_color="#FFE4E1", corner_radius=15)
        summary_header_frame.pack(fill="x", padx=20, pady=(20, 10))
        
        summary_title_label = ctk.CTkLabel(
            summary_header_frame,
            text="🛍️ สรุปรายการสินค้า",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        summary_title_label.pack(pady=15)

        # --- 4.2 สร้าง Frame ที่เลื่อนได้สำหรับแสดงรายการสินค้า ---
        summary_items_frame = ctk.CTkScrollableFrame(
            right_panel, # ใส่ใน right_panel
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        # fill="both", expand=True ให้ขยายเต็มพื้นที่ที่เหลือ (เหนือส่วน Total)
        summary_items_frame.pack(fill="both", expand=True, padx=20, pady=10) 

        # --- 4.3 วนลูปแสดงรายการสินค้า ---
        cart_items_for_summary = self.cart.get_items() # ดึงรายการสินค้าจาก Cart
        for item in cart_items_for_summary:
            # สร้าง Frame เล็กๆ สำหรับสินค้าแต่ละรายการ
            item_card_summary = ctk.CTkFrame(summary_items_frame, fg_color="#FFF0F5", corner_radius=10)
            item_card_summary.pack(fill="x", pady=5)
            
            # Frame ภายในสำหรับจัดวาง Label
            item_info_summary = ctk.CTkFrame(item_card_summary, fg_color="transparent")
            item_info_summary.pack(fill="x", padx=15, pady=10)
            
            # Label ชื่อสินค้า
            item_name_label = ctk.CTkLabel(
                item_info_summary,
                text=f"• {item.product.name}", # ใส่ • นำหน้า
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6D4C41",
                anchor="w" # ชิดซ้าย
            )
            item_name_label.pack(side="left")
            
            # Label จำนวนสินค้า (ชิดขวา)
            item_quantity_label = ctk.CTkLabel(
                item_info_summary,
                text=f"x{item.quantity}",
                font=ctk.CTkFont(size=12),
                text_color="#FFB6C1",
                anchor="e" # ชิดขวา
            )
            item_quantity_label.pack(side="right", padx=10)
            
            # Label ราคารวมของรายการ (ชิดขวา, ก่อนจำนวน)
            item_total_price_label = ctk.CTkLabel(
                item_info_summary,
                text=item.format_total_price(), # ใช้ format_total_price ของ CartItem
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FF6B9D",
                anchor="e" # ชิดขวา
            )
            item_total_price_label.pack(side="right")
            
        # --- 4.4 สร้างส่วนแสดงยอดรวม และ ปุ่มยืนยัน (อยู่ด้านล่างสุด) ---
        total_section_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        # side="bottom" ให้อยู่ล่างสุด, fill="x" ให้ยืดเต็มกว้าง
        total_section_container.pack(side="bottom", fill="x", padx=20, pady=20) 
        
        # --- 4.4.1 เส้นคั่น ---
        total_separator = ctk.CTkFrame(total_section_container, height=2, fg_color="#FFEBEE")
        total_separator.pack(fill="x", pady=15)
        
        # --- 4.4.2 Frame แสดงยอดสุทธิ ---
        total_display_frame = ctk.CTkFrame(total_section_container, fg_color="#FFE4E1", corner_radius=15)
        total_display_frame.pack(fill="x", pady=(0, 15))
        
        # Frame ภายในสำหรับจัดวาง
        total_inner_frame = ctk.CTkFrame(total_display_frame, fg_color="transparent")
        total_inner_frame.pack(fill="x", padx=20, pady=15)
        
        # Label "ยอดสุทธิ:"
        total_text_label_summary = ctk.CTkLabel(
            total_inner_frame,
            text="ยอดสุทธิ:",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        total_text_label_summary.pack(side="left")
        
        # Label แสดงยอดสุทธิ (ดึงจาก cart)
        total_value_label_summary = ctk.CTkLabel(
            total_inner_frame,
            text=self.cart.format_total_price(), # ใช้ format_total_price ของ Cart
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF6B9D"
        )
        total_value_label_summary.pack(side="right")
        
        # --- 4.4.3 ปุ่มยืนยันคำสั่งซื้อ ---
        confirm_order_button = ctk.CTkButton(
            total_section_container, # ใส่ใน container หลักของส่วน total
            text="✅ ยืนยันคำสั่งซื้อ",
            command=self.place_order, # กดแล้วเรียกฟังก์ชัน place_order
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            text_color="white"
        )
        confirm_order_button.pack(fill="x") # ยืดเต็มความกว้าง

        # --- 4.5 ปิดการใช้งานปุ่มยืนยัน ถ้าตะกร้าว่าง หรือ ไม่มีที่อยู่ ---
        # เช็คทั้งสองเงื่อนไข
        if not cart_items_for_summary or not current_user_address: 
            confirm_order_button.configure(state="disabled") # ทำให้ปุ่มกดไม่ได้
        # --- จบ Panel ด้านขวา ---

    # --- (ลบฟังก์ชัน create_shipping_payment_panel และ create_summary_panel) ---

    def place_order(self):
        """ดำเนินการสร้างคำสั่งซื้อ (Logic เดิม)"""
        # --- 1. รวบรวมข้อมูล ---
        current_user = self.session.current_user
        items_in_cart = self.cart.get_items()
        cart_total_price = self.cart.get_total_price()
        selected_payment_method = self.payment_var.get() # ดึงค่าจาก RadioButton
        user_shipping_address = current_user.address

        # --- 2. ตรวจสอบข้อมูล (ป้องกันอีกชั้น) ---
        if not items_in_cart:
            messagebox.showwarning("ผิดพลาด", "ตะกร้าสินค้าของคุณว่างเปล่า", parent=self)
            return # หยุดทำงาน
        if not user_shipping_address:
            messagebox.showwarning("ผิดพลาด", "กรุณาเพิ่มที่อยู่สำหรับจัดส่งในหน้าโปรไฟล์ก่อน", parent=self)
            return # หยุดทำงาน

        # --- 3. พยายามสร้าง Order ใน DB ---
        try:
            # เรียกฟังก์ชัน create_order ใน database.py
            new_order_id = self.db.create_order(
                user_id=current_user.user_id,
                total_amount=cart_total_price,
                items=items_in_cart, # ส่ง List ของ CartItem object ไป
                payment_method=selected_payment_method,
                shipping_address=user_shipping_address
            )
            # --- 4. จัดการผลลัพธ์ ---
            if new_order_id: # ถ้าสร้างสำเร็จ (ได้ order_id กลับมา)
                self.cart.clear() # ล้างตะกร้า!
                # ไปหน้า ThankYou พร้อมส่ง order_id ไปด้วย
                self.main_app.navigate_to('ThankYouWindow', order_id=new_order_id) 
            else: # ถ้า create_order คืนค่า None (อาจเกิด error ที่ดักจับได้ใน DB)
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างคำสั่งซื้อได้ โปรดลองอีกครั้ง", parent=self)
                
        except Exception as e: # ดักจับ error อื่นๆ ที่อาจเกิดขึ้นระหว่างการสร้าง order
            print(f"เกิด Error ตอนสร้าง Order: {e}") # แสดง error ใน console (สำหรับ debug)
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}", parent=self)