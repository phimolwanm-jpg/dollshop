import customtkinter as ctk
from tkinter import messagebox
import bcrypt # Keep bcrypt for essential password checking

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน Lavender Blush
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.session = main_app.session 
        self.db = main_app.db
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ข้อมูลในฟอร์มสดใหม่เสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Profile"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (content_frame) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        header_frame = ctk.CTkFrame(self, # ใส่ header ใน ProfileWindow (self)
                                    fg_color="#FFFFFF", 
                                    corner_radius=0, 
                                    height=70, 
                                    border_width=1, 
                                    border_color="#FFEBEE")
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันปุ่มไปขวา)
        header_frame.grid_columnconfigure(1, weight=1) 
        
        # Label ชื่อหน้า
        header_title = ctk.CTkLabel(
            header_frame, 
            text="👤 โปรไฟล์ของฉัน", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # ปุ่ม "< กลับไปหน้าหลัก"
        back_button = ctk.CTkButton(
            header_frame, 
            text="< กลับไปหน้าหลัก", 
            fg_color="transparent", 
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow') # กดแล้วกลับหน้า Home
        )
        back_button.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---
        
        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (วาง Panel ซ้าย-ขวา) ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        # วาง content_frame ในแถว 1 (ใต้ header) ยืดเต็มพื้นที่
        content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew") 
        # แบ่ง content_frame เป็น 2 คอลัมน์เท่าๆ กัน (uniform="group1")
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1") 
        # ให้แถว 0 (แถวเดียว) ขยายเต็มความสูง
        content_frame.grid_rowconfigure(0, weight=1) 

        # --- 4. สร้าง Panel ด้านซ้าย (ข้อมูลส่วนตัว) ---
        # (ย้ายโค้ดจาก create_profile_panel มาไว้ตรงนี้)
        profile_panel = ctk.CTkFrame(content_frame, # ใส่ใน content_frame คอลัมน์ 0
                                     fg_color="#FFFFFF", 
                                     corner_radius=20, 
                                     border_width=2, 
                                     border_color="#FFEBEE")
        # วาง panel ยืดเต็มพื้นที่แนวตั้งแนวนอน (sticky="nsew")
        profile_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10) 
        # ให้คอลัมน์ 0 ใน panel ขยายเต็มความกว้าง
        profile_panel.grid_columnconfigure(0, weight=1) 

        # --- 4.1 Header ของ Panel ข้อมูลส่วนตัว ---
        profile_panel_header = ctk.CTkFrame(profile_panel, fg_color="#FFE4E1", corner_radius=15)
        profile_panel_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew") # ยืดเต็มกว้าง
        
        profile_panel_title = ctk.CTkLabel(
            profile_panel_header, 
            text="✨ ข้อมูลส่วนตัว", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        profile_panel_title.pack(pady=15)

        # --- 4.2 สร้างช่องกรอกข้อมูล (เขียนทีละช่อง) ---
        # เก็บ Entry widgets ไว้ใน dictionary เพื่อใช้อ้างอิงตอนกดบันทึก
        self.profile_entries = {} 
        # ดึงข้อมูล user ปัจจุบันจาก session
        current_user_data = self.session.current_user 
        
        # --- ช่องกรอก "ชื่อ-นามสกุล" ---
        label_fullname = ctk.CTkLabel(
            profile_panel, text="ชื่อ-นามสกุล:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_fullname.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="w") # วาง Label แถว 1
        
        entry_fullname = ctk.CTkEntry(
            profile_panel, height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        # เติมข้อมูลปัจจุบันลงในช่อง (ถ้าไม่มี ใช้ "")
        entry_fullname.insert(0, getattr(current_user_data, 'full_name', "") or "") 
        entry_fullname.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew") # วาง Entry แถว 2
        self.profile_entries['full_name'] = entry_fullname # เก็บ entry ไว้

        # --- ช่องกรอก "อีเมล" (ห้ามแก้ไข) ---
        label_email = ctk.CTkLabel(
            profile_panel, text="อีเมล:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_email.grid(row=3, column=0, padx=30, pady=(15, 5), sticky="w") # วาง Label แถว 3
        
        entry_email = ctk.CTkEntry(
            profile_panel, height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        entry_email.insert(0, getattr(current_user_data, 'email', "") or "")
        # ทำให้แก้ไขไม่ได้ (disabled)
        entry_email.configure(state="disabled", text_color="gray50") 
        entry_email.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="ew") # วาง Entry แถว 4
        self.profile_entries['email'] = entry_email # เก็บ entry ไว้ (เผื่อจำเป็น)

        # --- ช่องกรอก "เบอร์โทรศัพท์" ---
        label_phone = ctk.CTkLabel(
            profile_panel, text="เบอร์โทรศัพท์:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_phone.grid(row=5, column=0, padx=30, pady=(15, 5), sticky="w") # วาง Label แถว 5
        
        entry_phone = ctk.CTkEntry(
            profile_panel, height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        entry_phone.insert(0, getattr(current_user_data, 'phone', "") or "")
        entry_phone.grid(row=6, column=0, padx=30, pady=(0, 10), sticky="ew") # วาง Entry แถว 6
        self.profile_entries['phone'] = entry_phone

        # --- ช่องกรอก "ที่อยู่สำหรับจัดส่ง" (Textbox) ---
        label_address = ctk.CTkLabel(
            profile_panel, text="ที่อยู่สำหรับจัดส่ง:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_address.grid(row=7, column=0, padx=30, pady=(15, 5), sticky="w") # วาง Label แถว 7
        
        entry_address = ctk.CTkTextbox(
            profile_panel, height=100, corner_radius=15, # ใช้ Textbox สูง 100
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        # เติมข้อมูล (ใช้ index "1.0" สำหรับ Textbox)
        entry_address.insert("1.0", getattr(current_user_data, 'address', "") or "") 
        entry_address.grid(row=8, column=0, padx=30, pady=(0, 10), sticky="ew") # วาง Textbox แถว 8
        self.profile_entries['address'] = entry_address
            
        # --- 4.3 ปุ่มบันทึกข้อมูลส่วนตัว ---
        save_profile_button = ctk.CTkButton(
            profile_panel, 
            text="💾 บันทึกข้อมูลส่วนตัว", 
            command=self.save_profile, # กดแล้วเรียก save_profile
            height=45, corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white"
        )
        # วางปุ่มในแถวถัดไป (แถว 9)
        save_profile_button.grid(row=9, column=0, sticky="ew", padx=30, pady=25) 
        # --- จบ Panel ด้านซ้าย ---

        # --- 5. สร้าง Panel ด้านขวา (เปลี่ยนรหัสผ่าน) ---
        # (ย้ายโค้ดจาก create_password_panel มาไว้ตรงนี้)
        password_panel = ctk.CTkFrame(content_frame, # ใส่ใน content_frame คอลัมน์ 1
                                      fg_color="#FFFFFF", 
                                      corner_radius=20, 
                                      border_width=2, 
                                      border_color="#FFEBEE")
        # วาง panel ยืดเต็มพื้นที่
        password_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10) 
        # ให้คอลัมน์ 0 ใน panel ขยายเต็มความกว้าง
        password_panel.grid_columnconfigure(0, weight=1) 

        # --- 5.1 Header ของ Panel เปลี่ยนรหัสผ่าน ---
        password_panel_header = ctk.CTkFrame(password_panel, fg_color="#FFE4E1", corner_radius=15)
        password_panel_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        password_panel_title = ctk.CTkLabel(
            password_panel_header, 
            text="🔒 เปลี่ยนรหัสผ่าน", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        password_panel_title.pack(pady=15)
        
        # --- 5.2 สร้างช่องกรอกรหัสผ่าน (เขียนทีละช่อง) ---
        # เก็บ Entry widgets ไว้ใน dictionary
        self.password_entries = {} 

        # --- ช่องกรอก "รหัสผ่านปัจจุบัน" ---
        label_current_pass = ctk.CTkLabel(
            password_panel, text="รหัสผ่านปัจจุบัน:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_current_pass.grid(row=1, column=0, padx=30, pady=(15, 5), sticky="w") # แถว 1
        
        entry_current_pass = ctk.CTkEntry(
            password_panel, show="*", # แสดงเป็น *
            height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        entry_current_pass.grid(row=2, column=0, padx=30, pady=(0, 10), sticky="ew") # แถว 2
        self.password_entries['current_password'] = entry_current_pass

        # --- ช่องกรอก "รหัสผ่านใหม่" ---
        label_new_pass = ctk.CTkLabel(
            password_panel, text="รหัสผ่านใหม่:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_new_pass.grid(row=3, column=0, padx=30, pady=(15, 5), sticky="w") # แถว 3
        
        entry_new_pass = ctk.CTkEntry(
            password_panel, show="*", height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        entry_new_pass.grid(row=4, column=0, padx=30, pady=(0, 10), sticky="ew") # แถว 4
        self.password_entries['new_password'] = entry_new_pass

        # --- ช่องกรอก "ยืนยันรหัสผ่านใหม่" ---
        label_confirm_pass = ctk.CTkLabel(
            password_panel, text="ยืนยันรหัสผ่านใหม่:", 
            font=ctk.CTkFont(size=14), text_color="#6D4C41"
        )
        label_confirm_pass.grid(row=5, column=0, padx=30, pady=(15, 5), sticky="w") # แถว 5
        
        entry_confirm_pass = ctk.CTkEntry(
            password_panel, show="*", height=45, corner_radius=15,
            border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14)
        )
        entry_confirm_pass.grid(row=6, column=0, padx=30, pady=(0, 10), sticky="ew") # แถว 6
        self.password_entries['confirm_password'] = entry_confirm_pass
            
        # --- 5.3 ปุ่มเปลี่ยนรหัสผ่าน ---
        change_password_button = ctk.CTkButton(
            password_panel, 
            text="🔐 เปลี่ยนรหัสผ่าน", 
            command=self.change_password, # กดแล้วเรียก change_password
            height=45, corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B9D", hover_color="#FF8FB3", text_color="white"
        )
        # วางปุ่มในแถวถัดไป (แถว 7)
        change_password_button.grid(row=7, column=0, sticky="ew", padx=30, pady=25) 
        # --- จบ Panel ด้านขวา ---

    # --- (ลบฟังก์ชัน create_profile_panel และ create_password_panel) ---

    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวที่แก้ไข (Logic เดิม)"""
        # 1. ดึงข้อมูลจาก self.profile_entries
        full_name_input = self.profile_entries['full_name'].get().strip()
        phone_input = self.profile_entries['phone'].get().strip()
        # ดึงข้อมูลจาก Textbox
        address_input = self.profile_entries['address'].get("1.0", "end-1c").strip() 

        # 2. ตรวจสอบข้อมูล (ชื่อห้ามว่าง)
        if not full_name_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล", parent=self)
            return # หยุดทำงาน

        # 3. อัปเดตฐานข้อมูล
        current_user_id = self.session.current_user.user_id
        update_success = self.db.update_user_profile(current_user_id, full_name_input, phone_input, address_input)
        
        # 4. จัดการผลลัพธ์
        if update_success:
            # --- สำคัญ: อัปเดตข้อมูลใน session (RAM) ด้วย ---
            self.session.current_user.full_name = full_name_input
            self.session.current_user.phone = phone_input
            self.session.current_user.address = address_input
            
            messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว", parent=self)
            self.on_show() # Refresh หน้าจอเพื่อให้เห็นข้อมูลใหม่ (ถ้าจำเป็น)
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลส่วนตัวได้ โปรดลองอีกครั้ง", parent=self)

    def change_password(self):
        """เปลี่ยนรหัสผ่าน (Logic เดิม)"""
        # 1. ดึงข้อมูลจาก self.password_entries
        current_password_input = self.password_entries['current_password'].get()
        new_password_input = self.password_entries['new_password'].get()
        confirm_password_input = self.password_entries['confirm_password'].get()

        # 2. ตรวจสอบข้อมูลเบื้องต้น
        # 2.1 เช็คว่ากรอกครบทุกช่องหรือไม่
        if not current_password_input or not new_password_input or not confirm_password_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกรหัสผ่านให้ครบทุกช่อง", parent=self)
            return
        # 2.2 เช็คว่ารหัสใหม่ตรงกันหรือไม่
        if new_password_input != confirm_password_input:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน", parent=self)
            return
        # 2.3 เช็คความยาวรหัสผ่านใหม่ (แก้เป็น 8 ตาม ui_login)
        if len(new_password_input) < 8: 
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่ต้องมีอย่างน้อย 8 ตัวอักษร", parent=self)
            return
            
        # 3. ตรวจสอบรหัสผ่านปัจจุบันกับฐานข้อมูล
        current_user_id = self.session.current_user.user_id
        # ดึงข้อมูล user (รวม password ที่ hash ไว้) จาก DB
        user_data_from_db = self.db.get_user_by_id(current_user_id) 
        
        # --- ใช้ bcrypt.checkpw เพื่อเปรียบเทียบ ---
        # ต้อง encode รหัสผ่านที่ user กรอก ให้เป็น bytes ก่อน
        current_password_bytes = current_password_input.encode('utf-8') 
        # hashed_password จาก DB (เป็น bytes อยู่แล้ว)
        hashed_password_from_db = user_data_from_db['password'] 
        
        # ถ้าหา user ไม่เจอ หรือ checkpw ไม่ผ่าน
        if not user_data_from_db or not bcrypt.checkpw(current_password_bytes, hashed_password_from_db):
            messagebox.showerror("ผิดพลาด", "รหัสผ่านปัจจุบันไม่ถูกต้อง", parent=self)
            return # หยุดทำงาน
            
        # 4. ถ้าผ่านหมด: อัปเดตรหัสผ่านใหม่ในฐานข้อมูล
        update_success = self.db.update_user_password(current_user_id, new_password_input) 
        
        # 5. จัดการผลลัพธ์
        if update_success:
            messagebox.showinfo("สำเร็จ", "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว", parent=self)
            # ล้างค่าในช่องกรอกรหัสผ่านทั้งหมด
            for entry_widget in self.password_entries.values():
                entry_widget.delete(0, 'end')
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเปลี่ยนรหัสผ่านได้ โปรดลองอีกครั้ง", parent=self)