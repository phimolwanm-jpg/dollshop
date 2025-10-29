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
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 2. สร้างส่วนหัว (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        header_title = ctk.CTkLabel(
            header_frame,
            text="💳 ยืนยันคำสั่งซื้อและชำระเงิน",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)

        back_btn = ctk.CTkButton(
            header_frame,
            text="< กลับไปตะกร้า",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('CartWindow')
        )
        back_btn.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Panel ด้านซ้าย (ที่อยู่ และ วิธีชำระเงิน) ---
        left_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(30, 10), pady=10)

        # --- 3.1 ส่วนแสดงที่อยู่สำหรับจัดส่ง ---
        shipping_header_frame = ctk.CTkFrame(left_panel, fg_color="#FFE4E1", corner_radius=15)
        shipping_header_frame.pack(fill="x", padx=20, pady=(20, 10))

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

        # --- vvvv เพิ่มการตรวจสอบตรงนี้ vvvv ---
        # ดึงที่อยู่ (ถ้า Login แล้ว) หรือใช้ข้อความเตือน (ถ้ายังไม่ Login)
        current_user_address = None # เริ่มต้นให้เป็น None
        address_display_text = "⚠️ ยังไม่มีที่อยู่\nกรุณาเพิ่มในหน้าโปรไฟล์" # ข้อความเริ่มต้น
        if self.session.is_logged_in(): # เช็คว่า login หรือยัง
            current_user_address = self.session.current_user.address # ถ้า login แล้ว ค่อยดึง address
            if current_user_address: # ถ้ามี address อยู่แล้ว
                 address_display_text = current_user_address # ใช้ address นั้น
        # --- ^^^^ สิ้นสุดการตรวจสอบ ^^^^ ---

        # Label แสดงที่อยู่ (หรือข้อความเตือน)
        self.address_label = ctk.CTkLabel(
            address_display_frame,
            text=address_display_text, # ใช้ text ที่เตรียมไว้
            justify="left",
            wraplength=400,
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

        self.payment_var = ctk.StringVar(value="โอนเงินผ่านธนาคาร")

        # --- 3.2.2 ตัวเลือกที่ 1: โอนเงิน ---
        radio_bank_transfer = ctk.CTkRadioButton(
            payment_options_frame, text="🏦 โอนเงินผ่านธนาคาร",
            variable=self.payment_var, value="โอนเงินผ่านธนาคาร",
            font=ctk.CTkFont(size=14), text_color="#6D4C41",
            fg_color="#FFB6C1", hover_color="#FFC0CB"
        )
        radio_bank_transfer.pack(anchor="w", padx=25, pady=8)

        # --- 3.2.3 แสดงข้อมูลบัญชี ---
        bank_info_frame = ctk.CTkFrame(payment_options_frame, fg_color="#FFF0F5", corner_radius=10, border_width=1, border_color="#FFEBEE")
        bank_info_frame.pack(fill="x", padx=25, pady=(5, 8))

        bank_info_label = ctk.CTkLabel(
            bank_info_frame, text="📋 เลขที่บัญชี: 123-4-56789-0\nธนาคารกสิกรไทย\nชื่อบัญชี: Dollie Shop",
            justify="left", font=ctk.CTkFont(size=13), text_color="#6D4C41"
        )
        bank_info_label.pack(padx=15, pady=10)

        # --- 3.2.4 ตัวเลือกที่ 2: COD ---
        radio_cod = ctk.CTkRadioButton(
            payment_options_frame, text="📦 เก็บเงินปลายทาง (COD)",
            variable=self.payment_var, value="เก็บเงินปลายทาง",
            font=ctk.CTkFont(size=14), text_color="#6D4C41",
            fg_color="#FFB6C1", hover_color="#FFC0CB"
        )
        radio_cod.pack(anchor="w", padx=25, pady=8)
        # --- จบ Panel ด้านซ้าย ---

        # --- 4. สร้าง Panel ด้านขวา (สรุปรายการสินค้า และ ยอดรวม) ---
        right_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10)

        # --- 4.1 สร้าง Header ของ Panel สรุป ---
        summary_header_frame = ctk.CTkFrame(right_panel, fg_color="#FFE4E1", corner_radius=15)
        summary_header_frame.pack(fill="x", padx=20, pady=(20, 10))

        summary_title_label = ctk.CTkLabel(
            summary_header_frame, text="🛍️ สรุปรายการสินค้า",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41"
        )
        summary_title_label.pack(pady=15)

        # --- 4.2 สร้าง Frame ที่เลื่อนได้สำหรับแสดงรายการสินค้า ---
        summary_items_frame = ctk.CTkScrollableFrame(
            right_panel, fg_color="transparent", scrollbar_button_color="#FFB6C1"
        )
        summary_items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # --- 4.3 วนลูปแสดงรายการสินค้า ---
        cart_items_for_summary = self.cart.get_items()
        for item in cart_items_for_summary:
            item_card_summary = ctk.CTkFrame(summary_items_frame, fg_color="#FFF0F5", corner_radius=10)
            item_card_summary.pack(fill="x", pady=5)

            item_info_summary = ctk.CTkFrame(item_card_summary, fg_color="transparent")
            item_info_summary.pack(fill="x", padx=15, pady=10)

            item_name_label = ctk.CTkLabel(
                item_info_summary, text=f"• {item.product.name}",
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#6D4C41", anchor="w"
            )
            item_name_label.pack(side="left")

            item_quantity_label = ctk.CTkLabel(
                item_info_summary, text=f"x{item.quantity}",
                font=ctk.CTkFont(size=12), text_color="#FFB6C1", anchor="e"
            )
            item_quantity_label.pack(side="right", padx=10)

            item_total_price_label = ctk.CTkLabel(
                item_info_summary, text=item.format_total_price(),
                font=ctk.CTkFont(size=14, weight="bold"), text_color="#FF6B9D", anchor="e"
            )
            item_total_price_label.pack(side="right")

        # --- 4.4 สร้างส่วนแสดงยอดรวม และ ปุ่มยืนยัน ---
        total_section_container = ctk.CTkFrame(right_panel, fg_color="transparent")
        total_section_container.pack(side="bottom", fill="x", padx=20, pady=20)

        # --- 4.4.1 เส้นคั่น ---
        total_separator = ctk.CTkFrame(total_section_container, height=2, fg_color="#FFEBEE")
        total_separator.pack(fill="x", pady=15)

        # --- 4.4.2 Frame แสดงยอดสุทธิ ---
        total_display_frame = ctk.CTkFrame(total_section_container, fg_color="#FFE4E1", corner_radius=15)
        total_display_frame.pack(fill="x", pady=(0, 15))

        total_inner_frame = ctk.CTkFrame(total_display_frame, fg_color="transparent")
        total_inner_frame.pack(fill="x", padx=20, pady=15)

        total_text_label_summary = ctk.CTkLabel(
            total_inner_frame, text="ยอดสุทธิ:",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41"
        )
        total_text_label_summary.pack(side="left")

        total_value_label_summary = ctk.CTkLabel(
            total_inner_frame, text=self.cart.format_total_price(),
            font=ctk.CTkFont(size=24, weight="bold"), text_color="#FF6B9D"
        )
        total_value_label_summary.pack(side="right")

        # --- 4.4.3 ปุ่มยืนยันคำสั่งซื้อ ---
        confirm_order_button = ctk.CTkButton(
            total_section_container, text="✅ ยืนยันคำสั่งซื้อ", command=self.place_order,
            height=50, corner_radius=15, font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#4CAF50", hover_color="#66BB6A", text_color="white"
        )
        confirm_order_button.pack(fill="x")

        # --- 4.5 ปิดการใช้งานปุ่มยืนยัน ถ้าตะกร้าว่าง หรือ ไม่มีที่อยู่ (ใช้ค่า current_user_address ที่เช็คไว้) ---
        # แก้ไขเงื่อนไขตรงนี้
        if not cart_items_for_summary or not current_user_address:
            confirm_order_button.configure(state="disabled")
        # --- จบ Panel ด้านขวา ---

    # --- (ลบฟังก์ชัน create_shipping_payment_panel และ create_summary_panel) ---

    def place_order(self):
        """ดำเนินการสร้างคำสั่งซื้อ (Logic เดิม)"""
        # --- 1. รวบรวมข้อมูล ---
        # --- vvvv เพิ่มการตรวจสอบก่อน ถ้ายังไม่ login ให้หยุด vvvv ---
        if not self.session.is_logged_in():
            messagebox.showerror("ผิดพลาด", "กรุณาเข้าสู่ระบบก่อนทำการสั่งซื้อ", parent=self)
            # อาจจะพาไปหน้า login
            # self.main_app.navigate_to("LoginWindow")
            return
        # --- ^^^^ สิ้นสุดการตรวจสอบ ^^^^ ---

        current_user = self.session.current_user
        items_in_cart = self.cart.get_items()
        cart_total_price = self.cart.get_total_price()
        selected_payment_method = self.payment_var.get()
        user_shipping_address = current_user.address # ดึง address อีกครั้ง (เผื่อมีการเปลี่ยนแปลง)

        # --- 2. ตรวจสอบข้อมูล ---
        if not items_in_cart:
            messagebox.showwarning("ผิดพลาด", "ตะกร้าสินค้าของคุณว่างเปล่า", parent=self)
            return
        if not user_shipping_address:
            messagebox.showwarning("ผิดพลาด", "กรุณาเพิ่มที่อยู่สำหรับจัดส่งในหน้าโปรไฟล์ก่อน", parent=self)
            return

        # --- 3. พยายามสร้าง Order ใน DB ---
        try:
            new_order_id = self.db.create_order(
                user_id=current_user.user_id, total_amount=cart_total_price,
                items=items_in_cart, payment_method=selected_payment_method,
                shipping_address=user_shipping_address
            )
            # --- 4. จัดการผลลัพธ์ ---
            if new_order_id:
                self.cart.clear()
                self.main_app.navigate_to('ThankYouWindow', order_id=new_order_id)
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างคำสั่งซื้อได้ โปรดลองอีกครั้ง", parent=self)

        except Exception as e:
            print(f"เกิด Error ตอนสร้าง Order: {e}")
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดที่ไม่คาดคิด: {e}", parent=self)