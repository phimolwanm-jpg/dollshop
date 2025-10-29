import customtkinter as ctk
from tkinter import messagebox
import re # Import regular expression module for email validation

# --- ฟังก์ชันช่วยเหลือ (ยังคงไว้เพราะมีประโยชน์และไม่ซับซ้อนมาก) ---
def validate_email(email: str) -> bool:
    """
    ตรวจสอบรูปแบบอีเมลง่ายๆ ว่ามี @ และ . หรือไม่
    """
    # ใช้ re.match เพื่อดูว่า email ตรงกับ pattern ที่กำหนดหรือไม่
    # pattern คือ: [ตัวอักษรหรือตัวเลข 1 ตัวขึ้นไป]@[ตัวอักษรหรือตัวเลข 1 ตัวขึ้นไป].[ตัวอักษร 1 ตัวขึ้นไป]
    return re.match(r"[^@]+@[^@]+\.[^@]+", email) is not None

def show_message(parent_window, title_text, message_text, severity_level="info"):
    """
    แสดงกล่องข้อความแจ้งเตือน (info, warning, error)
    """
    if severity_level == "error":
        messagebox.showerror(title_text, message_text, parent=parent_window)
    elif severity_level == "warning":
        messagebox.showwarning(title_text, message_text, parent=parent_window)
    else: # ถ้าไม่ใช่ error หรือ warning ก็ให้เป็น info
        messagebox.showinfo(title_text, message_text, parent=parent_window)
# --- จบฟังก์ชันช่วยเหลือ ---

class LoginWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5") # ตั้งสีพื้นหลัง frame หลัก
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.db = main_app.db 
        # --- ไม่ต้องมี self.assets ถ้าใช้ main_app.load_image ---
        # self.assets = main_app.assets 
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Login/Register"""
        
        # --- 1. สร้างการ์ดหลักตรงกลางจอ ---
        main_card = ctk.CTkFrame(self, # ใส่การ์ดลงใน LoginWindow (self)
                                 width=850, height=600, # กำหนดขนาดการ์ด
                                 corner_radius=25, # ทำให้มุมมน
                                 fg_color="#FFFFFF", # สีพื้นหลังการ์ด (ขาว)
                                 border_width=2,
                                 border_color="#FFEBEE") # สีขอบชมพูอ่อน
        # .place() ใช้วาง widget แบบอ้างอิงตำแหน่ง (relative)
        # relx=0.5, rely=0.5 คือ กึ่งกลางแนวนอน/ตั้ง
        # anchor="center" คือ ให้จุดกึ่งกลางของ widget อยู่ที่ตำแหน่งนั้น
        main_card.place(relx=0.5, rely=0.5, anchor="center") 
        # grid_propagate(False) ป้องกันไม่ให้การ์ดหดตามเนื้อหาข้างใน
        main_card.grid_propagate(False) 
        # แบ่งการ์ดเป็น 2 คอลัมน์: คอลัมน์ 0 กว้าง 5 ส่วน (รูป), คอลัมน์ 1 กว้าง 6 ส่วน (ฟอร์ม)
        main_card.grid_columnconfigure(0, weight=5) 
        main_card.grid_columnconfigure(1, weight=6)
        # ให้แถวที่ 0 (แถวเดียว) ขยายเต็มความสูง
        main_card.grid_rowconfigure(0, weight=1) 

        # --- 2. สร้าง Frame ด้านซ้ายสำหรับใส่รูปภาพ ---
        image_frame = ctk.CTkFrame(main_card, # ใส่ใน main_card
                                   fg_color="#FFE4E1", # สีพื้นหลังชมพูเข้มขึ้น
                                   corner_radius=20)
        # วาง image_frame ในแถว 0, คอลัมน์ 0, ยืดเต็มพื้นที่ (sticky="nsew")
        image_frame.grid(row=0, column=0, sticky="nsew", padx=20, pady=20) 
        
        # โหลดรูปตัวละคร (สมมติว่า main.py มี load_image แล้ว)
        character_image = self.main_app.load_image("character_image.png", size=(350, 500)) 
        # สร้าง Label แสดงรูปภาพ
        image_label = ctk.CTkLabel(image_frame, text="", image=character_image)
        # pack(expand=True) ให้รูปอยู่กลาง frame
        image_label.pack(expand=True) 

        # --- 3. สร้าง Frame ด้านขวาสำหรับใส่ฟอร์ม ---
        form_frame = ctk.CTkFrame(main_card, fg_color="transparent") # พื้นหลังโปร่งใส
        # วาง form_frame ในแถว 0, คอลัมน์ 1, ยืดเต็มพื้นที่
        form_frame.grid(row=0, column=1, sticky="nsew", padx=(0, 40), pady=20) 

        # --- 3.1 ใส่ Logo ---
        # โหลดรูป logo (สมมติว่า main.py มี load_image แล้ว)
        logo_image = self.main_app.load_image("logo.png", size=(100, 100)) 
        logo_label = ctk.CTkLabel(form_frame, text="", image=logo_image)
        logo_label.pack(pady=(20, 10)) # เว้นระยะบน/ล่าง

        # --- 3.2 ใส่ข้อความต้อนรับ ---
        welcome_label1 = ctk.CTkLabel(form_frame, text="Welcome to Dollie Shop", 
                                     font=("IBM Plex Sans Thai", 28, "bold"), 
                                     text_color="#6D4C41")
        welcome_label1.pack()
        welcome_label2 = ctk.CTkLabel(form_frame, text="เข้าสู่ระบบ หรือ สร้างบัญชีใหม่", 
                                     font=("IBM Plex Sans Thai", 14), 
                                     text_color="#BCAAA4") # สีเทา
        welcome_label2.pack(pady=(0, 20))

        # --- 3.3 สร้าง TabView (สำหรับสลับหน้า Login/Register) ---
        tab_view = ctk.CTkTabview(form_frame, # ใส่ใน form_frame
                                  fg_color="transparent", 
                                  border_width=1, border_color="#FFEBEE",
                                  # ตั้งค่าสีปุ่ม Tab
                                  segmented_button_selected_color="#FFB6C1",      # สีปุ่มที่เลือก
                                  segmented_button_selected_hover_color="#FFC0CB",# สีปุ่มที่เลือก (hover)
                                  segmented_button_unselected_color="#FFFFFF",    # สีปุ่มที่ไม่ได้เลือก
                                  text_color="#6D4C41") # สีข้อความบนปุ่ม Tab
        # fill="both", expand=True ให้ TabView ขยายเต็มพื้นที่ที่เหลือใน form_frame
        tab_view.pack(fill="both", expand=True) 
        
        # เพิ่ม Tab "เข้าสู่ระบบ" (tab_view.add จะคืนค่า Frame ของ Tab นั้น)
        self.login_tab_frame = tab_view.add("เข้าสู่ระบบ") 
        # เพิ่ม Tab "สมัครสมาชิก"
        self.register_tab_frame = tab_view.add("สมัครสมาชิก") 
        # เก็บ TabView object ไว้ เพื่อใช้สั่ง .set() ทีหลัง (ตอนสมัครเสร็จ)
        self.tab_view = tab_view 

        # --- 4. เติมเนื้อหาลงในแต่ละ Tab ---
        # (ย้ายโค้ดจาก setup_login_tab และ setup_register_tab มาไว้ตรงนี้)
        
        # --- 4.1 เติมเนื้อหา Tab "เข้าสู่ระบบ" ---
        
        # --- ช่องกรอก "ชื่อผู้ใช้" (Login) ---
        login_user_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                        border_width=1, border_color="#FFEBEE")
        # โหลด icon user (สมมติว่า main.py มี load_image แล้ว)
        login_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20)) 
        login_user_icon_label = ctk.CTkLabel(login_user_frame, text="", image=login_user_icon)
        login_user_icon_label.pack(side="left", padx=(10, 5))
        
        self.login_username_entry = ctk.CTkEntry(login_user_frame, placeholder_text="ชื่อผู้ใช้", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14))
        self.login_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        login_user_frame.pack(fill="x", pady=(20, 10), padx=10) # สั่ง pack frame ทีหลัง

        # --- ช่องกรอก "รหัสผ่าน" (Login) ---
        login_pass_frame = ctk.CTkFrame(self.login_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                        border_width=1, border_color="#FFEBEE")
        # โหลด icon lock (สมมติว่า main.py มี load_image แล้ว)
        login_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20)) 
        login_pass_icon_label = ctk.CTkLabel(login_pass_frame, text="", image=login_pass_icon)
        login_pass_icon_label.pack(side="left", padx=(10, 5))
        
        self.login_password_entry = ctk.CTkEntry(login_pass_frame, placeholder_text="รหัสผ่าน", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14),
                                           show="*") # แสดงเป็น *
        self.login_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        login_pass_frame.pack(fill="x", pady=10, padx=10) 

        # --- ปุ่ม "เข้าสู่ระบบ" ---
        login_button = ctk.CTkButton(self.login_tab_frame, text="เข้าสู่ระบบ", height=45, corner_radius=20, 
                                     font=("IBM Plex Sans Thai", 14, "bold"),
                                     fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                                     command=self.handle_login) # กดแล้วเรียก handle_login
        login_button.pack(fill="x", pady=20, padx=10)
        # --- จบ Tab "เข้าสู่ระบบ" ---

        # --- 4.2 เติมเนื้อหา Tab "สมัครสมาชิก" ---
        
        # --- ช่องกรอก "ตั้งชื่อผู้ใช้" (Register) ---
        reg_user_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                      border_width=1, border_color="#FFEBEE")
        # โหลด icon user (ใช้ซ้ำได้)
        reg_user_icon = self.main_app.load_image("user_icon.png", size=(20, 20)) 
        reg_user_icon_label = ctk.CTkLabel(reg_user_frame, text="", image=reg_user_icon)
        reg_user_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_username_entry = ctk.CTkEntry(reg_user_frame, placeholder_text="ตั้งชื่อผู้ใช้", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14))
        self.register_username_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_user_frame.pack(fill="x", pady=(10, 8), padx=10) 

        # --- ช่องกรอก "อีเมล" (Register) ---
        reg_email_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                       border_width=1, border_color="#FFEBEE")
        # โหลด icon email (สมมติว่า main.py มี load_image แล้ว)
        reg_email_icon = self.main_app.load_image("email_icon.png", size=(20, 20)) 
        reg_email_icon_label = ctk.CTkLabel(reg_email_frame, text="", image=reg_email_icon)
        reg_email_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_email_entry = ctk.CTkEntry(reg_email_frame, placeholder_text="อีเมล", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14))
        self.register_email_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_email_frame.pack(fill="x", pady=8, padx=10) 

        # --- ช่องกรอก "ชื่อ-นามสกุล" (Register) ---
        reg_name_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                      border_width=1, border_color="#FFEBEE")
        # โหลด icon name (สมมติว่า main.py มี load_image แล้ว)
        reg_name_icon = self.main_app.load_image("name_icon.png", size=(20, 20)) 
        reg_name_icon_label = ctk.CTkLabel(reg_name_frame, text="", image=reg_name_icon)
        reg_name_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_fullname_entry = ctk.CTkEntry(reg_name_frame, placeholder_text="ชื่อ-นามสกุล", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14))
        self.register_fullname_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_name_frame.pack(fill="x", pady=8, padx=10) 

        # --- ช่องกรอก "ตั้งรหัสผ่าน" (Register) ---
        reg_pass_frame = ctk.CTkFrame(self.register_tab_frame, fg_color="#FFF0F5", corner_radius=15,
                                      border_width=1, border_color="#FFEBEE")
        # โหลด icon lock (ใช้ซ้ำได้)
        reg_pass_icon = self.main_app.load_image("lock_icon.png", size=(20, 20)) 
        reg_pass_icon_label = ctk.CTkLabel(reg_pass_frame, text="", image=reg_pass_icon)
        reg_pass_icon_label.pack(side="left", padx=(10, 5))
        
        self.register_password_entry = ctk.CTkEntry(reg_pass_frame, placeholder_text="ตั้งรหัสผ่าน (8 ตัวขึ้นไป)", height=35,
                                           border_width=0, fg_color="transparent", 
                                           font=("IBM Plex Sans Thai", 14),
                                           show="*") # แสดงเป็น *
        self.register_password_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        reg_pass_frame.pack(fill="x", pady=8, padx=10) 

        # --- ปุ่ม "สร้างบัญชี" ---
        register_button = ctk.CTkButton(self.register_tab_frame, text="สร้างบัญชี", height=45, corner_radius=20, 
                                        font=("IBM Plex Sans Thai", 14, "bold"),
                                        fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
                                        command=self.handle_register) # กดแล้วเรียก handle_register
        register_button.pack(fill="x", pady=15, padx=10)
        # --- จบ Tab "สมัครสมาชิก" ---
        
        # --- จบการสร้าง UI ทั้งหมด ---

    # --- (ลบฟังก์ชัน create_entry_with_icon, setup_login_tab, setup_register_tab) ---

    def handle_login(self):
        """
        จัดการการกดปุ่มเข้าสู่ระบบ
        """
        # 1. ดึงข้อมูลจากช่องกรอก
        username_input = self.login_username_entry.get().strip() # .strip() ตัดช่องว่างหน้า/หลัง
        password_input = self.login_password_entry.get()
        
        # 2. ตรวจสอบว่ากรอกครบหรือไม่
        if not username_input or not password_input:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกชื่อผู้ใช้และรหัสผ่าน", "warning")
            return # หยุดทำงาน

        # 3. ตรวจสอบข้อมูลกับฐานข้อมูล
        # เรียกฟังก์ชัน authenticate_user ใน database.py
        user_data_from_db = self.db.authenticate_user(username_input, password_input) 
        
        # 4. จัดการผลลัพธ์
        if user_data_from_db: # ถ้า authenticate_user คืนค่าข้อมูล user (ไม่ใช่ None) = สำเร็จ
            # เรียกฟังก์ชัน on_login_success ของ main_app เพื่อแจ้งว่า login สำเร็จ
            self.main_app.on_login_success(user_data_from_db) 
        else: # ถ้า authenticate_user คืนค่า None = ล้มเหลว
            show_message(self, "ผิดพลาด", "ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง", "error")

    def handle_register(self):
        """
        จัดการการกดปุ่มสร้างบัญชี
        """
        # 1. ดึงข้อมูลจากช่องกรอก
        username_input = self.register_username_entry.get().strip()
        email_input = self.register_email_entry.get().strip()
        fullname_input = self.register_fullname_entry.get().strip()
        password_input = self.register_password_entry.get()

        # 2. ตรวจสอบข้อมูลเบื้องต้น
        # 2.1 เช็คว่ากรอกครบทุกช่องหรือไม่
        if not username_input or not email_input or not fullname_input or not password_input:
            show_message(self, "ข้อมูลไม่ครบ", "กรุณากรอกข้อมูลให้ครบทุกช่อง", "warning")
            return
        # 2.2 เช็ครูปแบบอีเมล
        if not validate_email(email_input):
            show_message(self, "ผิดพลาด", "รูปแบบอีเมลไม่ถูกต้อง", "error")
            return
        # 2.3 เช็คความยาวรหัสผ่าน (แก้เป็น 8 ตามเงื่อนไข)
        if len(password_input) < 8: 
            show_message(self, "ผิดพลาด", "รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร", "error")
            return
        # 2.4 เช็คว่าชื่อผู้ใช้ซ้ำหรือไม่ (ถามฐานข้อมูล)
        if self.db.get_user(username_input): # ถ้า get_user คืนค่า (ไม่เป็น None) แปลว่ามีอยู่แล้ว
             show_message(self, "ผิดพลาด", "ชื่อผู้ใช้นี้มีอยู่แล้ว กรุณาใช้ชื่ออื่น", "error")
             return

        # 3. สร้างผู้ใช้ใหม่ในฐานข้อมูล
        # เรียกฟังก์ชัน create_user ใน database.py
        new_user_id = self.db.create_user(username_input, password_input, email_input, fullname_input) 
        
        # 4. จัดการผลลัพธ์
        if new_user_id: # ถ้า create_user คืนค่า user_id (ไม่ใช่ None) = สำเร็จ
            show_message(self, "สำเร็จ", "สมัครสมาชิกสำเร็จ! กรุณาเข้าสู่ระบบ", "info")
            # สลับ TabView ไปที่หน้า "เข้าสู่ระบบ" อัตโนมัติ
            self.tab_view.set("เข้าสู่ระบบ") 
            # ล้างข้อมูลในช่องกรอกของ Tab สมัครสมาชิก
            self.register_username_entry.delete(0, 'end')
            self.register_email_entry.delete(0, 'end')
            self.register_fullname_entry.delete(0, 'end')
            self.register_password_entry.delete(0, 'end')
        else: # ถ้า create_user คืนค่า None = ล้มเหลว (อาจเกิดจาก email ซ้ำ)
            show_message(self, "ผิดพลาด", "การสมัครสมาชิกล้มเหลว (อาจเกิดจากอีเมลซ้ำ)", "error")