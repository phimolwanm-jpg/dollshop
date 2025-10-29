import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import os
from PIL import Image # ต้องติดตั้ง pip install Pillow
import time # ใช้สำหรับสร้างชื่อไฟล์ที่ไม่ซ้ำกัน

# กำหนด Path สำหรับเก็บรูปโปรไฟล์ (ต้องสร้างโฟลเดอร์นี้เอง)
PROFILE_IMG_DIR = "assets/profile_images"

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน Lavender Blush
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db
        self.new_image_file = None # เก็บ path ของไฟล์รูปภาพใหม่ชั่วคราว
        
        # ตรวจสอบและสร้างโฟลเดอร์สำหรับรูปโปรไฟล์
        if not os.path.exists(PROFILE_IMG_DIR):
            os.makedirs(PROFILE_IMG_DIR)

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมด"""
        
        # vvvv โค้ดตรวจสอบการล็อกอิน (แก้ไขแล้ว) vvvv
        if not self.session.current_user:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            
            warning_frame = ctk.CTkFrame(self, fg_color="transparent")
            warning_frame.pack(expand=True)
            
            ctk.CTkLabel(warning_frame, text="❌ คุณยังไม่ได้เข้าสู่ระบบ ❌", font=ctk.CTkFont(size=24, weight="bold"), text_color="#FF6B9D").pack(padx=50, pady=(100, 20))
            ctk.CTkButton(
                warning_frame, 
                text="ไปหน้าล็อกอิน", 
                command=lambda: self.main_app.navigate_to('LoginWindow'),
                font=ctk.CTkFont(size=16),
                fg_color="#FFB6C1",
                hover_color="#FFC0CB",
                text_color="white"
            ).pack(pady=10, ipady=5)
            return
        # ^^^^ สิ้นสุดโค้ดตรวจสอบ ^^^^

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text="👤 โปรไฟล์ของฉัน", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        ).pack(side="left", padx=30, pady=20)
        
        back_button = ctk.CTkButton(
            header_frame, 
            text="< กลับไปหน้าหลัก", 
            fg_color="transparent", 
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow')
        )
        back_button.pack(side="right", padx=30, pady=20)
        
        # --- Main Content Frame ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_profile_panel(content_frame)
        self.create_password_panel(content_frame)

    def create_profile_panel(self, parent):
        """สร้าง Panel สำหรับแก้ไขข้อมูลส่วนตัว (พร้อมช่องรูปโปรไฟล์)"""
        panel = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        panel.grid_columnconfigure(0, weight=1)

        # Header ของ Panel
        header = ctk.CTkFrame(panel, fg_color="#FFE4E1", corner_radius=15)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(
            header, 
            text="✨ ข้อมูลส่วนตัว", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)

        user = self.session.current_user
        row_counter = 1
        
        # --- (ส่วนที่เพิ่ม) รูปโปรไฟล์ ---
        ctk.CTkLabel(
            panel, 
            text="รูปโปรไฟล์:", 
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        ).grid(row=row_counter, column=0, padx=30, pady=(15, 5), sticky="w")
        
        img_frame = ctk.CTkFrame(panel, fg_color="transparent")
        img_frame.grid(row=row_counter + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
        img_frame.grid_columnconfigure(0, weight=1)
        
        # โหลดรูปภาพปัจจุบัน หรือ รูป Default
        self.current_img_path = user.profile_image_url if user.profile_image_url else 'assets/default_profile.png'
        
        try:
            # พยายามโหลดรูปภาพ
            img_full_path = os.path.join(PROFILE_IMG_DIR, self.current_img_path) if user.profile_image_url else self.current_img_path
            
            # ปรับขนาดรูปภาพให้พอดี
            self.profile_img = ctk.CTkImage(Image.open(img_full_path).resize((60, 60), Image.LANCZOS), size=(60, 60))
            
        except:
            # ถ้าโหลดไม่ได้ ให้ใช้รูป default ที่มีอยู่แล้ว (ต้องมี default_profile.png อยู่ใน assets)
            default_path = 'assets/default_profile.png'
            if os.path.exists(default_path):
                 self.profile_img = ctk.CTkImage(Image.open(default_path).resize((60, 60), Image.LANCZOS), size=(60, 60))
            else:
                 self.profile_img = ctk.CTkImage(Image.open(self.main_app.assets.get_image('default_icon')), size=(60, 60)) # fallback 

        self.img_label = ctk.CTkLabel(img_frame, image=self.profile_img, text="", compound="left")
        self.img_label.grid(row=0, column=0, sticky="w", padx=(0, 10))

        # ปุ่มเลือกรูป
        select_img_btn = ctk.CTkButton(
            img_frame, 
            text="🖼️ เลือกรูปภาพใหม่", 
            command=self.select_profile_image, 
            corner_radius=15,
            font=ctk.CTkFont(size=14),
            fg_color="#FFC0CB",
            hover_color="#FFB6C1",
            text_color="white"
        )
        select_img_btn.grid(row=0, column=1, sticky="w")
        
        row_counter += 2
        
        # --- (ส่วนของข้อมูลส่วนตัวที่เหลือ) ---
        fields = {
            "full_name": "ชื่อ-นามสกุล:", 
            "email": "อีเมล:", 
            "phone": "เบอร์โทรศัพท์:", 
            "address": "ที่อยู่สำหรับจัดส่ง:"
        }
        self.profile_entries = {}
        
        for key, label in fields.items():
            # Label
            ctk.CTkLabel(
                panel, 
                text=label, 
                font=ctk.CTkFont(size=14),
                text_color="#6D4C41"
            ).grid(row=row_counter, column=0, padx=30, pady=(15, 5), sticky="w")
            
            # Entry (แก้ไขให้ช่องที่อยู่ (address) ใช้ได้)
            if key == "address":
                entry = ctk.CTkTextbox(
                    panel, 
                    height=100, 
                    corner_radius=15,
                    border_width=1,
                    border_color="#FFEBEE",
                    fg_color="#FFF0F5",
                    font=ctk.CTkFont(size=14)
                )
                entry.insert("1.0", getattr(user, key) or "")
            else:
                entry = ctk.CTkEntry(
                    panel, 
                    height=45,
                    corner_radius=15,
                    border_width=1,
                    border_color="#FFEBEE",
                    fg_color="#FFF0F5",
                    font=ctk.CTkFont(size=14)
                )
                entry.insert(0, getattr(user, key) or "")
            
            # Email ไม่ให้แก้ไข
            if key == "email": 
                entry.configure(state="disabled", text_color="gray50")

            entry.grid(row=row_counter + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
            self.profile_entries[key] = entry
            row_counter += 2
            
        # ปุ่มบันทึก
        save_btn = ctk.CTkButton(
            panel, 
            text="💾 บันทึกข้อมูลส่วนตัว", 
            command=self.save_profile, 
            height=45,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white"
        )
        save_btn.grid(row=row_counter, column=0, sticky="ew", padx=30, pady=25)

    def create_password_panel(self, parent):
        """สร้าง Panel สำหรับเปลี่ยนรหัสผ่าน (โค้ดเดิม)"""
        panel = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        panel.grid_columnconfigure(0, weight=1)

        # Header ของ Panel
        header = ctk.CTkFrame(panel, fg_color="#FFE4E1", corner_radius=15)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(
            header, 
            text="🔒 เปลี่ยนรหัสผ่าน", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)
        
        fields = {
            "current_password": "รหัสผ่านปัจจุบัน:", 
            "new_password": "รหัสผ่านใหม่:", 
            "confirm_password": "ยืนยันรหัสผ่านใหม่:"
        }
        self.password_entries = {}

        row_counter = 1
        for key, label in fields.items():
            # Label
            ctk.CTkLabel(
                panel, 
                text=label, 
                font=ctk.CTkFont(size=14),
                text_color="#6D4C41"
            ).grid(row=row_counter, column=0, padx=30, pady=(15, 5), sticky="w")
            
            # Entry
            entry = ctk.CTkEntry(
                panel, 
                show="*",
                height=45,
                corner_radius=15,
                border_width=1,
                border_color="#FFEBEE",
                fg_color="#FFF0F5",
                font=ctk.CTkFont(size=14)
            )
            entry.grid(row=row_counter + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
            self.password_entries[key] = entry
            row_counter += 2
            
        # ปุ่มเปลี่ยนรหัสผ่าน
        change_btn = ctk.CTkButton(
            panel, 
            text="🔐 เปลี่ยนรหัสผ่าน", 
            command=self.change_password, 
            height=45,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B9D",
            hover_color="#FF8FB3",
            text_color="white"
        )
        change_btn.grid(row=row_counter, column=0, sticky="ew", padx=30, pady=25)
        
    def select_profile_image(self):
        """เปิด Dialog ให้ผู้ใช้เลือกรูปภาพ และแสดงตัวอย่าง"""
        filetypes = [("Image files", "*.png *.jpg *.jpeg")]
        filepath = filedialog.askopenfilename(title="เลือกรูปโปรไฟล์", filetypes=filetypes)
        
        if filepath:
            self.new_image_file = filepath
            
            # แสดงตัวอย่างรูปใหม่บน UI
            try:
                new_img = ctk.CTkImage(Image.open(filepath).resize((60, 60), Image.LANCZOS), size=(60, 60))
                self.img_label.configure(image=new_img)
                self.img_label.image = new_img # ป้องกันการถูกทำลายโดย garbage collector
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถโหลดรูปภาพได้: {e}", parent=self)
                self.new_image_file = None

    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวที่แก้ไข พร้อมจัดการรูปโปรไฟล์"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ", parent=self)
            return

        full_name = self.profile_entries['full_name'].get().strip()
        phone = self.profile_entries['phone'].get().strip()
        address = self.profile_entries['address'].get("1.0", "end-1c").strip()
        
        # 1. จัดการการอัปโหลดรูปภาพใหม่ (ถ้ามีการเลือกรูปใหม่)
        new_image_filename = self.session.current_user.profile_image_url # ใช้ชื่อไฟล์เดิมเป็นค่าเริ่มต้น

        if self.new_image_file:
            try:
                # 1.1 สร้างชื่อไฟล์ใหม่ที่ไม่ซ้ำกัน
                ext = os.path.splitext(self.new_image_file)[1]
                # ใช้ user_id และ timestamp เพื่อให้ชื่อไฟล์ไม่ซ้ำกัน
                new_image_filename = f"profile_{self.session.current_user.user_id}_{int(time.time())}{ext}" 
                
                # 1.2 คัดลอก/ย้ายไฟล์ไปยังโฟลเดอร์เก็บรูป
                dest_path = os.path.join(PROFILE_IMG_DIR, new_image_filename)
                
                img = Image.open(self.new_image_file)
                # บันทึกไฟล์ใหม่
                img.save(dest_path) 
                
                # 1.3 ลบไฟล์เก่าทิ้ง (ถ้ามี และไม่ใช่รูป default)
                old_filename = self.session.current_user.profile_image_url
                if old_filename and old_filename != 'default_profile.png':
                    old_path = os.path.join(PROFILE_IMG_DIR, old_filename)
                    if os.path.exists(old_path):
                        os.remove(old_path)
                        
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถบันทึกรูปภาพได้: {e}", parent=self)
                return

        if not full_name:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล", parent=self)
            return

        user_id = self.session.current_user.user_id
        
        # 2. อัปเดตข้อมูลในฐานข้อมูล (รวมถึงชื่อไฟล์รูปภาพ)
        if self.db.update_user_profile(user_id, full_name, phone, address, new_image_filename):
            # อัปเดตข้อมูลใน session ด้วย
            self.session.current_user.full_name = full_name
            self.session.current_user.phone = phone
            self.session.current_user.address = address
            self.session.current_user.profile_image_url = new_image_filename # อัปเดต URL รูปใหม่
            
            messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว", parent=self)
            self.new_image_file = None # ล้างค่าชั่วคราว
            self.on_show() # รีเฟรชหน้า
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลได้", parent=self)

    def change_password(self):
        """เปลี่ยนรหัสผ่าน (โค้ดเดิม)"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ", parent=self)
            return

        current_pass = self.password_entries['current_password'].get()
        new_pass = self.password_entries['new_password'].get()
        confirm_pass = self.password_entries['confirm_password'].get()

        if not all([current_pass, new_pass, confirm_pass]):
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกรหัสผ่านให้ครบทุกช่อง", parent=self)
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน", parent=self)
            return
        
        if len(new_pass) < 6:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร", parent=self)
            return
            
        user_id = self.session.current_user.user_id
        user_data = self.db.get_user_by_id(user_id)
        
        # สมมติว่าใน database.py ยังเป็นรหัสผ่านแบบข้อความธรรมดา (ตามโค้ดที่คุณส่ง)
        if not user_data or user_data['password'] != current_pass:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านปัจจุบันไม่ถูกต้อง", parent=self)
            return
            
        if self.db.update_user_password(user_id, new_pass):
            messagebox.showinfo("สำเร็จ", "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว", parent=self)
            # เคลียร์ช่องรหัสผ่าน
            for entry in self.password_entries.values():
                entry.delete(0, 'end')
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเปลี่ยนรหัสผ่านได้", parent=self)