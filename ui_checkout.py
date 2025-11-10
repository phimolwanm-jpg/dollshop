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
        
        # ### <<< เพิ่มใหม่ >>> ###
        # ตัวแปรสำหรับเก็บช่องกรอกข้อมูลที่อยู่
        self.entry_name = None
        self.entry_phone = None
        self.entry_address = None
        # ### <<< จบส่วนที่เพิ่ม >>> ###
       
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
        
        # ### <<< เพิ่มใหม่ >>> ###
        # ดึงข้อมูลโปรไฟล์มาใส่ในช่องกรอกโดยอัตโนมัติ
        self.load_profile_data() 
        # ### <<< จบส่วนที่เพิ่ม >>> ###
        
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
        
        # ### <<< แก้ไข >>> ### (เรียกใช้ฟังก์ชันที่แก้ไขแล้ว)
        self.create_shipping_payment_panel(left_panel)
        
        # --- Right Panel ---
        right_panel = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        right_panel.grid(row=1, column=1, sticky="nsew", padx=(10, 30), pady=10)
        self.create_summary_panel(right_panel)

    def create_shipping_payment_panel(self, parent):
        """สร้าง Panel ที่อยู่และวิธีการชำระเงิน"""
        parent.grid_columnconfigure(0, weight=1) # ### <<< เพิ่มใหม่ >>> ###
        
        # Shipping Address Section 
        shipping_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        # ### <<< แก้ไข >>> ### (ใช้ .grid แทน .pack)
        shipping_header.grid(row=0, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            shipping_header,
            text="📦 กรอกข้อมูลจัดส่ง", # ### <<< แก้ไข >>> ###
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15, padx=20)
        
        # ### <<< เพิ่มใหม่ >>> ###
        # --- กรอบสำหรับปุ่มดึงข้อมูล ---
        load_btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        load_btn_frame.grid(row=1, column=0, sticky="e", padx=20, pady=(0, 5))
        
        load_btn = ctk.CTkButton(
            load_btn_frame,
            text="ดึงข้อมูลจากโปรไฟล์",
            command=self.load_profile_data,
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            border_width=1,
            border_color="#FFB6C1",
            corner_radius=10,
            font=ctk.CTkFont(size=12)
        )
        load_btn.pack()
        
        # --- กรอบสำหรับช่องกรอกข้อมูล ---
        address_frame = ctk.CTkFrame(parent, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        address_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        address_frame.grid_columnconfigure(1, weight=1) # ให้ช่องกรอกขยาย
        
        # 1. ชื่อ-นามสกุล
        ctk.CTkLabel(address_frame, text="ชื่อ-นามสกุล ผู้รับ:", font=ctk.CTkFont(size=14)).grid(row=0, column=0, padx=10, pady=(15, 5), sticky="e")
        self.entry_name = ctk.CTkEntry(address_frame, font=ctk.CTkFont(size=14))
        self.entry_name.grid(row=0, column=1, padx=(0, 20), pady=(15, 5), sticky="ew")
        
        # 2. เบอร์โทร
        ctk.CTkLabel(address_frame, text="เบอร์โทรศัพท์:", font=ctk.CTkFont(size=14)).grid(row=1, column=0, padx=10, pady=5, sticky="e")
        self.entry_phone = ctk.CTkEntry(address_frame, font=ctk.CTkFont(size=14))
        self.entry_phone.grid(row=1, column=1, padx=(0, 20), pady=5, sticky="ew")
        
        # 3. ที่อยู่
        ctk.CTkLabel(address_frame, text="ที่อยู่จัดส่ง:", font=ctk.CTkFont(size=14)).grid(row=2, column=0, padx=10, pady=5, sticky="ne")
        self.entry_address = ctk.CTkTextbox(address_frame, font=ctk.CTkFont(size=14), height=100)
        self.entry_address.grid(row=2, column=1, padx=(0, 20), pady=(5, 15), sticky="ew")
        
        # ผูก event ให้ปุ่มยืนยันอัปเดต เมื่อมีการพิมพ์
        self.entry_name.bind("<KeyRelease>", self.update_confirm_button_state)
        self.entry_phone.bind("<KeyRelease>", self.update_confirm_button_state)
        self.entry_address.bind("<KeyRelease>", self.update_confirm_button_state)
        # ### <<< จบส่วนที่เพิ่ม/แก้ไข >>> ###
        
        # Payment Method Section 
        payment_header = ctk.CTkFrame(parent, fg_color="#FFE4E1", corner_radius=15)
        # ### <<< แก้ไข >>> ### (ใช้ .grid แทน .pack)
        payment_header.grid(row=3, column=0, sticky="ew", padx=20, pady=(20, 10))
        ctk.CTkLabel(
            payment_header,
            text="💰 วิธีการชำระเงิน",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15, padx=20)
        
        # Payment Options
        payment_frame = ctk.CTkFrame(parent, fg_color="transparent")
        # ### <<< แก้ไข >>> ### (ใช้ .grid แทน .pack)
        payment_frame.grid(row=4, column=0, sticky="ew", padx=20, pady=10)
        
        self.payment_var = ctk.StringVar(value="โอนเงินผ่านธนาคาร")
        self.payment_var.trace_add("write", lambda n, i, m: self.update_payment_ui())
        
        radio1 = ctk.CTkRadioButton(
            payment_frame,
            text="🏦 โอนเงินผ่านธนาคาร/พร้อมเพย์ (พร้อมแนบสลิป)",
            variable=self.payment_var, 
            value="โอนเงินผ่านธนาคาร",   
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB"
        )
        radio1.pack(anchor="w", padx=25, pady=8)
        
        # ส่วน QR Code และแนบสลิป (จะถูกซ่อน/แสดง)
        self.bank_transfer_detail_frame = ctk.CTkFrame(payment_frame, fg_color="#FFF0F5", corner_radius=10, border_width=1, border_color="#FFEBEE")
        
        qr_code_frame = ctk.CTkFrame(self.bank_transfer_detail_frame, fg_color="transparent")
        qr_code_frame.pack(side="left", padx=15, pady=10, fill="y")
        
        try:
            qr_img = Image.open(self.QR_PATH).resize((180, 180), Image.LANCZOS)
            self.qr_ctk_img = ctk.CTkImage(qr_img, size=(180, 180))
            ctk.CTkLabel(qr_code_frame, image=self.qr_ctk_img, text="").pack(pady=5)
        except FileNotFoundError:
             ctk.CTkLabel(qr_code_frame, text="[QR Code ไม่พบ]", text_color="#F44336").pack(pady=5)
        except Exception:
             ctk.CTkLabel(qr_code_frame, text="[โหลดรูป QR Code ผิดพลาด]", text_color="#F44336").pack(pady=5)

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
            font=ctk.CTkFont(size=12, slant="italic"), 
            text_color="gray50",
            anchor="w"
        )
        self.slip_filename_label.grid(row=0, column=1, sticky="w")
        
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

    # ### <<< เพิ่มใหม่ >>> ###
    def load_profile_data(self):
        """ดึงข้อมูลจากโปรไฟล์มาใส่ในช่องกรอก"""
        user = self.session.current_user
        if not user:
            return # ถ้าไม่มี user (เช่น guest) ก็ไม่ต้องทำอะไร
            
        # เคลียร์ข้อมูลเก่า (ถ้ามี)
        self.entry_name.delete(0, "end")
        self.entry_phone.delete(0, "end")
        self.entry_address.delete("1.0", "end")
        
        # ใส่ข้อมูลใหม่จากโปรไฟล์
        if user.full_name:
            self.entry_name.insert(0, user.full_name)
        if user.phone:
            self.entry_phone.insert(0, user.phone)
        if user.address:
            self.entry_address.insert("1.0", user.address)
            
        # อัปเดตสถานะปุ่มหลังจากดึงข้อมูล
        self.update_confirm_button_state()

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
        
        self.update_confirm_button_state(event=None) # ### <<< แก้ไข >>> ### (เรียกใช้)

    def update_payment_ui(self):
        """แสดง/ซ่อนรายละเอียดการโอนเงินตามที่เลือก"""
        if self.payment_var.get() == "โอนเงินผ่านธนาคาร":
            self.bank_transfer_detail_frame.pack(fill="x", padx=25, pady=(5, 8))
        else:
            self.bank_transfer_detail_frame.pack_forget()
            
        self.update_confirm_button_state(event=None) # ### <<< แก้ไข >>> ### (เรียกใช้)

    # ### <<< แก้ไข >>> ### (เพิ่ม event=None เพื่อรับการเรียกใช้จาก .bind)
    def update_confirm_button_state(self, event=None):
        """อัปเดตสถานะปุ่มยืนยันคำสั่งซื้อ (กดได้/ไม่ได้)"""
        if not self.confirm_btn:
            return

        # 1. ตรวจสอบที่อยู่ (จากช่องกรอกใหม่)
        # (ต้องเช็คว่า widget ถูกสร้างแล้วหรือยัง)
        has_name = bool(self.entry_name and self.entry_name.get().strip())
        has_phone = bool(self.entry_phone and self.entry_phone.get().strip())
        has_address = bool(self.entry_address and self.entry_address.get("1.0", "end-1c").strip())
        
        # 2. ตรวจสอบว่ามีของในตะกร้า
        has_items = bool(self.cart.get_items()) 
        
        # 3. ตรวจสอบสลิป (เฉพาะเมื่อเลือกโอนเงิน)
        payment_method = self.payment_var.get()
        slip_ok = True 
        
        if payment_method == "โอนเงินผ่านธนาคาร":
            slip_ok = bool(self.uploaded_slip_path)
        
        # สรุปเงื่อนไข:
        # มีของ AND มีชื่อ AND มีเบอร์ AND มีที่อยู่ AND สลิปโอเค
        can_confirm = has_items and has_name and has_phone and has_address and slip_ok
        
        if can_confirm:
            self.confirm_btn.configure(state="normal")
        else:
            self.confirm_btn.configure(state="disabled")

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

        # เรียกอัปเดตสถานะปุ่มครั้งแรก
        self.update_confirm_button_state() # ### <<< แก้ไข >>> ### (ลบ event=None)

    def place_order(self):
        """ดำเนินการสร้างคำสั่งซื้อ (เมื่อกดยืนยัน)"""
        user = self.session.current_user
        
        if not user:
            messagebox.showerror("ผิดพลาด", "ไม่พบข้อมูลผู้ใช้ กรุณาล็อกอินใหม่", parent=self)
            return
            
        cart_items = self.cart.get_items()
        total_price = self.cart.get_total_price()
        payment_method = self.payment_var.get()
        slip_filename = None 

        # --- 1. ตรวจสอบความพร้อม (Validation) ---
        if not cart_items:
            messagebox.showwarning("ผิดพลาด", "ตะกร้าสินค้าของคุณว่างเปล่า", parent=self)
            return
            
        # ### <<< เพิ่มใหม่ >>> ###
        # --- ดึงข้อมูลจากช่องกรอก และตรวจสอบ ---
        buyer_name = self.entry_name.get().strip()
        buyer_phone = self.entry_phone.get().strip()
        buyer_address = self.entry_address.get("1.0", "end-1c").strip()
        
        if not buyer_name or not buyer_phone or not buyer_address:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอก ชื่อ, เบอร์โทร, และที่อยู่จัดส่ง ให้ครบถ้วน", parent=self)
            return
        # ### <<< จบส่วนที่เพิ่ม >>> ###

        # --- 2. จัดการไฟล์สลิป (ถ้าเลือกโอนเงิน) ---
        if payment_method == "โอนเงินผ่านธนาคาร":
            if not self.uploaded_slip_path:
                messagebox.showwarning("ผิดพลาด", "กรุณาแนบสลิปโอนเงินก่อนยืนยันคำสั่งซื้อ", parent=self)
                return
            
            try:
                ext = os.path.splitext(self.uploaded_slip_path)[1]
                slip_filename = f"slip_{user.user_id}_{int(time.time())}{ext}" 
                
                if not os.path.exists(self.SLIP_DIR):
                    os.makedirs(self.SLIP_DIR) 
                    
                dest_path = os.path.join(self.SLIP_DIR, slip_filename)
                
                copyfile(self.uploaded_slip_path, dest_path)
                
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกไฟล์สลิปได้: {e}", parent=self)
                return

        # --- 3. บันทึกคำสั่งซื้อลง Database ---
        try:
            # ### <<< แก้ไข >>> ### (ส่งข้อมูลที่กรอกใหม่เข้า DB)
            order_id = self.db.create_order(
                user_id=user.user_id,
                total_amount=total_price,
                items=cart_items,
                payment_method=payment_method,
                shipping_address=buyer_address, # ส่งที่อยู่ใหม่ไปช่อง legacy
                slip_image_filename=slip_filename,
                
                # ส่งข้อมูลใหม่ไปช่องที่ถูกต้อง
                buyer_name=buyer_name,
                buyer_phone=buyer_phone,
                buyer_address=buyer_address
            )
            # ### <<< จบส่วนที่แก้ไข >>> ###
            
            if order_id:
                self.cart.clear() 
                self.main_app.navigate_to('ThankYouWindow', order_id=order_id)
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างคำสั่งซื้อได้", parent=self)
                
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาดขณะบันทึกคำสั่งซื้อ: {e}", parent=self)