# M:/doll_shop/ui_login.py (แก้ไข handle_register และ placeholder)

import customtkinter as ctk
from tkinter import messagebox
import re # Import regular expression module for email validation

# --- ฟังก์ชันช่วยเหลือ (validate_email, show_message) เหมือนเดิม ---
def validate_email(email: str) -> bool:
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def show_message(parent_window, title_text, message_text, severity_level="info"):
    if severity_level == "error":
        messagebox.showerror(title_text, message_text, parent=parent_window)
    elif severity_level == "warning":
        messagebox.showwarning(title_text, message_text, parent=parent_window)
    else:
        messagebox.showinfo(title_text, message_text, parent=parent_window)
# --- จบฟังก์ชันช่วยเหลือ ---

class LoginWindow(ctk.CTkFrame):
    # ... (__init__ และ toggle_password_visibility เหมือนเดิม) ...
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.setup_ui()

    def toggle_password_visibility(self, entry_widget, button_widget):
        current_show_state = entry_widget.cget("show")
        if current_show_state == "*":
            entry_widget.configure(show="")
            button_widget.configure(text="👁️‍🗨️")
        else:
            entry_widget.configure(show="*")
            button_widget.configure(text="👁️")

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Login/Register"""
        # --- 1. สร้างการ์ดหลัก (เหมือนเดิม) ---
        main_card = ctk.CTkFrame(self, width=850, height=600, corner_radius=25,
                                 fg_color="#FFFFFF", border_width=2, border_color="#FFEBEE")
        main_card.place(relx=0.5, rely=0.5, anchor="center")
        main_card.grid_propagate(False)
        main_card.grid_columnconfigure(0, weight=5)
        main_card.grid_columnconfigure(1, weight=6)
        main_card.grid_rowconfigure(0, weight=1)

        # --- 2. Frame รูปภาพ (เหมือนเดิม) ---
        image_frame = ctk.CTkFrame(main_card, fg_color="#FFE4E1", corner_radius=20)
        image_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        character_image = self.main_app.load_image("character_image.png", size=(350, 500))
        image_label = ctk.CTkLabel(image_frame, text="", image=character_image)
        image_label.pack(expand=True)

        # --- 3. Frame ฟอร์ม (เหมือนเดิม) ---
        form_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 40), pady=20)
        logo_image = self.main_app.load_image("logo.png", size=(100, 100))
        logo_label = ctk.CTkLabel(form_frame, text="", image=logo_image)
        logo_label.pack(pady=(20, 10))
        welcome_label1 = ctk.CTkLabel(form_frame, text="Welcome to Dollie Shop", font=("IBM Plex Sans Thai", 28, "bold"), text_color="#6D4C41")
        welcome_label1.pack()
        welcome_label2 = ctk.CTkLabel(form_frame, text="เข้าสู่ระบบ หรือ สร้างบัญชีใหม่", font=("IBM Plex Sans Thai", 14), text_color="#BCAAA4")
        welcome_label2.pack(pady=(0, 20))
        tab_view = ctk.CTkTabview(form_frame, fg_color="transparent", border_width=1, border_color="#FFEBEE",
                                  segmented_button_selected_color="#FFB6C1", segmented_button_selected_hover_color="#FFC0CB",
                                  segmented_button_unselected_color="#FFFFFF", text_color="#6D4C41")
        tab_view.pack(fill="both", expand=True)
        self.login_tab_frame = tab_view.add("เข้าสู่ระบบ")
        self.register_tab_frame = tab_view.add("สมัครสมาชิก")
        self.tab_view = tab_view

        # --- 4. เติมเนื้อหา Tab ---

        # --- 4.1 Tab "เข้าสู่ระบบ" (เหมือนเดิม) ---
        login_user_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        login_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20))
        login_user_icon_label = ctk.CTkLabel(login_user_frame, text="", image=login_user_icon)
        login_user_icon_label.pack(side="left", padx=(10, 5))
        self.login_username_entry = ctk.CTkEntry(login_user_frame, placeholder_text="ชื่อผู้ใช้", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14))
        self.login_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        login_user_frame.pack(fill="x", pady=(20, 10), padx=10)
        login_pass_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        login_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20))
        login_pass_icon_label = ctk.CTkLabel(login_pass_frame, text="", image=login_pass_icon)
        login_pass_icon_label.pack(side="left", padx=(10, 5))
        self.login_password_entry = ctk.CTkEntry(login_pass_frame, placeholder_text="รหัสผ่าน", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14), show="*")
        login_show_pass_button = ctk.CTkButton(
            login_pass_frame, text="👁️", width=30, height=30,
            fg_color="transparent", hover=False, text_color="gray50",
            command=lambda: self.toggle_password_visibility(self.login_password_entry, login_show_pass_button)
        )
        login_show_pass_button.pack(side="right", padx=(0, 5))
        self.login_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 0))
        login_pass_frame.pack(fill="x", pady=10, padx=10)
        login_button = ctk.CTkButton(self.login_tab_frame, text="เข้าสู่ระบบ", height=45, corner_radius=20, font=("IBM Plex Sans Thai", 14, "bold"),
                                     fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white", command=self.handle_login)
        login_button.pack(fill="x", pady=20, padx=10)

        # --- 4.2 Tab "สมัครสมาชิก" (แก้ไข Placeholder) ---
        reg_user_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        reg_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20))
        reg_user_icon_label = ctk.CTkLabel(reg_user_frame, text="", image=reg_user_icon)
        reg_user_icon_label.pack(side="left", padx=(10, 5))
        self.register_username_entry = ctk.CTkEntry(reg_user_frame, placeholder_text="ชื่อผู้ใช้ (พิมพ์ใหญ่ 1+, ไม่เกิน 10 ตัว)", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14)) # <--- แก้ placeholder
        self.register_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_user_frame.pack(fill="x", pady=(10, 8), padx=10)

        # --- (Email, Fullname entries - เหมือนเดิม) ---
        reg_email_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        reg_email_icon = self.main_app.load_image("email_icon.png", size=(20, 20))
        reg_email_icon_label = ctk.CTkLabel(reg_email_frame, text="", image=reg_email_icon)
        reg_email_icon_label.pack(side="left", padx=(10, 5))
        self.register_email_entry = ctk.CTkEntry(reg_email_frame, placeholder_text="อีเมล", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14))
        self.register_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_email_frame.pack(fill="x", pady=8, padx=10)

        reg_name_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        reg_name_icon = self.main_app.load_image("name_icon.png", size=(20, 20))
        reg_name_icon_label = ctk.CTkLabel(reg_name_frame, text="", image=reg_name_icon)
        reg_name_icon_label.pack(side="left", padx=(10, 5))
        self.register_fullname_entry = ctk.CTkEntry(reg_name_frame, placeholder_text="ชื่อ-นามสกุล", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14))
        self.register_fullname_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_name_frame.pack(fill="x", pady=8, padx=10)
        # --- (End Email, Fullname entries) ---

        reg_pass_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15, border_width=1, border_color="#FFEBEE")
        reg_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20))
        reg_pass_icon_label = ctk.CTkLabel(reg_pass_frame, text="", image=reg_pass_icon)
        reg_pass_icon_label.pack(side="left", padx=(10, 5))
        self.register_password_entry = ctk.CTkEntry(reg_pass_frame, placeholder_text="ตั้งรหัสผ่าน (8+ ตัว, มีอักษร 3+ ตัว)", height=35, border_width=0, fg_color="transparent", font=("IBM Plex Sans Thai", 14), show="*")
        register_show_pass_button = ctk.CTkButton(
            reg_pass_frame, text="👁️", width=30, height=30,
            fg_color="transparent", hover=False, text_color="gray50",
            command=lambda: self.toggle_password_visibility(self.register_password_entry, register_show_pass_button)
        )
        register_show_pass_button.pack(side="right", padx=(0, 5))
        self.register_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 0))
        reg_pass_frame.pack(fill="x", pady=8, padx=10)

        register_button = ctk.CTkButton(self.register_tab_frame, text="สร้างบัญชี", height=45, corner_radius=20, font=("IBM Plex Sans Thai", 14, "bold"),
                                        fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white", command=self.handle_register)
        register_button.pack(fill="x", pady=15, padx=10)


    # --- (ลบฟังก์ชัน create_entry_with_icon, setup_login_tab, setup_register_tab) ---

    # --- ฟังก์ชัน handle_login (เหมือนเดิม) ---
    def handle_login(self):
        username_input = self.login_username_entry.get().strip()
        password_input = self.login_password_entry.get()
        if not username_input or not password_input:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", "warning")
            return

        user_data_from_db = self.db.authenticate_user(username_input, password_input)
        if user_data_from_db:
            self.main_app.on_login_success(user_data_from_db)
        else:
            show_message(self, "ผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")

    # --- vvvv แก้ไขฟังก์ชัน handle_register vvvv ---
    def handle_register(self):
        """
        จัดการการกดปุ่มสร้างบัญชี (เพิ่ม Validation Rules)
        """
        # 1. ดึงข้อมูลจากช่องกรอก
        username_input = self.register_username_entry.get().strip()
        email_input = self.register_email_entry.get().strip()
        fullname_input = self.register_fullname_entry.get().strip()
        password_input = self.register_password_entry.get() # ไม่ต้อง strip รหัสผ่าน

        # 2. ตรวจสอบข้อมูลเบื้องต้น
        # 2.1 เช็คว่ากรอกครบทุกช่องหรือไม่
        if not username_input or not email_input or not fullname_input or not password_input:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง", "warning")
            return

        # --- 2.2 เช็ค Username: ต้องมีตัวพิมพ์ใหญ่อย่างน้อย 1 ตัว ---
        if not any(c.isupper() for c in username_input):
            show_message(self, "Username ไม่ถูกต้อง", "ชื่อผู้ใช้ต้องมีตัวอักษรพิมพ์ใหญ่อย่างน้อย 1 ตัว", "warning")
            return

        # --- 2.2.1 เช็ค Username: ความยาวไม่เกิน 10 ตัว ---
        if len(username_input) > 10:
            show_message(self, "Username ยาวเกินไป", "ชื่อผู้ใช้ต้องมีความยาวไม่เกิน 10 ตัวอักษร", "warning")
            return
        # --- สิ้นสุดการเช็ค Username ---

        # 2.3 เช็ครูปแบบอีเมล
        if not validate_email(email_input):
            show_message(self, "ผิดพลาด", "รูปแบบอีเมลไม่ถูกต้อง", "error")
            return

        # 2.4 เช็คความยาวรหัสผ่าน (ขั้นต่ำ 8 ตัว)
        if len(password_input) < 8:
            show_message(self, "รหัสผ่านสั้นไป", "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร", "warning")
            return

        # 2.5 เช็ครหัสผ่าน: ต้องมีตัวอักษรอย่างน้อย 3 ตัว
        letter_count = sum(c.isalpha() for c in password_input)
        if letter_count < 3:
             show_message(self, "รหัสผ่านไม่ปลอดภัย", "รหัสผ่านต้องมีตัวอักษร (a-z, A-Z) อย่างน้อย 3 ตัว", "warning")
             return

        # 2.6 เช็คว่าชื่อผู้ใช้ซ้ำหรือไม่
        if self.db.get_user(username_input):
             show_message(self, "ผิดพลาด", "ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น", "error")
             return

        # 3. สร้างผู้ใช้ใหม่ในฐานข้อมูล
        new_user_id = self.db.create_user(username_input, password_input, email_input, fullname_input)

        # 4. จัดการผลลัพธ์
        if new_user_id:
            show_message(self, "สำเร็จ", "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "info")
            self.tab_view.set("เข้าสู่ระบบ")
            self.register_username_entry.delete(0, 'end')
            self.register_email_entry.delete(0, 'end')
            self.register_fullname_entry.delete(0, 'end')
            self.register_password_entry.delete(0, 'end')
        else:
            show_message(self, "ผิดพลาด", "การสมัครสมาชิกล้มเหลว (อาจเกิดจากอีเมลซ้ำ)", "error")
    # --- ^^^^ สิ้นสุดการแก้ไข handle_register ^^^^ ---