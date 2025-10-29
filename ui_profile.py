import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt
import os
from PIL import Image
import time
import shutil

# กำหนด Path สำหรับเก็บรูปโปรไฟล์
PROFILE_IMG_DIR = "assets/profile_images"

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db
        self.new_image_file = None
        
        # สร้างโฟลเดอร์สำหรับรูปโปรไฟล์ถ้ายังไม่มี
        if not os.path.exists(PROFILE_IMG_DIR):
            os.makedirs(PROFILE_IMG_DIR)

    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมด"""
        
        # ตรวจสอบการล็อกอิน
        if not self.session.current_user:
            self.grid_columnconfigure(0, weight=1)
            self.grid_rowconfigure(0, weight=1)
            
            warning_frame = ctk.CTkFrame(self, fg_color="transparent")
            warning_frame.pack(expand=True)
            
            ctk.CTkLabel(
                warning_frame, 
                text="❌ คุณยังไม่ได้เข้าสู่ระบบ ❌", 
                font=ctk.CTkFont(size=24, weight="bold"), 
                text_color="#FF6B9D"
            ).pack(padx=50, pady=(100, 20))
            
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

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # Header
        header_frame = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF", 
            corner_radius=0, 
            height=70, 
            border_width=1, 
            border_color="#FFEBEE"
        )
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
            text="← กลับไปหน้าหลัก", 
            fg_color="transparent", 
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14),
            command=lambda: self.main_app.navigate_to('HomeWindow')
        )
        back_button.pack(side="right", padx=30, pady=20)
        
        # Main Content Frame
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=1)

        self.create_profile_panel(content_frame)
        self.create_password_panel(content_frame)

    def create_profile_panel(self, parent):
        """สร้าง Panel สำหรับแก้ไขข้อมูลส่วนตัวพร้อมรูปโปรไฟล์"""
        panel = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=20, 
            border_width=2, 
            border_color="#FFEBEE"
        )
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
        
        # ส่วนรูปโปรไฟล์
        profile_img_frame = ctk.CTkFrame(panel, fg_color="#FFF0F5", corner_radius=15)
        profile_img_frame.grid(row=row_counter, column=0, padx=30, pady=(15, 20), sticky="ew")
        profile_img_frame.grid_columnconfigure(1, weight=1)
        
        # โหลดรูปภาพปัจจุบัน
        self.load_profile_image(user)
        
        # แสดงรูปโปรไฟล์
        self.img_label = ctk.CTkLabel(
            profile_img_frame, 
            image=self.profile_img, 
            text=""
        )
        self.img_label.grid(row=0, column=0, padx=20, pady=15)
        
        # ข้อมูลพื้นฐานข้างรูป
        info_frame = ctk.CTkFrame(profile_img_frame, fg_color="transparent")
        info_frame.grid(row=0, column=1, sticky="w", padx=10, pady=15)
        
        ctk.CTkLabel(
            info_frame,
            text=user.full_name or "ยังไม่ระบุชื่อ",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#FF6B9D"
        ).pack(anchor="w", pady=(0, 5))
        
        ctk.CTkLabel(
            info_frame,
            text=user.email,
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        ).pack(anchor="w")
        
        # ปุ่มเลือกรูปภาพ
        btn_frame = ctk.CTkFrame(profile_img_frame, fg_color="transparent")
        btn_frame.grid(row=0, column=2, padx=20, pady=15)
        
        ctk.CTkButton(
            btn_frame, 
            text="📷 เลือกรูปใหม่", 
            command=self.select_profile_image,
            width=140,
            height=35,
            corner_radius=15,
            font=ctk.CTkFont(size=14),
            fg_color="#FFC0CB",
            hover_color="#FFB6C1",
            text_color="white"
        ).pack(pady=(0, 5))
        
        ctk.CTkButton(
            btn_frame, 
            text="🗑️ ลบรูป", 
            command=self.remove_profile_image,
            width=140,
            height=35,
            corner_radius=15,
            font=ctk.CTkFont(size=14),
            fg_color="#FFE4E1",
            hover_color="#FFD1DC",
            text_color="#FF6B9D"
        ).pack()
        
        row_counter += 1
        
        # ช่องกรอกข้อมูลส่วนตัว
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
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6D4C41"
            ).grid(row=row_counter, column=0, padx=30, pady=(15, 5), sticky="w")
            
            # Entry
            if key == "address":
                entry = ctk.CTkTextbox(
                    panel, 
                    height=100, 
                    corner_radius=15,
                    border_width=2,
                    border_color="#FFEBEE",
                    fg_color="#FFFFFF",
                    font=ctk.CTkFont(size=14)
                )
                entry.insert("1.0", getattr(user, key) or "")
            else:
                entry = ctk.CTkEntry(
                    panel, 
                    height=45,
                    corner_radius=15,
                    border_width=2,
                    border_color="#FFEBEE",
                    fg_color="#FFFFFF",
                    font=ctk.CTkFont(size=14)
                )
                entry.insert(0, getattr(user, key) or "")
            
            # Email ไม่ให้แก้ไข
            if key == "email": 
                entry.configure(state="disabled", text_color="#999999")

            entry.grid(row=row_counter + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
            self.profile_entries[key] = entry
            row_counter += 2
            
        # ปุ่มบันทึก
        save_btn = ctk.CTkButton(
            panel, 
            text="💾 บันทึกข้อมูลส่วนตัว", 
            command=self.save_profile, 
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            text_color="white"
        )
        save_btn.grid(row=row_counter, column=0, sticky="ew", padx=30, pady=25)

    def load_profile_image(self, user):
        """โหลดรูปโปรไฟล์ของผู้ใช้"""
        default_img_path = 'assets/default_profile.png'
        img_size = (100, 100)
        
        try:
            if user.profile_image_url and user.profile_image_url != 'default_profile.png':
                # ลองโหลดรูปจากโฟลเดอร์ profile_images
                img_path = os.path.join(PROFILE_IMG_DIR, user.profile_image_url)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    # ครอปเป็นวงกลม (สี่เหลี่ยม)
                    img = self.crop_to_circle(img, img_size)
                    self.profile_img = ctk.CTkImage(img, size=img_size)
                    return
            
            # ใช้รูป default
            if os.path.exists(default_img_path):
                img = Image.open(default_img_path)
                img = self.crop_to_circle(img, img_size)
                self.profile_img = ctk.CTkImage(img, size=img_size)
            else:
                # สร้างรูป placeholder
                self.profile_img = self.create_placeholder_image(img_size)
                
        except Exception as e:
            print(f"Error loading profile image: {e}")
            self.profile_img = self.create_placeholder_image(img_size)
    
    def crop_to_circle(self, img, size):
        """ครอปรูปภาพเป็นวงกลม"""
        img = img.resize(size, Image.LANCZOS)
        
        # สร้าง mask วงกลม
        mask = Image.new('L', size, 0)
        from PIL import ImageDraw
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # สร้างภาพพื้นหลังขาว
        output = Image.new('RGBA', size, (255, 255, 255, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def create_placeholder_image(self, size):
        """สร้างรูป placeholder"""
        img = Image.new('RGB', size, color='#FFB6C1')
        from PIL import ImageDraw, ImageFont
        draw = ImageDraw.Draw(img)
        
        # วาดไอคอนผู้ใช้
        draw.ellipse([20, 20, 80, 80], fill='#FFFFFF')
        draw.ellipse([35, 30, 65, 60], fill='#FFB6C1')
        draw.ellipse([25, 55, 75, 95], fill='#FFB6C1')
        
        return ctk.CTkImage(img, size=size)

    def select_profile_image(self):
        """เปิด Dialog ให้เลือกรูปภาพและแสดงตัวอย่าง"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        filepath = filedialog.askopenfilename(
            title="เลือกรูปโปรไฟล์", 
            filetypes=filetypes
        )
        
        if filepath:
            try:
                # ตรวจสอบขนาดไฟล์ (จำกัดที่ 5MB)
                file_size = os.path.getsize(filepath) / (1024 * 1024)  # MB
                if file_size > 5:
                    messagebox.showwarning(
                        "ไฟล์ใหญ่เกินไป", 
                        "กรุณาเลือกรูปภาพที่มีขนาดไม่เกิน 5MB",
                        parent=self
                    )
                    return
                
                # บันทึก path ชั่วคราว
                self.new_image_file = filepath
                
                # แสดงตัวอย่างรูปใหม่
                img = Image.open(filepath)
                img = self.crop_to_circle(img, (100, 100))
                new_img = ctk.CTkImage(img, size=(100, 100))
                
                self.img_label.configure(image=new_img)
                self.img_label.image = new_img
                
                messagebox.showinfo(
                    "เลือกรูปภาพสำเร็จ", 
                    "กรุณากดปุ่ม 'บันทึกข้อมูลส่วนตัว' เพื่อยืนยันการเปลี่ยนรูป",
                    parent=self
                )
                
            except Exception as e:
                messagebox.showerror(
                    "ผิดพลาด", 
                    f"ไม่สามารถโหลดรูปภาพได้: {str(e)}",
                    parent=self
                )
                self.new_image_file = None
    
    def remove_profile_image(self):
        """ลบรูปโปรไฟล์และใช้รูป default"""
        if messagebox.askyesno(
            "ยืนยันการลบ", 
            "คุณต้องการลบรูปโปรไฟล์และใช้รูป default หรือไม่?",
            parent=self
        ):
            self.new_image_file = "DELETE"
            
            # แสดงรูป default
            default_img_path = 'assets/default_profile.png'
            if os.path.exists(default_img_path):
                img = Image.open(default_img_path)
                img = self.crop_to_circle(img, (100, 100))
                default_img = ctk.CTkImage(img, size=(100, 100))
            else:
                default_img = self.create_placeholder_image((100, 100))
            
            self.img_label.configure(image=default_img)
            self.img_label.image = default_img
            
            messagebox.showinfo(
                "ลบรูปภาพสำเร็จ", 
                "กรุณากดปุ่ม 'บันทึกข้อมูลส่วนตัว' เพื่อยืนยัน",
                parent=self
            )

    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวพร้อมจัดการรูปโปรไฟล์"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ", parent=self)
            return

        # รับข้อมูลจากฟอร์ม
        full_name = self.profile_entries['full_name'].get().strip()
        phone = self.profile_entries['phone'].get().strip()
        address = self.profile_entries['address'].get("1.0", "end-1c").strip()
        
        # ตรวจสอบข้อมูล
        if not full_name:
            messagebox.showwarning(
                "ข้อมูลไม่ครบ", 
                "กรุณากรอกชื่อ-นามสกุล",
                parent=self
            )
            return
        
        # ตรวจสอบเบอร์โทร (ถ้ามี)
        if phone and not phone.replace("-", "").isdigit():
            messagebox.showwarning(
                "ข้อมูลไม่ถูกต้อง", 
                "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลขเท่านั้น",
                parent=self
            )
            return

        # จัดการรูปโปรไฟล์
        new_image_filename = self.session.current_user.profile_image_url
        
        if self.new_image_file == "DELETE":
            # ลบรูปเก่าและใช้ default
            old_filename = self.session.current_user.profile_image_url
            if old_filename and old_filename != 'default_profile.png':
                old_path = os.path.join(PROFILE_IMG_DIR, old_filename)
                if os.path.exists(old_path):
                    try:
                        os.remove(old_path)
                    except Exception as e:
                        print(f"Cannot delete old image: {e}")
            
            new_image_filename = None
            
        elif self.new_image_file:
            # อัปโหลดรูปใหม่
            try:
                # สร้างชื่อไฟล์ใหม่
                ext = os.path.splitext(self.new_image_file)[1].lower()
                if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                    ext = '.png'
                
                new_image_filename = f"profile_{self.session.current_user.user_id}_{int(time.time())}{ext}"
                dest_path = os.path.join(PROFILE_IMG_DIR, new_image_filename)
                
                # บันทึกไฟล์
                img = Image.open(self.new_image_file)
                img = img.convert('RGB')  # แปลงเป็น RGB ก่อนบันทึก
                img.save(dest_path, quality=95)
                
                # ลบไฟล์เก่า
                old_filename = self.session.current_user.profile_image_url
                if old_filename and old_filename != 'default_profile.png':
                    old_path = os.path.join(PROFILE_IMG_DIR, old_filename)
                    if os.path.exists(old_path):
                        try:
                            os.remove(old_path)
                        except Exception as e:
                            print(f"Cannot delete old image: {e}")
                            
            except Exception as e:
                messagebox.showerror(
                    "ผิดพลาด", 
                    f"ไม่สามารถบันทึกรูปภาพได้: {str(e)}",
                    parent=self
                )
                return

        # อัปเดตข้อมูลในฐานข้อมูล
        user_id = self.session.current_user.user_id
        
        if self.db.update_user_profile(user_id, full_name, phone, address, new_image_filename):
            # อัปเดต session
            self.session.current_user.full_name = full_name
            self.session.current_user.phone = phone
            self.session.current_user.address = address
            self.session.current_user.profile_image_url = new_image_filename
            
            messagebox.showinfo(
                "สำเร็จ", 
                "✅ อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว",
                parent=self
            )
            
            self.new_image_file = None
            self.on_show()  # รีเฟรชหน้า
        else:
            messagebox.showerror(
                "ผิดพลาด", 
                "ไม่สามารถอัปเดตข้อมูลได้ กรุณาลองใหม่อีกครั้ง",
                parent=self
            )

    def create_password_panel(self, parent):
        """สร้าง Panel สำหรับเปลี่ยนรหัสผ่าน"""
        panel = ctk.CTkFrame(
            parent, 
            fg_color="#FFFFFF", 
            corner_radius=20, 
            border_width=2, 
            border_color="#FFEBEE"
        )
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        panel.grid_columnconfigure(0, weight=1)

        # Header
        header = ctk.CTkFrame(panel, fg_color="#FFE4E1", corner_radius=15)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        ctk.CTkLabel(
            header, 
            text="🔒 เปลี่ยนรหัสผ่าน", 
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)
        
        # คำแนะนำ
        info_label = ctk.CTkLabel(
            panel,
            text="💡 รหัสผ่านควรมีความยาวอย่างน้อย 6 ตัวอักษร\nและประกอบด้วยตัวอักษรและตัวเลข",
            font=ctk.CTkFont(size=12),
            text_color="#999999",
            justify="left"
        )
        info_label.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="w")
        
        # ช่องกรอกรหัสผ่าน
        fields = {
            "current_password": "รหัสผ่านปัจจุบัน:", 
            "new_password": "รหัสผ่านใหม่:", 
            "confirm_password": "ยืนยันรหัสผ่านใหม่:"
        }
        self.password_entries = {}

        row_counter = 2
        for key, label in fields.items():
            # Label
            ctk.CTkLabel(
                panel, 
                text=label, 
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#6D4C41"
            ).grid(row=row_counter, column=0, padx=30, pady=(15, 5), sticky="w")
            
            # Entry frame (สำหรับปุ่มแสดง/ซ่อนรหัสผ่าน)
            entry_frame = ctk.CTkFrame(panel, fg_color="transparent")
            entry_frame.grid(row=row_counter + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
            entry_frame.grid_columnconfigure(0, weight=1)
            
            # Entry
            entry = ctk.CTkEntry(
                entry_frame, 
                show="●",
                height=45,
                corner_radius=15,
                border_width=2,
                border_color="#FFEBEE",
                fg_color="#FFFFFF",
                font=ctk.CTkFont(size=14)
            )
            entry.grid(row=0, column=0, sticky="ew")
            self.password_entries[key] = entry
            row_counter += 2
            
        # ปุ่มเปลี่ยนรหัสผ่าน
        change_btn = ctk.CTkButton(
            panel, 
            text="🔐 เปลี่ยนรหัสผ่าน", 
            command=self.change_password, 
            height=50,
            corner_radius=15,
            font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B9D",
            hover_color="#FF8FB3",
            text_color="white"
        )
        change_btn.grid(row=row_counter, column=0, sticky="ew", padx=30, pady=25)
        
        # ปุ่มล้างข้อมูล
        clear_btn = ctk.CTkButton(
            panel, 
            text="🗑️ ล้างข้อมูล", 
            command=self.clear_password_fields,
            height=40,
            corner_radius=15,
            font=ctk.CTkFont(size=14),
            fg_color="#FFE4E1",
            hover_color="#FFD1DC",
            text_color="#FF6B9D"
        )
        clear_btn.grid(row=row_counter + 1, column=0, sticky="ew", padx=30, pady=(0, 25))
    
    def clear_password_fields(self):
        """ล้างช่องกรอกรหัสผ่านทั้งหมด"""
        for entry in self.password_entries.values():
            entry.delete(0, 'end')

    def change_password(self):
        """เปลี่ยนรหัสผ่าน"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ", parent=self)
            return

        current_pass = self.password_entries['current_password'].get()
        new_pass = self.password_entries['new_password'].get()
        confirm_pass = self.password_entries['confirm_password'].get()

        # ตรวจสอบข้อมูล
        if not all([current_pass, new_pass, confirm_pass]):
            messagebox.showwarning(
                "ข้อมูลไม่ครบ", 
                "กรุณากรอกรหัสผ่านให้ครบทุกช่อง",
                parent=self
            )
            return
        
        if new_pass != confirm_pass:
            messagebox.showerror(
                "ผิดพลาด", 
                "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน",
                parent=self
            )
            return
        
        if len(new_pass) < 6:
            messagebox.showerror(
                "ผิดพลาด", 
                "รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร",
                parent=self
            )
            return
        
        if current_pass == new_pass:
            messagebox.showwarning(
                "คำเตือน", 
                "รหัสผ่านใหม่ไม่ควรเหมือนกับรหัสผ่านเก่า",
                parent=self
            )
            return
            
        # ตรวจสอบรหัสผ่านปัจจุบัน
        user_id = self.session.current_user.user_id
        user_data = self.db.get_user_by_id(user_id)
        
        if not user_data:
            messagebox.showerror("ผิดพลาด", "ไม่พบข้อมูลผู้ใช้", parent=self)
            return
        
        # ตรวจสอบรหัสผ่านปัจจุบัน
        if user_data['password'] != current_pass:
            messagebox.showerror(
                "ผิดพลาด", 
                "รหัสผ่านปัจจุบันไม่ถูกต้อง",
                parent=self
            )
            return
            
        # อัปเดตรหัสผ่านใหม่
        if self.db.update_user_password(user_id, new_pass):
            messagebox.showinfo(
                "สำเร็จ", 
                "✅ เปลี่ยนรหัสผ่านเรียบร้อยแล้ว",
                parent=self
            )
            # ล้างช่องรหัสผ่านทั้งหมด
            self.clear_password_fields()
        else:
            messagebox.showerror(
                "ผิดพลาด", 
                "ไม่สามารถเปลี่ยนรหัสผ่านได้ กรุณาลองใหม่อีกครั้ง",
                parent=self
            )