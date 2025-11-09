import customtkinter as ctk
from tkinter import messagebox, filedialog
import os
import time
from PIL import Image, ImageDraw

PROFILE_IMG_DIR = "assets/profile_images"

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db
        self.new_image = None
        
        # สร้างโฟลเดอร์รูปโปรไฟล์
        if not os.path.exists(PROFILE_IMG_DIR):
            os.makedirs(PROFILE_IMG_DIR)
    
    def on_show(self):
        """เปิดหน้านี้ - รีเฟรชข้อมูล"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_ui()
    
    def create_ui(self):
        """สร้างหน้าจอโปรไฟล์"""
        # ตรวจสอบ Login
        if not self.session.current_user:
            self.show_not_logged_in()
            return
        
        # ตั้งค่าขยายเต็มจอ
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # สร้างส่วนต่างๆ
        self.create_header()
        self.create_content()
    
    def show_not_logged_in(self):
        """แสดงข้อความยังไม่ Login"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)
        
        box = ctk.CTkFrame(self, fg_color="transparent")
        box.pack(expand=True)
        
        msg = ctk.CTkLabel(box, text="❌ คุณยังไม่ได้เข้าสู่ระบบ ❌",
                          font=ctk.CTkFont(size=24, weight="bold"),
                          text_color="#FF6B9D")
        msg.pack(padx=50, pady=(100, 20))
        
        btn = ctk.CTkButton(box, text="ไปหน้าล็อกอิน",
                           command=self.go_login,
                           font=ctk.CTkFont(size=16),
                           fg_color="#FFB6C1", hover_color="#FFC0CB",
                           text_color="white")
        btn.pack(pady=10, ipady=5)
    
    def create_header(self):
        """สร้างส่วนหัว"""
        header = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0,
                             height=70, border_width=1, border_color="#FFEBEE")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(header, text="👤 โปรไฟล์ของฉัน",
                            font=ctk.CTkFont(size=28, weight="bold"),
                            text_color="#FFB6C1")
        title.pack(side="left", padx=30, pady=20)
        
        back_btn = ctk.CTkButton(header, text="← กลับไปหน้าหลัก",
                                fg_color="transparent", text_color="#FFB6C1",
                                hover_color="#FFE4E1",
                                font=ctk.CTkFont(size=14),
                                command=self.go_home)
        back_btn.pack(side="right", padx=30, pady=20)
    
    def create_content(self):
        """สร้างเนื้อหาหลัก"""
        scroll = ctk.CTkScrollableFrame(self, fg_color="transparent",
                                        scrollbar_button_color="#FFB6C1",
                                        scrollbar_button_hover_color="#FFC0CB")
        scroll.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        scroll.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        
        self.create_profile_panel(scroll)
        self.create_password_panel(scroll)
    
    def create_profile_panel(self, parent):
        """สร้างแผงข้อมูลส่วนตัว"""
        panel = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=20,
                            border_width=2, border_color="#FFEBEE")
        panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        panel.grid_columnconfigure(0, weight=1)
        
        # หัวข้อ
        header = ctk.CTkFrame(panel, fg_color="#FFE4E1", corner_radius=15)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        title = ctk.CTkLabel(header, text="✨ ข้อมูลส่วนตัว",
                            font=ctk.CTkFont(size=20, weight="bold"),
                            text_color="#6D4C41")
        title.pack(pady=15)
        
        # ส่วนรูปโปรไฟล์
        user = self.session.current_user
        row = 1
        
        self.create_image_section(panel, user, row)
        row += 1
        
        # ช่องกรอกข้อมูล
        fields = {
            "full_name": "ชื่อ-นามสกุล:",
            "email": "อีเมล:",
            "phone": "เบอร์โทรศัพท์:",
            "address": "ที่อยู่สำหรับจัดส่ง:"
        }
        
        self.entries = {}
        
        for key, label in fields.items():
            row = self.add_field(panel, key, label, user, row)
        
        # ปุ่มบันทึก
        save_btn = ctk.CTkButton(panel, text="💾 บันทึกข้อมูลส่วนตัว",
                                command=self.save_profile,
                                height=50, corner_radius=15,
                                font=ctk.CTkFont(size=16, weight="bold"),
                                fg_color="#FFB6C1", hover_color="#FFC0CB",
                                text_color="white")
        save_btn.grid(row=row, column=0, sticky="ew", padx=30, pady=25)
    
    def create_image_section(self, parent, user, row):
        """สร้างส่วนรูปโปรไฟล์"""
        img_box = ctk.CTkFrame(parent, fg_color="#FFF0F5", corner_radius=15)
        img_box.grid(row=row, column=0, padx=30, pady=(15, 20), sticky="ew")
        img_box.grid_columnconfigure(1, weight=1)
        
        # โหลดและแสดงรูป
        self.load_image(user)
        
        self.img_label = ctk.CTkLabel(img_box, image=self.profile_img, text="")
        self.img_label.grid(row=0, column=0, padx=20, pady=15)
        
        # ข้อมูลข้างรูป
        info_box = ctk.CTkFrame(img_box, fg_color="transparent")
        info_box.grid(row=0, column=1, sticky="w", padx=10, pady=15)
        
        name = ctk.CTkLabel(info_box,
                           text=user.full_name or "ยังไม่ระบุชื่อ",
                           font=ctk.CTkFont(size=18, weight="bold"),
                           text_color="#FF6B9D")
        name.pack(anchor="w", pady=(0, 5))
        
        email = ctk.CTkLabel(info_box, text=user.email,
                            font=ctk.CTkFont(size=14),
                            text_color="#6D4C41")
        email.pack(anchor="w")
        
        # ปุ่มจัดการรูป
        btn_box = ctk.CTkFrame(img_box, fg_color="transparent")
        btn_box.grid(row=0, column=2, padx=20, pady=15)
        
        select_btn = ctk.CTkButton(btn_box, text="📷 เลือกรูปใหม่",
                                   command=self.select_image,
                                   width=140, height=35, corner_radius=15,
                                   font=ctk.CTkFont(size=14),
                                   fg_color="#FFC0CB", hover_color="#FFB6C1",
                                   text_color="white")
        select_btn.pack(pady=(0, 5))
        
        delete_btn = ctk.CTkButton(btn_box, text="🗑️ ลบรูป",
                                   command=self.remove_image,
                                   width=140, height=35, corner_radius=15,
                                   font=ctk.CTkFont(size=14),
                                   fg_color="#FFE4E1", hover_color="#FFD1DC",
                                   text_color="#FF6B9D")
        delete_btn.pack()
    
    def add_field(self, parent, key, label, user, row):
        """เพิ่มช่องกรอกข้อมูล"""
        # Label
        lbl = ctk.CTkLabel(parent, text=label,
                          font=ctk.CTkFont(size=14, weight="bold"),
                          text_color="#6D4C41")
        lbl.grid(row=row, column=0, padx=30, pady=(15, 5), sticky="w")
        
        # Entry
        if key == "address":
            entry = ctk.CTkTextbox(parent, height=100, corner_radius=15,
                                  border_width=2, border_color="#FFEBEE",
                                  fg_color="#FFFFFF",
                                  font=ctk.CTkFont(size=14))
            entry.insert("1.0", getattr(user, key) or "")
        else:
            entry = ctk.CTkEntry(parent, height=45, corner_radius=15,
                                border_width=2, border_color="#FFEBEE",
                                fg_color="#FFFFFF",
                                font=ctk.CTkFont(size=14))
            entry.insert(0, getattr(user, key) or "")
        
        # Email ไม่ให้แก้
        if key == "email":
            entry.configure(state="disabled", text_color="#999999")
        
        entry.grid(row=row + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
        self.entries[key] = entry
        
        return row + 2
    
    def load_image(self, user):
        """โหลดรูปโปรไฟล์"""
        size = (100, 100)
        default_path = 'assets/default_profile.png'
        
        try:
            # ลองโหลดรูปผู้ใช้
            if user.profile_image_url and user.profile_image_url != 'default_profile.png':
                img_path = os.path.join(PROFILE_IMG_DIR, user.profile_image_url)
                if os.path.exists(img_path):
                    img = Image.open(img_path)
                    img = self.make_circle(img, size)
                    self.profile_img = ctk.CTkImage(img, size=size)
                    return
            
            # ใช้รูป default
            if os.path.exists(default_path):
                img = Image.open(default_path)
                img = self.make_circle(img, size)
                self.profile_img = ctk.CTkImage(img, size=size)
            else:
                self.profile_img = self.make_placeholder(size)
        
        except Exception as e:
            print(f"โหลดรูปไม่สำเร็จ: {e}")
            self.profile_img = self.make_placeholder(size)
    
    def make_circle(self, img, size):
        """ทำรูปเป็นวงกลม"""
        img = img.resize(size, Image.LANCZOS)
        
        # สร้าง mask วงกลม
        mask = Image.new('L', size, 0)
        draw = ImageDraw.Draw(mask)
        draw.ellipse((0, 0) + size, fill=255)
        
        # ใส่ mask
        output = Image.new('RGBA', size, (255, 255, 255, 0))
        output.paste(img, (0, 0))
        output.putalpha(mask)
        
        return output
    
    def make_placeholder(self, size):
        """สร้างรูป placeholder"""
        img = Image.new('RGB', size, color='#FFB6C1')
        draw = ImageDraw.Draw(img)
        
        # วาดไอคอนผู้ใช้
        draw.ellipse([20, 20, 80, 80], fill='#FFFFFF')
        draw.ellipse([35, 30, 65, 60], fill='#FFB6C1')
        draw.ellipse([25, 55, 75, 95], fill='#FFB6C1')
        
        return ctk.CTkImage(img, size=size)
    
    def select_image(self):
        """เลือกรูปใหม่"""
        filetypes = [
            ("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"),
            ("All files", "*.*")
        ]
        
        path = filedialog.askopenfilename(title="เลือกรูปโปรไฟล์",
                                         filetypes=filetypes)
        
        if not path:
            return
        
        try:
            # ตรวจสอบขนาด (ไม่เกิน 5MB)
            size_mb = os.path.getsize(path) / (1024 * 1024)
            if size_mb > 5:
                messagebox.showwarning("ไฟล์ใหญ่เกินไป",
                                      "กรุณาเลือกรูปภาพที่มีขนาดไม่เกิน 5MB",
                                      parent=self)
                return
            
            # เก็บ path ชั่วคราว
            self.new_image = path
            
            # แสดงตัวอย่าง
            img = Image.open(path)
            img = self.make_circle(img, (100, 100))
            new_img = ctk.CTkImage(img, size=(100, 100))
            
            self.img_label.configure(image=new_img)
            self.img_label.image = new_img
            
            messagebox.showinfo("เลือกรูปภาพสำเร็จ",
                               "กรุณากดปุ่ม 'บันทึกข้อมูลส่วนตัว' เพื่อยืนยัน",
                               parent=self)
        
        except Exception as e:
            messagebox.showerror("ผิดพลาด",
                               f"ไม่สามารถโหลดรูปภาพได้: {str(e)}",
                               parent=self)
            self.new_image = None
    
    def remove_image(self):
        """ลบรูปโปรไฟล์"""
        confirm = messagebox.askyesno("ยืนยันการลบ",
                                     "คุณต้องการลบรูปโปรไฟล์และใช้รูป default หรือไม่?",
                                     parent=self)
        
        if not confirm:
            return
        
        self.new_image = "DELETE"
        
        # แสดงรูป default
        default_path = 'assets/default_profile.png'
        if os.path.exists(default_path):
            img = Image.open(default_path)
            img = self.make_circle(img, (100, 100))
            default_img = ctk.CTkImage(img, size=(100, 100))
        else:
            default_img = self.make_placeholder((100, 100))
        
        self.img_label.configure(image=default_img)
        self.img_label.image = default_img
        
        messagebox.showinfo("ลบรูปภาพสำเร็จ",
                           "กรุณากดปุ่ม 'บันทึกข้อมูลส่วนตัว' เพื่อยืนยัน",
                           parent=self)
    
    def save_profile(self):
        """บันทึกข้อมูลส่วนตัว"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ",
                               parent=self)
            return
        
        # รับข้อมูล
        full_name = self.entries['full_name'].get().strip()
        phone = self.entries['phone'].get().strip()
        address = self.entries['address'].get("1.0", "end-1c").strip()
        
        # ตรวจสอบ
        if not full_name:
            messagebox.showwarning("ข้อมูลไม่ครบ",
                                  "กรุณากรอกชื่อ-นามสกุล",
                                  parent=self)
            return
        
        if phone and not phone.replace("-", "").isdigit():
            messagebox.showwarning("ข้อมูลไม่ถูกต้อง",
                                  "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลขเท่านั้น",
                                  parent=self)
            return
        
        # จัดการรูป
        new_filename = self.handle_image_save()
        if new_filename is False:
            return
        
        # บันทึกลงฐานข้อมูล
        user_id = self.session.current_user.user_id
        
        if self.db.update_user_profile(user_id, full_name, phone, address, new_filename):
            # อัปเดต session
            self.session.current_user.full_name = full_name
            self.session.current_user.phone = phone
            self.session.current_user.address = address
            self.session.current_user.profile_image_url = new_filename
            
            messagebox.showinfo("สำเร็จ",
                               "✅ อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว",
                               parent=self)
            
            self.new_image = None
            self.on_show()
        else:
            messagebox.showerror("ผิดพลาด",
                               "ไม่สามารถอัปเดตข้อมูลได้ กรุณาลองใหม่อีกครั้ง",
                               parent=self)
    
    def handle_image_save(self):
        """จัดการบันทึกรูปภาพ"""
        current_filename = self.session.current_user.profile_image_url
        
        # ถ้าลบรูป
        if self.new_image == "DELETE":
            self.delete_old_image(current_filename)
            return None
        
        # ถ้าไม่มีรูปใหม่
        if not self.new_image:
            return current_filename
        
        # อัปโหลดรูปใหม่
        try:
            ext = os.path.splitext(self.new_image)[1].lower()
            if ext not in ['.png', '.jpg', '.jpeg', '.gif', '.bmp']:
                ext = '.png'
            
            user_id = self.session.current_user.user_id
            new_filename = f"profile_{user_id}_{int(time.time())}{ext}"
            dest_path = os.path.join(PROFILE_IMG_DIR, new_filename)
            
            # บันทึกไฟล์
            img = Image.open(self.new_image)
            img = img.convert('RGB')
            img.save(dest_path, quality=95)
            
            # ลบไฟล์เก่า
            self.delete_old_image(current_filename)
            
            return new_filename
        
        except Exception as e:
            messagebox.showerror("ผิดพลาด",
                               f"ไม่สามารถบันทึกรูปภาพได้: {str(e)}",
                               parent=self)
            return False
    
    def delete_old_image(self, filename):
        """ลบรูปเก่า"""
        if not filename or filename == 'default_profile.png':
            return
        
        old_path = os.path.join(PROFILE_IMG_DIR, filename)
        if os.path.exists(old_path):
            try:
                os.remove(old_path)
            except Exception as e:
                print(f"ลบรูปเก่าไม่สำเร็จ: {e}")
    
    def create_password_panel(self, parent):
        """สร้างแผงเปลี่ยนรหัสผ่าน"""
        panel = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=20,
                            border_width=2, border_color="#FFEBEE")
        panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        panel.grid_columnconfigure(0, weight=1)
        
        # หัวข้อ
        header = ctk.CTkFrame(panel, fg_color="#FFE4E1", corner_radius=15)
        header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        
        title = ctk.CTkLabel(header, text="🔒 เปลี่ยนรหัสผ่าน",
                            font=ctk.CTkFont(size=20, weight="bold"),
                            text_color="#6D4C41")
        title.pack(pady=15)
        
        # คำแนะนำ
        info = ctk.CTkLabel(panel,
                           text="💡 รหัสผ่านควรมีความยาวอย่างน้อย 6 ตัวอักษร\nและประกอบด้วยตัวอักษรและตัวเลข",
                           font=ctk.CTkFont(size=12),
                           text_color="#999999",
                           justify="left")
        info.grid(row=1, column=0, padx=30, pady=(0, 15), sticky="w")
        
        # ช่องกรอกรหัสผ่าน
        fields = {
            "current_password": "รหัสผ่านปัจจุบัน:",
            "new_password": "รหัสผ่านใหม่:",
            "confirm_password": "ยืนยันรหัสผ่านใหม่:"
        }
        
        self.pass_entries = {}
        row = 2
        
        for key, label in fields.items():
            row = self.add_password_field(panel, key, label, row)
        
        # ปุ่มเปลี่ยนรหัส
        change_btn = ctk.CTkButton(panel, text="🔐 เปลี่ยนรหัสผ่าน",
                                   command=self.change_password,
                                   height=50, corner_radius=15,
                                   font=ctk.CTkFont(size=16, weight="bold"),
                                   fg_color="#FF6B9D", hover_color="#FF8FB3",
                                   text_color="white")
        change_btn.grid(row=row, column=0, sticky="ew", padx=30, pady=25)
        
        # ปุ่มล้าง
        clear_btn = ctk.CTkButton(panel, text="🗑️ ล้างข้อมูล",
                                 command=self.clear_password,
                                 height=40, corner_radius=15,
                                 font=ctk.CTkFont(size=14),
                                 fg_color="#FFE4E1", hover_color="#FFD1DC",
                                 text_color="#FF6B9D")
        clear_btn.grid(row=row + 1, column=0, sticky="ew", padx=30, pady=(0, 25))
    
    def add_password_field(self, parent, key, label, row):
        """เพิ่มช่องกรอกรหัสผ่าน"""
        lbl = ctk.CTkLabel(parent, text=label,
                          font=ctk.CTkFont(size=14, weight="bold"),
                          text_color="#6D4C41")
        lbl.grid(row=row, column=0, padx=30, pady=(15, 5), sticky="w")
        
        entry_box = ctk.CTkFrame(parent, fg_color="transparent")
        entry_box.grid(row=row + 1, column=0, padx=30, pady=(0, 10), sticky="ew")
        entry_box.grid_columnconfigure(0, weight=1)
        
        entry = ctk.CTkEntry(entry_box, show="●", height=45, corner_radius=15,
                            border_width=2, border_color="#FFEBEE",
                            fg_color="#FFFFFF", font=ctk.CTkFont(size=14))
        entry.grid(row=0, column=0, sticky="ew")
        
        self.pass_entries[key] = entry
        return row + 2
    
    def clear_password(self):
        """ล้างช่องรหัสผ่าน"""
        for entry in self.pass_entries.values():
            entry.delete(0, 'end')
    
    def change_password(self):
        """เปลี่ยนรหัสผ่าน"""
        if not self.session.current_user:
            messagebox.showerror("ผิดพลาด", "คุณยังไม่ได้เข้าสู่ระบบ",
                               parent=self)
            return
        
        # รับข้อมูล
        current = self.pass_entries['current_password'].get()
        new = self.pass_entries['new_password'].get()
        confirm = self.pass_entries['confirm_password'].get()
        
        # ตรวจสอบ
        if not all([current, new, confirm]):
            messagebox.showwarning("ข้อมูลไม่ครบ",
                                  "กรุณากรอกรหัสผ่านให้ครบทุกช่อง",
                                  parent=self)
            return
        
        if new != confirm:
            messagebox.showerror("ผิดพลาด",
                               "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน",
                               parent=self)
            return
        
        if len(new) < 6:
            messagebox.showerror("ผิดพลาด",
                               "รหัสผ่านใหม่ต้องมีอย่างน้อย 6 ตัวอักษร",
                               parent=self)
            return
        
        if current == new:
            messagebox.showwarning("คำเตือน",
                                  "รหัสผ่านใหม่ไม่ควรเหมือนกับรหัสผ่านเก่า",
                                  parent=self)
            return
        
        # ตรวจสอบรหัสเก่า
        user_id = self.session.current_user.user_id
        user_data = self.db.get_user_by_id(user_id)
        
        if not user_data:
            messagebox.showerror("ผิดพลาด", "ไม่พบข้อมูลผู้ใช้",
                               parent=self)
            return
        
        if user_data['password'] != current:
            messagebox.showerror("ผิดพลาด",
                               "รหัสผ่านปัจจุบันไม่ถูกต้อง",
                               parent=self)
            return
        
        # อัปเดตรหัสใหม่
        if self.db.update_user_password(user_id, new):
            messagebox.showinfo("สำเร็จ",
                               "✅ เปลี่ยนรหัสผ่านเรียบร้อยแล้ว",
                               parent=self)
            self.clear_password()
        else:
            messagebox.showerror("ผิดพลาด",
                               "ไม่สามารถเปลี่ยนรหัสผ่านได้ กรุณาลองใหม่อีกครั้ง",
                               parent=self)
    
    def go_login(self):
        """ไปหน้า Login"""
        self.main_app.navigate_to('LoginWindow')
    
    def go_home(self):
        """กลับหน้าหลัก"""
        self.main_app.navigate_to('HomeWindow')