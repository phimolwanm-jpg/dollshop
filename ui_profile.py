import customtkinter as ctk
from tkinter import messagebox
import bcrypt

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน Lavender Blush
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        # ล้าง UI เก่าทิ้งทั้งหมดก่อนสร้างใหม่
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมด"""

        # vvvv  (สำคัญ) โค้ดที่แก้ไข/เพิ่มเข้าไป vvvv
        # ตรวจสอบก่อนว่าล็อกอินหรือยัง
        if not self.session.current_user:
            # ถ้ายังไม่ล็อกอิน (current_user เป็น None)
            self.grid_columnconfigure(0, weight=1) # กำหนดค่า grid ก่อน
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
            return # <--- (สำคัญมาก) หยุดการทำงานทันที ไม่สร้าง UI ที่เหลือ
        # ^^^^  สิ้นสุดโค้ดที่เพิ่ม ^^^^

        # --- (โค้ดเดิมของคุณ) ---
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
        """สร้าง Panel สำหรับแก้ไขข้อมูลส่วนตัว"""
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

        fields = {
            "full_name": "ชื่อ-นามสกุล:", 
            "email": "อีเมล:", 
            "phone": "เบอร์โทรศัพท์:", 
            "address": "ที่อยู่สำหรับจัดส่ง:"
        }
        self.profile_entries = {}
        
        # เราตรวจสอบแล้วใน setup_ui ว่า user ไม่ใช่ None
        user = self.session.current_user
        
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
        """สร้าง Panel สำหรับเปลี่ยนรหัสผ่าน"""
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
            "confirm_password": "ยืนยืนรหัสผ่านใหม่:"
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

    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวที่แก้ไข"""
        # (ตรวจสอบอีกครั้งเผื่อไว้)
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ", parent=self)
            return

        full_name = self.profile_entries['full_name'].get().strip()
        phone = self.profile_entries['phone'].get().strip()
        address = self.profile_entries['address'].get("1.0", "end-1c").strip()

        if not full_name:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล", parent=self)
            return

        user_id = self.session.current_user.user_id
        if self.db.update_user_profile(user_id, full_name, phone, address):
            # อัปเดตข้อมูลใน session ด้วย
            self.session.current_user.full_name = full_name
            self.session.current_user.phone = phone
            self.session.current_user.address = address
            messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว", parent=self)
            self.on_show() # รีเฟรชหน้า
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลได้", parent=self)

    def change_password(self):
        """เปลี่ยนรหัสผ่าน"""
        # (ตรวจสอบอีกครั้งเผื่อไว้)
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
        
        # (หมายเหตุ: โค้ดนี้จะใช้ได้ถ้าคุณแก้ database.py ให้ใช้ bcrypt ด้วย)
        # (ถ้ายังใช้รหัสผ่านแบบข้อความธรรมดา ให้เปลี่ยนเป็น:
        # if not user_data or user_data['password'] != current_pass: )
        
        # สมมติว่าใน database.py ยังเป็นข้อความธรรมดา
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