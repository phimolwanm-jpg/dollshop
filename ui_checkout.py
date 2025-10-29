import customtkinter as ctk
from tkinter import messagebox, filedialog # <--- เพิ่ม filedialog
import os # <--- เพิ่ม os
import time # <--- เพิ่ม time
from PIL import Image # <--- ต้องติดตั้ง pip install pillow ก่อน

class CheckoutWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        self.session = main_app.session
        self.cart = main_app.cart
        self.db = main_app.db
        self.assets = main_app.assets
        self.edit_window = None
        
        # VVVV เพิ่มตัวแปรสำหรับจัดการสลิป VVVV
        self.uploaded_slip_path = None # Path ของไฟล์สลิปที่เลือกมา
        self.slip_filename_label = None # Label แสดงชื่อไฟล์
        # ^^^^ สิ้นสุดส่วนเพิ่ม ^^^^

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        # รีเซ็ตตัวแปรเมื่อเข้าหน้านี้
        self.uploaded_slip_path = None
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
        # VVVV เรียกอัปเดตสถานะปุ่มเมื่อเปิดหน้า VVVV
        self.update_payment_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมด"""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header (เหมือนเดิม) ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame,
            text="💳 ยืนยันคำสั่งซื้อและชำระเงิน",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        ).pack(side="left", padx=30, pady=20)
        
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

        # --- Left Panel ---
        left_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        left_panel.grid(row=1, column=0, sticky="nsew", padx=(30, 10), pady=10)
        self.create_shipping_payment_panel(left_panel)
        
        # --- Right Panel ---
        right_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10)
        self.create_summary_panel(right_panel)

    def create_shipping_payment_panel(self, parent):
        """สร้าง Panel ที่อยู่และวิธีการชำระเงิน (ปรับปรุง)"""
        parent.pack_propagate(False)
        
        # Shipping Address Section (เหมือนเดิม)
        shipping_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        shipping_header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            shipping_header,
            text="📦 ที่อยู่สำหรับจัดส่ง",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15, padx=20)
        
        address_frame = ctk.CTkFrame(parent, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        address_frame.pack(fill="x", padx=20, pady=(0, 20))
        
        address_text = self.session.current_user.address or "⚠️ ยังไม่มีที่อยู่\nกรุณาเพิ่มในหน้าโปรไฟล์"
        self.address_label = ctk.CTkLabel(
            address_frame,
            text=address_text,
            justify="left",
            wraplength=400,
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        self.address_label.pack(padx=20, pady=20)
        
        edit_btn = ctk.CTkButton(
            parent,
            text="✏️ แก้ไขที่อยู่",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            border_width=1,
            border_color="#FFB6C1",
            corner_radius=10,
            command=lambda: self.main_app.navigate_to('ProfileWindow')
        )
        edit_btn.pack(padx=20, pady=(0, 20))
        
        # Payment Method Section (เหมือนเดิม)
        payment_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        payment_header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            payment_header,
            text="💰 วิธีการชำระเงิน",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15, padx=20)
        
        # Payment Options
        payment_frame = ctk.CTkFrame(parent, fg_color="transparent")
        payment_frame.pack(fill="x", padx=20, pady=10)
        
        self.payment_var = ctk.StringVar(value="โอนเงินผ่านธนาคาร")
        self.payment_var.trace_add("write", lambda name, index, mode: self.update_payment_ui()) # <--- เพิ่ม trace
        
        radio1 = ctk.CTkRadioButton(
            payment_frame,
            text="🏦 โอนเงินผ่านธนาคาร (พร้อมแนบสลิป)",
            variable=self.payment_var,
            value="โอนเงินผ่านธนาคาร",
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio1.pack(anchor="w", padx=25, pady=8)
        
        # VVVV ส่วน QR Code และแนบสลิป VVVV
        self.bank_transfer_detail_frame = ctk.CTkFrame(payment_frame, fg_color="#FFF0F5", corner_radius=10, border_width=1, border_color="#FFEBEE")
        # โค้ด pack จะถูกเรียกใน update_payment_ui
        
        # QR Code Section
        qr_code_frame = ctk.CTkFrame(self.bank_transfer_detail_frame, fg_color="transparent")
        qr_code_frame.pack(side="left", padx=15, pady=10, fill="y")
        
        # Load QR Code Image (สมมติต้องมี assets/qr_code.png)
        try:
            qr_img = Image.open("assets/qr_code.png").resize((120, 120), Image.LANCZOS)
            self.qr_ctk_img = ctk.CTkImage(qr_img, size=(120, 120))
            ctk.CTkLabel(qr_code_frame, image=self.qr_ctk_img, text="").pack(pady=5)
        except:
             ctk.CTkLabel(qr_code_frame, text="[QR Code ไม่พบ]", text_color="#F44336").pack(pady=5)

        # Bank Info Text
        bank_info_text = ctk.CTkFrame(self.bank_transfer_detail_frame, fg_color="transparent")
        bank_info_text.pack(side="left", padx=15, pady=10, fill="both", expand=True)

        ctk.CTkLabel(
            bank_info_text,
            text="📋 เลขที่บัญชี: 123-4-56789-0\nธนาคารกสิกรไทย\nชื่อบัญชี: Dollie Shop",
            justify="left",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#6D4C41",
            anchor="w"
        ).pack(anchor="w", pady=(0, 5))

        # Upload Slip Section
        self.upload_slip_frame = ctk.CTkFrame(bank_info_text, fg_color="transparent")
        self.upload_slip_frame.pack(fill="x", pady=(5, 0))
        self.upload_slip_frame.grid_columnconfigure(0, weight=1)

        upload_btn = ctk.CTkButton(
            self.upload_slip_frame,
            text="อัปโหลดสลิป",
            command=self.select_slip_image,
            font=ctk.CTkFont(size=13),
            fg_color="#4CAF50",
            hover_color="#66BB6A"
        )
        upload_btn.grid(row=0, column=0, padx=(0, 10), sticky="ew")

        self.slip_filename_label = ctk.CTkLabel(
            self.upload_slip_frame,
            text="ไฟล์ยังไม่ได้เลือก",
            font=ctk.CTkFont(size=12, italic=True),
            text_color="gray50",
            anchor="w"
        )
        self.slip_filename_label.grid(row=0, column=1, sticky="w")
        # ^^^^ สิ้นสุดส่วน QR Code และแนบสลิป ^^^^
        
        radio2 = ctk.CTkRadioButton(
            payment_frame,
            text="📦 เก็บเงินปลายทาง (COD)",
            variable=self.payment_var,
            value="เก็บเงินปลายทาง",
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio2.pack(anchor="w", padx=25, pady=8)

    def select_slip_image(self):
        """เปิด Dialog เลือกไฟล์สลิป"""
        filetypes = [("Image files", "*.png *.jpg *.jpeg")]
        filepath = filedialog.askopenfilename(title="เลือกไฟล์สลิปการโอนเงิน", filetypes=filetypes)
        
        if filepath:
            self.uploaded_slip_path = filepath
            filename = os.path.basename(filepath)
            self.slip_filename_label.configure(text=filename, text_color="#4CAF50")
        else:
            self.uploaded_slip_path = None
            self.slip_filename_label.configure(text="ไฟล์ยังไม่ได้เลือก", text_color="gray50")
        
        self.update_confirm_button_state() # อัปเดตสถานะปุ่มยืนยัน

    def update_payment_ui(self):
        """แสดง/ซ่อนรายละเอียดการโอนเงินตามที่เลือก"""
        if self.payment_var.get() == "โอนเงินผ่านธนาคาร":
            self.bank_transfer_detail_frame.pack(fill="x", padx=25, pady=(5, 8))
        else:
            self.bank_transfer_detail_frame.pack_forget()
            
        self.update_confirm_button_state()

    def update_confirm_button_state(self):
        """อัปเดตสถานะปุ่มยืนยันคำสั่งซื้อ"""
        confirm_btn = self.get_confirm_button()
        if not confirm_btn:
            return

        can_confirm = True
        
        # 1. ตรวจสอบตะกร้าและที่อยู่
        if not self.cart.get_items() or not self.session.current_user.address:
            can_confirm = False
        
        # 2. ตรวจสอบสลิป (ถ้าเลือกโอนเงิน)
        if self.payment_var.get() == "โอนเงินผ่านธนาคาร":
            if not self.uploaded_slip_path:
                can_confirm = False

        confirm_btn.configure(state="normal" if can_confirm else "disabled")

    def get_confirm_button(self):
        """ค้นหาและคืนค่าปุ่มยืนยันคำสั่งซื้อ"""
        # (หาปุ่มยืนยันใน total_container)
        for widget in self.winfo_children():
            if isinstance(widget, ctk.CTkFrame) and widget.grid_info().get('column') == 1:
                right_panel = widget
                for sub_widget in right_panel.winfo_children():
                    if isinstance(sub_widget, ctk.CTkFrame) and sub_widget.winfo_name() == "!ctkframe3": # หา total_container
                        total_container = sub_widget
                        for btn in total_container.winfo_children():
                            if isinstance(btn, ctk.CTkButton) and btn.cget("text") == "✅ ยืนยันคำสั่งซื้อ":
                                return btn
        return None

    def create_summary_panel(self, parent):
        """สร้าง Panel สรุปรายการสินค้าและยอดรวม (เหมือนเดิม)"""
        # ... (โค้ดสร้าง Panel สรุปรายการสินค้าและยอดรวมเหมือนเดิม) ...

        # Header
        summary_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        summary_header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            summary_header,
            text="🛍️ สรุปรายการสินค้า",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)

        # Items List
        items_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        for item in self.cart.get_items():
            item_card = ctk.CTkFrame(items_frame, fg_color="#FFF0F5", corner_radius=10)
            item_card.pack(fill="x", pady=5)
            
            item_info = ctk.CTkFrame(item_card, fg_color="transparent")
            item_info.pack(fill="x", padx=15, pady=10)
            
            ctk.CTkLabel(
                item_info,
                text=f"• {item.product.name}",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6D4C41",
                anchor="w"
            ).pack(side="left")
            
            ctk.CTkLabel(
                item_info,
                text=f"x{item.quantity}",
                font=ctk.CTkFont(size=12),
                text_color="#FFB6C1",
                anchor="e"
            ).pack(side="right", padx=10)
            
            ctk.CTkLabel(
                item_info,
                text=item.format_total_price(),
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#FF6B9D",
                anchor="e"
            ).pack(side="right")

        # Total Section
        total_container = ctk.CTkFrame(parent, fg_color="transparent")
        total_container.pack(side="bottom", fill="x", padx=20, pady=20)
        
        # Separator
        ctk.CTkFrame(total_container, height=2, fg_color="#FFEBEE").pack(fill="x", pady=15)
        
        total_frame = ctk.CTkFrame(total_container, fg_color="#FFE4E1", corner_radius=15)
        total_frame.pack(fill="x", pady=(0, 15))
        
        total_inner = ctk.CTkFrame(total_frame, fg_color="transparent")
        total_inner.pack(fill="x", padx=20, pady=15)
        
        ctk.CTkLabel(
            total_inner,
            text="ยอดสุทธิ:",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(side="left")
        
        ctk.CTkLabel(
            total_inner,
            text=self.cart.format_total_price(),
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF6B9D"
        ).pack(side="right")
        
        # Confirm Button
        confirm_btn = ctk.CTkButton(
            total_container,
            text="✅ ยืนยันคำสั่งซื้อ",
            command=self.place_order,
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=18, weight="bold"),
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            text_color="white"
        )
        confirm_btn.pack(fill="x")

        # เรียกอัปเดตสถานะปุ่มครั้งแรก
        self.update_confirm_button_state()

    def place_order(self):
        """ดำเนินการสร้างคำสั่งซื้อ"""
        user = self.session.current_user
        cart_items = self.cart.get_items()
        total_price = self.cart.get_total_price()
        payment_method = self.payment_var.get()
        shipping_address = user.address
        slip_filename = None

        if not cart_items:
            messagebox.showwarning("ผิดพลาด", "ตะกร้าสินค้าของคุณว่างเปล่า", parent=self)
            return
        if not shipping_address:
            messagebox.showwarning("ผิดพลาด", "กรุณาเพิ่มที่อยู่สำหรับจัดส่งในหน้าโปรไฟล์ก่อน", parent=self)
            return

        # VVVV จัดการไฟล์สลิป VVVV
        if payment_method == "โอนเงินผ่านธนาคาร":
            if not self.uploaded_slip_path:
                messagebox.showwarning("ผิดพลาด", "กรุณาแนบสลิปโอนเงินก่อนยืนยันคำสั่งซื้อ", parent=self)
                return
            
            # บันทึกไฟล์สลิป
            try:
                # สร้างชื่อไฟล์ที่ไม่ซ้ำกัน
                ext = os.path.splitext(self.uploaded_slip_path)[1]
                # ใช้ user_id และ timestamp
                slip_filename = f"slip_{user.user_id}_{int(time.time())}{ext}" 
                
                # Path สำหรับบันทึก
                SLIP_DIR = "assets/slips"
                if not os.path.exists(SLIP_DIR):
                    os.makedirs(SLIP_DIR)
                    
                dest_path = os.path.join(SLIP_DIR, slip_filename)
                
                # คัดลอกไฟล์ (ใช้ shutil.copy หรือ os.rename) - ที่นี่ใช้ os.rename/copy
                from shutil import copyfile
                copyfile(self.uploaded_slip_path, dest_path)
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกไฟล์สลิปได้: {e}", parent=self)
                return
        # ^^^^ สิ้นสุดส่วนจัดการไฟล์สลิป ^^^^

        try:
            order_id = self.db.create_order(
                user_id=user.user_id,
                total_amount=total_price,
                items=cart_items,
                payment_method=payment_method,
                shipping_address=shipping_address,
                slip_image_filename=slip_filename # <--- ส่งชื่อไฟล์สลิปเข้า DB
            )
            if order_id:
                self.cart.clear()
                self.main_app.navigate_to('ThankYouWindow', order_id=order_id)
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างคำสั่งซื้อได้", parent=self)
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}", parent=self)