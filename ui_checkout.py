import customtkinter as ctk
from tkinter import messagebox, filedialog
import os # Import os เพื่อใช้งาน Path
import time
from PIL import Image
from models import Session, Cart
from database import Database
from shutil import copyfile

class CheckoutWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.session = main_app.session
        self.cart = main_app.cart
        self.db = main_app.db
        
        # ตัวแปรสำหรับเก็บ widget หรือ path ที่ต้องใช้ภายหลัง
        self.edit_window = None
        self.uploaded_slip_path = None
        self.slip_filename_label = None 
        self.confirm_btn = None
        
       
        # หา Path ของโฟลเดอร์ปัจจุบันที่ไฟล์ ui_checkout.py อยู่
        BASE_DIR = os.path.abspath(os.path.dirname(__file__)) 
        
        # กำหนด Path รูปภาพหลัก (ใช้ os.path.join)
        self.QR_PATH = os.path.join(BASE_DIR, "assets", "qr_code.jpg") 
        
        # กำหนด Path โฟลเดอร์สลิป
        self.SLIP_DIR = os.path.join(BASE_DIR, "assets", "slips")
        # ----------------------------------------------------

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        # รีเซ็ตตัวแปรเมื่อเข้าหน้านี้
        self.uploaded_slip_path = None
        
        # ลบ widget เก่าทั้งหมดทิ้ง (เพื่อสร้างใหม่ด้วยข้อมูลล่าสุด)
        for widget in self.winfo_children():
            widget.destroy()
            
        # สร้าง UI และอัปเดตข้อมูลใหม่
        self.setup_ui()
        self.update_payment_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมด"""
        self.grid_columnconfigure(0, weight=2)
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
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
        """สร้าง Panel ที่อยู่และวิธีการชำระเงิน"""
        parent.pack_propagate(False)
        
        # Shipping Address Section 
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
        
        
        user = self.session.current_user
        if user and user.address:
            # ถ้ามี user และมีที่อยู่
            address_text = user.address
        else:
            # ถ้าไม่มี user หรือ user ไม่มีที่อยู่
            address_text = "⚠️ ยังไม่มีที่อยู่\nกรุณาเพิ่มในหน้าโปรไฟล์"
        # ----------------------------------------------------
        
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
        
        # Payment Method Section 
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
        # .trace_add จะคอย 'ดักฟัง' การเปลี่ยนแปลงของตัวแปรนี้
        # ถ้ามีการ 'write' (เปลี่ยนแปลง) ให้เรียกฟังก์ชัน self.update_payment_ui
        self.payment_var.trace_add("write", lambda name, index, mode: self.update_payment_ui())
        
        radio1 = ctk.CTkRadioButton(
            payment_frame,
            text="🏦 โอนเงินผ่านธนาคาร/พร้อมเพย์ (พร้อมแนบสลิป)",
            variable=self.payment_var, # ผูกกับตัวแปร
            value="โอนเงินผ่านธนาคาร",   # ค่าเมื่อถูกเลือก
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio1.pack(anchor="w", padx=25, pady=8)
        
        # ส่วน QR Code และแนบสลิป (จะถูกซ่อน/แสดง)
        self.bank_transfer_detail_frame = ctk.CTkFrame(payment_frame, fg_color="#FFF0F5", corner_radius=10, border_width=1, border_color="#FFEBEE")
        
        # QR Code Section
        qr_code_frame = ctk.CTkFrame(self.bank_transfer_detail_frame, fg_color="transparent")
        qr_code_frame.pack(side="left", padx=15, pady=10, fill="y")
        
        # Load QR Code Image
        try:
            # 💡 การใช้ self.QR_PATH ที่ถูกแก้ไขแล้ว จะทำให้หาไฟล์เจอแน่นอน
            qr_img = Image.open(self.QR_PATH).resize((180, 180), Image.LANCZOS)
            self.qr_ctk_img = ctk.CTkImage(qr_img, size=(180, 180))
            ctk.CTkLabel(qr_code_frame, image=self.qr_ctk_img, text="").pack(pady=5)
        except FileNotFoundError:
             ctk.CTkLabel(qr_code_frame, text="[QR Code ไม่พบ]", text_color="#F44336").pack(pady=5)
        except Exception:
             ctk.CTkLabel(qr_code_frame, text="[โหลดรูป QR Code ผิดพลาด]", text_color="#F44336").pack(pady=5)

        # Bank Info Text (ข้อมูลพร้อมเพย์)
        bank_info_text = ctk.CTkFrame(self.bank_transfer_detail_frame, fg_color="transparent")
        bank_info_text.pack(side="left", padx=15, pady=10, fill="both", expand=True)

        ctk.CTkLabel(
            bank_info_text,
            text="📱 พร้อมเพย์: 09X-XXX-XXXX\nธนาคารที่ผูก: กสิกรไทย\nชื่อบัญชี: Dollie Shop",
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

        # เก็บ Label นี้ไว้ใน self. เพื่อให้ฟังก์ชันอื่นอัปเดตข้อความได้
        self.slip_filename_label = ctk.CTkLabel(
            self.upload_slip_frame,
            text="ไฟล์ยังไม่ได้เลือก",
            font=ctk.CTkFont(size=12, slant="italic"), 
            text_color="gray50",
            anchor="w"
        )
        self.slip_filename_label.grid(row=0, column=1, sticky="w")
        
        radio2 = ctk.CTkRadioButton(
            payment_frame,
            text="📦 เก็บเงินปลายทาง (COD)",
            variable=self.payment_var, # ผูกกับตัวแปรเดียวกัน
            value="เก็บเงินปลายทาง",     # ค่าเมื่อถูกเลือก
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
            # ถ้าผู้ใช้เลือกไฟล์
            self.uploaded_slip_path = filepath
            filename = os.path.basename(filepath) # เอาเฉพาะชื่อไฟล์
            self.slip_filename_label.configure(text=filename, text_color="#4CAF50")
        else:
            # ถ้าผู้ใช้กดยกเลิก
            self.uploaded_slip_path = None
            self.slip_filename_label.configure(text="ไฟล์ยังไม่ได้เลือก", text_color="gray50")
        
        # อัปเดตสถานะปุ่มทุกครั้งที่เลือก (หรือยกเลิก) ไฟล์
        self.update_confirm_button_state()

    def update_payment_ui(self):
        """แสดง/ซ่อนรายละเอียดการโอนเงินตามที่เลือก"""
        if self.payment_var.get() == "โอนเงินผ่านธนาคาร":
            # ถ้าเลือกโอนเงิน -> 'แสดง' กรอบโอนเงิน
            self.bank_transfer_detail_frame.pack(fill="x", padx=25, pady=(5, 8))
        else:
            # ถ้าเลือกอย่างอื่น (COD) -> 'ซ่อน' กรอบโอนเงิน
            self.bank_transfer_detail_frame.pack_forget()
            
        # อัปเดตสถานะปุ่มทุกครั้งที่เปลี่ยนวิธีชำระเงิน
        self.update_confirm_button_state()

    def update_confirm_button_state(self):
        """อัปเดตสถานะปุ่มยืนยันคำสั่งซื้อ (กดได้/ไม่ได้)"""
        if not self.confirm_btn:
            # ถ้าปุ่มยังไม่ถูกสร้าง (เช่น ตอนเปิดแอปครั้งแรก) ก็ไม่ต้องทำอะไร
            return

        # ----------------------------------------------------
        # ตรวจสอบเงื่อนไขให้ชัดเจน
        # ----------------------------------------------------
        
        # 1. ตรวจสอบที่อยู่
        user_address = self.session.current_user.address if self.session.current_user else None
        has_address = bool(user_address) # True ถ้ามีที่อยู่, False ถ้าไม่มี
        
        # 2. ตรวจสอบว่ามีของในตะกร้า
        has_items = bool(self.cart.get_items()) # True ถ้ามีของ, False ถ้าตะกร้าว่าง
        
        # 3. ตรวจสอบสลิป (เฉพาะเมื่อเลือกโอนเงิน)
        payment_method = self.payment_var.get()
        slip_ok = True # ตั้งค่าเริ่มต้นว่า 'ผ่าน'
        
        if payment_method == "โอนเงินผ่านธนาคาร":
            # ถ้าเลือกโอนเงิน 'สลิปจะโอเค' ก็ต่อเมื่อ 'มีการอัปโหลดสลิปแล้ว'
            slip_ok = bool(self.uploaded_slip_path)
        
        # สรุปเงื่อนไข: ปุ่มจะกดได้ (normal)
        # ต่อเมื่อ: มีของ(has_items) AND มีที่อยู่(has_address) AND สลิปโอเค(slip_ok)
        
        can_confirm = has_items and has_address and slip_ok
        
        if can_confirm:
            self.confirm_btn.configure(state="normal")
        else:
            self.confirm_btn.configure(state="disabled")
        # ----------------------------------------------------

    def create_summary_panel(self, parent):
        """สร้าง Panel สรุปรายการสินค้าและยอดรวม"""
        # Header
        summary_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        summary_header.pack(fill="x", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            summary_header,
            text="🛍️ สรุปรายการสินค้า",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)

        # Items List (ใช้ ScrollableFrame เผื่อของเยอะ)
        items_frame = ctk.CTkScrollableFrame(
            parent,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        items_frame.pack(fill="both", expand=True, padx=20, pady=10)

        # วนลูปสร้าง 'การ์ด' ของสินค้าแต่ละชิ้นในตะกร้า
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
        
        # Separator (เส้นคั่น)
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
        
        # เก็บ reference ของปุ่ม Confirm ไว้ใน self.confirm_btn
        # เพื่อให้ฟังก์ชัน update_confirm_button_state เรียกใช้ได้
        self.confirm_btn = ctk.CTkButton(
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
        self.confirm_btn.pack(fill="x")

        # เรียกอัปเดตสถานะปุ่มครั้งแรก (ตอนที่หน้าเพิ่งโหลด)
        self.update_confirm_button_state()

    def place_order(self):
        """ดำเนินการสร้างคำสั่งซื้อ (เมื่อกดยืนยัน)"""
        user = self.session.current_user
        
        # ----------------------------------------------------
        # ตรวจสอบ user ก่อน เพื่อความปลอดภัย
        # ----------------------------------------------------
        if not user:
            messagebox.showerror("ผิดพลาด", "ไม่พบข้อมูลผู้ใช้ กรุณาล็อกอินใหม่", parent=self)
            return
            
        cart_items = self.cart.get_items()
        total_price = self.cart.get_total_price()
        payment_method = self.payment_var.get()
        shipping_address = user.address
        slip_filename = None # ชื่อไฟล์สลิปที่จะบันทึกลง DB (ถ้ามี)

        # --- 1. ตรวจสอบความพร้อม (Validation) ---
        if not cart_items:
            messagebox.showwarning("ผิดพลาด", "ตะกร้าสินค้าของคุณว่างเปล่า", parent=self)
            return # หยุดการทำงาน
        if not shipping_address:
            messagebox.showwarning("ผิดพลาด", "กรุณาเพิ่มที่อยู่สำหรับจัดส่งในหน้าโปรไฟล์ก่อน", parent=self)
            return # หยุดการทำงาน

        # --- 2. จัดการไฟล์สลิป (ถ้าเลือกโอนเงิน) ---
        if payment_method == "โอนเงินผ่านธนาคาร":
            if not self.uploaded_slip_path:
                messagebox.showwarning("ผิดพลาด", "กรุณาแนบสลิปโอนเงินก่อนยืนยันคำสั่งซื้อ", parent=self)
                return # หยุดการทำงาน
            
            # บันทึกไฟล์สลิป
            try:
                # สร้างชื่อไฟล์ใหม่ที่ไม่ซ้ำกัน
                ext = os.path.splitext(self.uploaded_slip_path)[1] # .png, .jpg
                # ใช้ user_id + เวลา (timestamp) เพื่อกันชื่อซ้ำ
                slip_filename = f"slip_{user.user_id}_{int(time.time())}{ext}" 
                
                # 💡 ใช้ self.SLIP_DIR ที่กำหนดไว้ตอน __init__
                if not os.path.exists(self.SLIP_DIR):
                    os.makedirs(self.SLIP_DIR) # สร้างโฟลเดอร์ถ้ายังไม่มี
                    
                dest_path = os.path.join(self.SLIP_DIR, slip_filename)
                
                # คัดลอกไฟล์ จากที่ผู้ใช้เลือก (source) ไปยังที่ที่เราเก็บ (destination)
                copyfile(self.uploaded_slip_path, dest_path)
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกไฟล์สลิปได้: {e}", parent=self)
                return # หยุดการทำงาน

        # --- 3. บันทึกคำสั่งซื้อลง Database ---
        try:
            order_id = self.db.create_order(
                user_id=user.user_id,
                total_amount=total_price,
                items=cart_items,
                payment_method=payment_method,
                shipping_address=shipping_address,
                slip_image_filename=slip_filename # จะเป็น None ถ้าเป็น COD
            )
            
            if order_id:
                # ถ้าสำเร็จ
                self.cart.clear() # ล้างตะกร้า
                # ไปหน้าขอบคุณ
                self.main_app.navigate_to('ThankYouWindow', order_id=order_id)
            else:
                # ถ้า db.create_order คืนค่ามาเป็น None (ไม่สำเร็จ)
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างคำสั่งซื้อได้", parent=self)
                
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดขณะบันทึกคำสั่งซื้อ: {e}", parent=self)