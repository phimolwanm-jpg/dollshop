import customtkinter as ctk
from tkinter import messagebox
import bcrypt # Keep bcrypt for essential password checking

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน Lavender Blush
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db

        # --- vvvv Register the validation function vvvv ---
        # Register the validation command with Tkinter
        self.validate_phone_cmd = self.register(self.validate_phone_input)
        # --- ^^^^ End registration ^^^^ ---

        # สร้างหน้าจอ UI ทันที
        self.setup_ui()

    # --- vvvv Add the validation function vvvv ---
    def validate_phone_input(self, P):
        """
        Validation function for the phone entry.
        Allows only digits and enforces a maximum length of 10.
        P: The value the entry will have if the change is allowed.
        """
        # Allow empty string (for deleting characters)
        if P == "":
            return True
        # Check if the string contains only digits and length is <= 10
        if P.isdigit() and len(P) <= 10:
            return True
        else:
            # If not digits or too long, disallow the change
            # self.bell() # Optional: make a sound
            return False
    # --- ^^^^ End validation function ^^^^ ---

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Profile"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- 2. สร้างส่วนหัว (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)

        header_title = ctk.CTkLabel(
            header_frame, text="👤 โปรไฟล์ของฉัน",
            font=ctk.CTkFont(size=28, weight="bold"), text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)

        back_button = ctk.CTkButton(
            header_frame, text="< กลับไปหน้าหลัก", fg_color="transparent", text_color="#FFB6C1",
            hover_color="#FFE4E1", font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow')
        )
        back_button.pack(side="right", padx=30, pady=20)

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=1)

        # --- 4. สร้าง Panel ด้านซ้าย (ข้อมูลส่วนตัว) ---
        profile_panel = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        profile_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        profile_panel.grid_columnconfigure(0, weight=1)

        profile_panel_header = ctk.CTkFrame(profile_panel, fg_color="#FFE4E1", corner_radius=15)
        profile_panel_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        profile_panel_title = ctk.CTkLabel(
            profile_panel_header, text="✨ ข้อมูลส่วนตัว",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41"
        )
        profile_panel_title.pack(pady=15)

        # --- 4.2 สร้างช่องกรอกข้อมูล ---
        self.profile_entries = {}
        current_user_data = self.session.current_user

        # --- ช่องกรอก "ชื่อ-นามสกุล" ---
        label_fullname = ctk.CTkLabel(profile_panel, text="ชื่อ-นามสกุล:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_fullname.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_fullname = ctk.CTkEntry(profile_panel, height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_fullname.insert(0, getattr(current_user_data, 'full_name', "") or "")
        entry_fullname.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.profile_entries['full_name'] = entry_fullname

        # --- ช่องกรอก "อีเมล" (ห้ามแก้ไข) ---
        label_email = ctk.CTkLabel(profile_panel, text="อีเมล:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_email.grid(row=3, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_email = ctk.CTkEntry(profile_panel, height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_email.insert(0, getattr(current_user_data, 'email', "") or "")
        entry_email.configure(state="disabled", text_color="gray50")
        entry_email.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.profile_entries['email'] = entry_email

        # --- ช่องกรอก "เบอร์โทรศัพท์" ---
        label_phone = ctk.CTkLabel(profile_panel, text="เบอร์โทรศัพท์ (ตัวเลข 10 หลัก):", font=ctk.CTkFont(size=14), text_color="#6D4C41") # <--- Update Label
        label_phone.grid(row=5, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_phone = ctk.CTkEntry(
            profile_panel, height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14),
            # --- vvvv Add validation configuration vvvv ---
            validate="key", # Validate whenever a key is pressed
            validatecommand=(self.validate_phone_cmd, '%P') # Call validate_phone_input with the potential value (%P)
            # --- ^^^^ End validation configuration ^^^^ ---
        )
        entry_phone.insert(0, getattr(current_user_data, 'phone', "") or "")
        entry_phone.grid(row=6, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.profile_entries['phone'] = entry_phone

        # --- ช่องกรอก "ที่อยู่สำหรับจัดส่ง" (Textbox) ---
        label_address = ctk.CTkLabel(profile_panel, text="ที่อยู่สำหรับจัดส่ง:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_address.grid(row=7, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_address = ctk.CTkTextbox(profile_panel, height=100, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_address.insert("1.0", getattr(current_user_data, 'address', "") or "")
        entry_address.grid(row=8, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.profile_entries['address'] = entry_address

        # --- 4.3 ปุ่มบันทึกข้อมูลส่วนตัว ---
        save_profile_button = ctk.CTkButton(
            profile_panel, text="💾 บันทึกข้อมูลส่วนตัว", command=self.save_profile,
            height=45, corner_radius=15, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white"
        )
        save_profile_button.grid(row=9, column=0, sticky="ew", padx=30, pady=25)

        # --- 5. สร้าง Panel ด้านขวา (เปลี่ยนรหัสผ่าน) ---
        password_panel = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        password_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        password_panel.grid_columnconfigure(0, weight=1)

        password_panel_header = ctk.CTkFrame(password_panel, fg_color="#FFE4E1", corner_radius=15)
        password_panel_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")

        password_panel_title = ctk.CTkLabel(
            password_panel_header, text="🔒 เปลี่ยนรหัสผ่าน",
            font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41"
        )
        password_panel_title.pack(pady=15)

        # --- 5.2 สร้างช่องกรอกรหัสผ่าน ---
        self.password_entries = {}

        label_current_pass = ctk.CTkLabel(password_panel, text="รหัสผ่านปัจจุบัน:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_current_pass.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_current_pass = ctk.CTkEntry(password_panel, show="*", height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_current_pass.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.password_entries['current_password'] = entry_current_pass

        label_new_pass = ctk.CTkLabel(password_panel, text="รหัสผ่านใหม่:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_new_pass.grid(row=3, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_new_pass = ctk.CTkEntry(password_panel, show="*", height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_new_pass.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.password_entries['new_password'] = entry_new_pass

        label_confirm_pass = ctk.CTkLabel(password_panel, text="ยืนยันรหัสผ่านใหม่:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_confirm_pass.grid(row=5, column=0, padx=30, pady=(15, 5), sticky="w")
        entry_confirm_pass = ctk.CTkEntry(password_panel, show="*", height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        entry_confirm_pass.grid(row=6, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.password_entries['confirm_password'] = entry_confirm_pass

        # --- 5.3 ปุ่มเปลี่ยนรหัสผ่าน ---
        change_password_button = ctk.CTkButton(
            password_panel, text="🔐 เปลี่ยนรหัสผ่าน", command=self.change_password,
            height=45, corner_radius=15, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B9D", hover_color="#FF8FB3", text_color="white"
        )
        change_password_button.grid(row=7, column=0, sticky="ew", padx=30, pady=25)

    # --- (ลบฟังก์ชัน create_profile_panel และ create_password_panel) ---

    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวที่แก้ไข (Logic เดิม)"""
        full_name_input = self.profile_entries['full_name'].get().strip()
        phone_input = self.profile_entries['phone'].get().strip()
        address_input = self.profile_entries['address'].get("1.0", "end-1c").strip()

        # --- vvvv Add validation for phone number length before saving vvvv ---
        if phone_input and (not phone_input.isdigit() or len(phone_input) != 10):
             messagebox.showwarning("เบอร์โทรศัพท์ไม่ถูกต้อง", "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลข 10 หลัก", parent=self)
             return
        # --- ^^^^ End phone validation ^^^^ ---

        if not full_name_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล", parent=self)
            return

        current_user_id = self.session.current_user.user_id
        update_success = self.db.update_user_profile(current_user_id, full_name_input, phone_input, address_input)

        if update_success:
            self.session.current_user.full_name = full_name_input
            self.session.current_user.phone = phone_input
            self.session.current_user.address = address_input
            messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว", parent=self)
            self.on_show()
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลส่วนตัวได้ โปรดลองอีกครั้ง", parent=self)

    def change_password(self):
        """เปลี่ยนรหัสผ่าน (Logic เดิม)"""
        current_password_input = self.password_entries['current_password'].get()
        new_password_input = self.password_entries['new_password'].get()
        confirm_password_input = self.password_entries['confirm_password'].get()

        if not current_password_input or not new_password_input or not confirm_password_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกรหัสผ่านให้ครบทุกช่อง", parent=self)
            return
        if new_password_input != confirm_password_input:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน", parent=self)
            return
        # You might want to reuse the password validation logic from ui_login here if needed
        if len(new_password_input) < 8: # Assuming 8 characters min based on ui_login
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่ต้องมีอย่างน้อย 8 ตัวอักษร", parent=self)
            return

        current_user_id = self.session.current_user.user_id
        user_data_from_db = self.db.get_user_by_id(current_user_id)

        current_password_bytes = current_password_input.encode('utf-8')
        hashed_password_from_db = user_data_from_db['password']

        # Check using bcrypt (assuming database stores hashed passwords)
        if not user_data_from_db or not bcrypt.checkpw(current_password_bytes, hashed_password_from_db):
            # If you switched database.py to store plain text, change this check to:
            # if not user_data_from_db or user_data_from_db['password'] != current_password_input:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านปัจจุบันไม่ถูกต้อง", parent=self)
            return

        update_success = self.db.update_user_password(current_user_id, new_password_input)

        if update_success:
            messagebox.showinfo("สำเร็จ", "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว", parent=self)
            for entry_widget in self.password_entries.values():
                entry_widget.delete(0, 'end')
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเปลี่ยนรหัสผ่านได้ โปรดลองอีกครั้ง", parent=self)