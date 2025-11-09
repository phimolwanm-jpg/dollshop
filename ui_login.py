import customtkinter as ctk
from tkinter import messagebox
import re

# ฟังก์ชันตรวจสอบอีเมล
def validate_email(email):
    pattern = r"[^@]+@[^@]+\.[^@]+"
    if re.match(pattern, email):
        return True
    else:
        return False

# ฟังก์ชันแสดงข้อความแจ้งเตือน
def show_message(parent, title, message, msg_type="info"):
    if msg_type == "error":
        messagebox.showerror(title, message, parent=parent)
    elif msg_type == "warning":
        messagebox.showwarning(title, message, parent=parent)
    else:
        messagebox.showinfo(title, message, parent=parent)


class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.setup_ui()

    def setup_ui(self):
        # สร้างกล่องหลักตรงกลางหน้าจอ
        main_card = ctk.CTkFrame(self, width=850, height=600, corner_radius=25,
                                 fg_color="#FFFFFF", border_width=2, border_color="#FFEBEE")
        main_card.place(relx=0.5, rely=0.5, anchor="center")
        main_card.grid_propagate(False)
        main_card.grid_columnconfigure(0, weight=5)
        main_card.grid_columnconfigure(1, weight=6)
        main_card.grid_rowconfigure(0, weight=1)

        # ส่วนแสดงรูปภาพด้านซ้าย
        image_frame = ctk.CTkFrame(main_card, fg_color="#FFE4E1", corner_radius=20)
        image_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20)
        
        character_image = self.main_app.load_image("character_image.png", size=(350, 500))
        image_label = ctk.CTkLabel(image_frame, text="", image=character_image)
        image_label.pack(expand=True)

        # ส่วนฟอร์มด้านขวา
        form_frame = ctk.CTkFrame(main_card, fg_color="transparent")
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 40), pady=20)
        
        # โลโก้
        logo_image = self.main_app.load_image("logo.png", size=(100, 100))
        logo_label = ctk.CTkLabel(form_frame, text="", image=logo_image)
        logo_label.pack(pady=(20, 10))
        
        # ข้อความต้อนรับ
        welcome_label1 = ctk.CTkLabel(form_frame, text="Welcome to Dollie Shop", 
                                      font=("IBM Plex Sans Thai", 28, "bold"), 
                                      text_color="#6D4C41")
        welcome_label1.pack()
        
        welcome_label2 = ctk.CTkLabel(form_frame, text="เข้าสู่ระบบ หรือ สร้างบัญชีใหม่", 
                                      font=("IBM Plex Sans Thai", 14), 
                                      text_color="#BCAAA4")
        welcome_label2.pack(pady=(0, 20))
        
        # แท็บเลือกระหว่างเข้าสู่ระบบและสมัครสมาชิก
        tab_view = ctk.CTkTabview(form_frame, fg_color="transparent", 
                                  border_width=1, border_color="#FFEBEE",
                                  segmented_button_selected_color="#FFB6C1", 
                                  segmented_button_selected_hover_color="#FFC0CB",
                                  segmented_button_unselected_color="#FFFFFF", 
                                  text_color="#6D4C41")
        tab_view.pack(fill="both", expand=True)
        
        self.login_tab_frame = tab_view.add("เข้าสู่ระบบ")
        self.register_tab_frame = tab_view.add("สมัครสมาชิก")
        self.tab_view = tab_view

        # สร้างฟอร์มเข้าสู่ระบบ
        self.create_login_form()
        
        # สร้างฟอร์มสมัครสมาชิก
        self.create_register_form()

    def create_login_form(self):
        # ช่องกรอกชื่อผู้ใช้
        login_user_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", 
                                        corner_radius=15, border_width=1, 
                                        border_color="#FFEBEE")
        login_user_frame.pack(fill="x", pady=(20, 10), padx=10)
        
        login_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20))
        login_user_icon_label = ctk.CTkLabel(login_user_frame, text="", image=login_user_icon)
        login_user_icon_label.pack(side="left", padx=(10, 5))
        
        self.login_username_entry = ctk.CTkEntry(login_user_frame, placeholder_text="ชื่อผู้ใช้", 
                                                 height=35, border_width=0, fg_color="transparent", 
                                                 font=("IBM Plex Sans Thai", 14))
        self.login_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # ช่องกรอกรหัสผ่าน
        login_pass_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", 
                                       corner_radius=15, border_width=1, 
                                       border_color="#FFEBEE")
        login_pass_frame.pack(fill="x", pady=10, padx=10)
        
        login_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20))
        login_pass_icon_label = ctk.CTkLabel(login_pass_frame, text="", image=login_pass_icon)
        login_pass_icon_label.pack(side="left", padx=(10, 5))
        
        self.login_password_entry = ctk.CTkEntry(login_pass_frame, placeholder_text="รหัสผ่าน", 
                                                 height=35, border_width=0, fg_color="transparent", 
                                                 font=("IBM Plex Sans Thai", 14), show="*")
        self.login_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 0))
        
        # ปุ่มแสดง/ซ่อนรหัสผ่าน
        login_show_pass_button = ctk.CTkButton(login_pass_frame, text="👁️", width=30, height=30,
                                               fg_color="transparent", hover=False, 
                                               text_color="gray50",
                                               command=lambda: self.show_hide_password(
                                                   self.login_password_entry, 
                                                   login_show_pass_button))
        login_show_pass_button.pack(side="right", padx=(0, 5))

        # ปุ่มเข้าสู่ระบบ
        login_button = ctk.CTkButton(self.login_tab_frame, text="เข้าสู่ระบบ", 
                                     height=45, corner_radius=20, 
                                     font=("IBM Plex Sans Thai", 14, "bold"),
                                     fg_color="#FFB6C1", hover_color="#FFC0CB", 
                                     text_color="white", 
                                     command=self.handle_login)
        login_button.pack(fill="x", pady=20, padx=10)

    def create_register_form(self):
        # ช่องกรอกชื่อผู้ใช้
        reg_user_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", 
                                     corner_radius=15, border_width=1, 
                                     border_color="#FFEBEE")
        reg_user_frame.pack(fill="x", pady=(10, 8), padx=10)
        
        reg_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20))
        reg_user_icon_label = ctk.CTkLabel(reg_user_frame, text="", image=reg_user_icon)
        reg_user_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_username_entry = ctk.CTkEntry(reg_user_frame, 
                                                    placeholder_text="ชื่อผู้ใช้ (พิมพ์ใหญ่ 1+, ไม่เกิน 10 ตัว)", 
                                                    height=35, border_width=0, fg_color="transparent", 
                                                    font=("IBM Plex Sans Thai", 14))
        self.register_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # ช่องกรอกอีเมล
        reg_email_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", 
                                      corner_radius=15, border_width=1, 
                                      border_color="#FFEBEE")
        reg_email_frame.pack(fill="x", pady=8, padx=10)
        
        reg_email_icon = self.main_app.load_image("email_icon.png", size=(20, 20))
        reg_email_icon_label = ctk.CTkLabel(reg_email_frame, text="", image=reg_email_icon)
        reg_email_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_email_entry = ctk.CTkEntry(reg_email_frame, placeholder_text="อีเมล", 
                                                height=35, border_width=0, fg_color="transparent", 
                                                font=("IBM Plex Sans Thai", 14))
        self.register_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # ช่องกรอกชื่อ-นามสกุล
        reg_name_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", 
                                     corner_radius=15, border_width=1, 
                                     border_color="#FFEBEE")
        reg_name_frame.pack(fill="x", pady=8, padx=10)
        
        reg_name_icon = self.main_app.load_image("name_icon.png", size=(20, 20))
        reg_name_icon_label = ctk.CTkLabel(reg_name_frame, text="", image=reg_name_icon)
        reg_name_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_fullname_entry = ctk.CTkEntry(reg_name_frame, 
                                                    placeholder_text="ชื่อ-นามสกุล", 
                                                    height=35, border_width=0, 
                                                    fg_color="transparent", 
                                                    font=("IBM Plex Sans Thai", 14))
        self.register_fullname_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))

        # ช่องกรอกรหัสผ่าน
        reg_pass_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", 
                                     corner_radius=15, border_width=1, 
                                     border_color="#FFEBEE")
        reg_pass_frame.pack(fill="x", pady=8, padx=10)
        
        reg_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20))
        reg_pass_icon_label = ctk.CTkLabel(reg_pass_frame, text="", image=reg_pass_icon)
        reg_pass_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_password_entry = ctk.CTkEntry(reg_pass_frame, 
                                                    placeholder_text="ตั้งรหัสผ่าน (8+ ตัว, มีอักษร 3+ ตัว)", 
                                                    height=35, border_width=0, 
                                                    fg_color="transparent", 
                                                    font=("IBM Plex Sans Thai", 14), 
                                                    show="*")
        self.register_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 0))
        
        # ปุ่มแสดง/ซ่อนรหัสผ่าน
        register_show_pass_button = ctk.CTkButton(reg_pass_frame, text="👁️", 
                                                  width=30, height=30,
                                                  fg_color="transparent", hover=False, 
                                                  text_color="gray50",
                                                  command=lambda: self.show_hide_password(
                                                      self.register_password_entry, 
                                                      register_show_pass_button))
        register_show_pass_button.pack(side="right", padx=(0, 5))

        # ปุ่มสร้างบัญชี
        register_button = ctk.CTkButton(self.register_tab_frame, text="สร้างบัญชี", 
                                       height=45, corner_radius=20, 
                                       font=("IBM Plex Sans Thai", 14, "bold"),
                                       fg_color="#FFB6C1", hover_color="#FFC0CB", 
                                       text_color="white", 
                                       command=self.handle_register)
        register_button.pack(fill="x", pady=15, padx=10)

    def show_hide_password(self, password_entry, button):
        # ตรวจสอบว่าตอนนี้รหัสผ่านถูกซ่อนอยู่หรือไม่
        current_show = password_entry.cget("show")
        
        if current_show == "*":
            # ถ้าซ่อนอยู่ ให้แสดงรหัสผ่าน
            password_entry.configure(show="")
            button.configure(text="👁️‍🗨️")
        else:
            # ถ้าแสดงอยู่ ให้ซ่อนรหัสผ่าน
            password_entry.configure(show="*")
            button.configure(text="👁️")

    def handle_login(self):
        # ดึงข้อมูลจากช่องกรอก
        username = self.login_username_entry.get().strip()
        password = self.login_password_entry.get()
        
        # เช็คว่ากรอกครบหรือไม่
        if not username or not password:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", "warning")
            return
        
        # ตรวจสอบข้อมูลกับฐานข้อมูล
        user_data = self.db.authenticate_user(username, password)
        
        if user_data:
            # ถ้าเข้าสู่ระบบสำเร็จ
            self.main_app.on_login_success(user_data)
        else:
            # ถ้าเข้าสู่ระบบไม่สำเร็จ
            show_message(self, "ผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")

    def handle_register(self):
        # ดึงข้อมูลจากช่องกรอกทั้งหมด
        username = self.register_username_entry.get().strip()
        email = self.register_email_entry.get().strip()
        fullname = self.register_fullname_entry.get().strip()
        password = self.register_password_entry.get()
        
        # เช็คว่ากรอกครบทุกช่องหรือไม่
        if not username or not email or not fullname or not password:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง", "warning")
            return
        
        # เช็คว่า username มีตัวพิมพ์ใหญ่อย่างน้อย 1 ตัวหรือไม่
        has_upper = False
        for char in username:
            if char.isupper():
                has_upper = True
                break
        
        if not has_upper:
            show_message(self, "Username ไม่ถูกต้อง", 
                        "ชื่อผู้ใช้ต้องมีตัวอักษรพิมพ์ใหญ่อย่างน้อย 1 ตัว", "warning")
            return
        
        # เช็คว่า username ไม่เกิน 10 ตัวอักษร
        if len(username) > 10:
            show_message(self, "Username ยาวเกินไป", 
                        "ชื่อผู้ใช้ต้องมีความยาวไม่เกิน 10 ตัวอักษร", "warning")
            return
        
        # เช็ครูปแบบอีเมล
        if not validate_email(email):
            show_message(self, "ผิดพลาด", "รูปแบบอีเมลไม่ถูกต้อง", "error")
            return
        
        # เช็ครหัสผ่านต้องยาวอย่างน้อย 8 ตัว
        if len(password) < 8:
            show_message(self, "รหัสผ่านสั้นไป", 
                        "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร", "warning")
            return
        
        # นับจำนวนตัวอักษรในรหัสผ่าน
        letter_count = 0
        for char in password:
            if char.isalpha():
                letter_count = letter_count + 1
        
        # เช็ครหัสผ่านต้องมีตัวอักษรอย่างน้อย 3 ตัว
        if letter_count < 3:
            show_message(self, "รหัสผ่านไม่ปลอดภัย", 
                        "รหัสผ่านต้องมีตัวอักษร (a-z, A-Z) อย่างน้อย 3 ตัว", "warning")
            return
        
        # เช็คว่า username ซ้ำหรือไม่
        if self.db.get_user(username):
            show_message(self, "ผิดพลาด", 
                        "ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น", "error")
            return
        
        # สร้างผู้ใช้ใหม่ในฐานข้อมูล
        new_user_id = self.db.create_user(username, password, email, fullname)
        
        if new_user_id:
            # สมัครสมาชิกสำเร็จ
            show_message(self, "สำเร็จ", "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "info")
            
            # เปลี่ยนไปแท็บเข้าสู่ระบบ
            self.tab_view.set("เข้าสู่ระบบ")
            
            # ล้างข้อมูลในช่องกรอกทั้งหมด
            self.register_username_entry.delete(0, 'end')
            self.register_email_entry.delete(0, 'end')
            self.register_fullname_entry.delete(0, 'end')
            self.register_password_entry.delete(0, 'end')
        else:
            # สมัครสมาชิกไม่สำเร็จ
            show_message(self, "ผิดพลาด", 
                        "การสมัครสมาชิกล้มเหลว (อาจเกิดจากอีเมลซ้ำ)", "error")