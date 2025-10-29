# M:/doll_shop/ui_profile.py (Updated with profile picture functionality)

import customtkinter as ctk
from tkinter import messagebox, filedialog
import bcrypt # Keep bcrypt for essential password checking
import os
import shutil
from datetime import datetime

class ProfileWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db

        self.validate_phone_cmd = self.register(self.validate_phone_input)

        # Variables for profile picture
        self.profile_image_display = None # The CTkLabel widget displaying the image
        self.profile_image_filename = None # Holds the *new* filename if user uploads one, otherwise None
        self.profile_entries = {} # Holds Entry/Textbox widgets for profile info
        self.password_entries = {} # Holds Entry widgets for password change

        self.setup_ui()

    def validate_phone_input(self, P):
        if P == "" or (P.isdigit() and len(P) <= 10):
            return True
        else:
            return False

    def on_show(self):
        """Refresh data and profile picture every time the page is shown."""
        self.profile_image_filename = None # Reset any newly selected image filename
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
        # Load and display the current profile image after UI is set up
        self.load_and_display_profile_image()

    def load_and_display_profile_image(self):
        """Load the current user's profile image from session and display it."""
        # Check if logged in and the image display widget exists
        if not self.session.is_logged_in():
            print("Not logged in, cannot load profile image.")
            # Optionally load default image if widget exists
            if hasattr(self, 'profile_image_display') and self.profile_image_display:
                 default_image = self.main_app.load_profile_image(None, size=(150, 150))
                 self.profile_image_display.configure(image=default_image)
                 self.profile_image_display.image = default_image # Keep reference
            return

        # Check if the display widget was created
        if not hasattr(self, 'profile_image_display') or not self.profile_image_display:
             print("Profile image display widget not yet created.")
             return # Cannot display image yet

        # Get current image filename from the logged-in user's data
        current_image_filename = getattr(self.session.current_user, 'profile_image_url', None)
        print(f"Loading profile image: {current_image_filename}")

        # Use main_app's function to load the image (handles default/errors)
        ctk_image = self.main_app.load_profile_image(current_image_filename, size=(150, 150)) # Larger size

        # Update the image in the CTkLabel
        self.profile_image_display.configure(image=ctk_image)
        # --- Keep a reference to prevent garbage collection ---
        self.profile_image_display.image = ctk_image

    def upload_profile_image(self):
        """Handle uploading a new profile image."""
        if not self.session.is_logged_in():
            messagebox.showwarning("ข้อผิดพลาด", "กรุณาเข้าสู่ระบบก่อนเปลี่ยนรูปโปรไฟล์", parent=self)
            return

        # Open file dialog
        filepath = filedialog.askopenfilename(
            title="เลือกรูปโปรไฟล์ใหม่",
            filetypes=(("ไฟล์รูปภาพ", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"), ("ทุกไฟล์", "*.*")),
            parent=self
        )
        if not filepath:
            return # User cancelled

        try:
            # Define target directory
            profile_pics_dir = os.path.join(self.main_app.base_path, "assets", "profile_pics")
            os.makedirs(profile_pics_dir, exist_ok=True) # Create if not exists

            # Create a unique filename
            user_id = self.session.current_user.user_id
            timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
            original_filename, file_extension = os.path.splitext(os.path.basename(filepath))
            if not file_extension: # Basic check for extension
                 messagebox.showerror("ผิดพลาด", "รูปแบบไฟล์รูปภาพไม่ถูกต้อง (ไม่มีนามสกุล)", parent=self)
                 return
            new_filename = f"user{user_id}_{timestamp}{file_extension.lower()}"
            destination_path = os.path.join(profile_pics_dir, new_filename)

            # Copy the file
            shutil.copy(filepath, destination_path)

            # --- Store the NEW filename to be saved later ---
            self.profile_image_filename = new_filename
            print(f"New profile image selected: {self.profile_image_filename}")

            # --- Show preview immediately ---
            ctk_image_preview = self.main_app.load_profile_image(self.profile_image_filename, size=(150, 150))
            if self.profile_image_display:
                self.profile_image_display.configure(image=ctk_image_preview)
                self.profile_image_display.image = ctk_image_preview # Keep reference

            messagebox.showinfo("เลือกรูปภาพ", "เลือกรูปภาพใหม่แล้ว กรุณากด 'บันทึกข้อมูลส่วนตัว' เพื่อยืนยัน", parent=self)

        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"ไม่สามารถอัปโหลดรูปภาพได้: {e}", parent=self)
            self.profile_image_filename = None # Reset filename on error

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้า Profile"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        # --- Header ---
        header_frame = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0, height=70, border_width=1, border_color="#FFEBEE")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        header_title = ctk.CTkLabel(header_frame, text="👤 โปรไฟล์ของฉัน", font=ctk.CTkFont(size=28, weight="bold"), text_color="#FFB6C1")
        header_title.pack(side="left", padx=30, pady=20)
        back_button = ctk.CTkButton(header_frame, text="< กลับไปหน้าหลัก", fg_color="transparent", text_color="#FFB6C1", hover_color="#FFE4E1", font=ctk.CTkFont(size=14), command=lambda: self.main_app.navigate_to('HomeWindow'))
        back_button.pack(side="right", padx=30, pady=20)

        # --- Main Content Frame ---
        content_frame = ctk.CTkFrame(self, fg_color="transparent")
        content_frame.grid(row=1, column=0, padx=30, pady=10, sticky="nsew")
        content_frame.grid_columnconfigure((0, 1), weight=1, uniform="group1")
        content_frame.grid_rowconfigure(0, weight=1)

        # --- Panel ซ้าย (ข้อมูลส่วนตัว + รูป) ---
        profile_panel = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        profile_panel.grid(row=0, column=0, sticky="nsew", padx=(0, 10), pady=10)
        profile_panel.grid_columnconfigure(0, weight=1)

        # --- ส่วนแสดงรูปและปุ่มอัปโหลด ---
        profile_pic_frame = ctk.CTkFrame(profile_panel, fg_color="transparent")
        profile_pic_frame.grid(row=0, column=0, pady=(20, 15)) # Place at the top

        # Label to display the image (initialized empty, loaded in on_show)
        self.profile_image_display = ctk.CTkLabel(profile_pic_frame, text="")
        self.profile_image_display.pack()

        upload_button = ctk.CTkButton(
            profile_pic_frame, text="เปลี่ยนรูปโปรไฟล์",
            height=30, corner_radius=10, font=("IBM Plex Sans Thai", 12),
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white",
            command=self.upload_profile_image # Calls the upload function
        )
        upload_button.pack(pady=(10, 0))

        # --- Header Panel ข้อมูลส่วนตัว ---
        profile_panel_header = ctk.CTkFrame(profile_panel, fg_color="#FFE4E1", corner_radius=15)
        profile_panel_header.grid(row=1, column=0, padx=20, pady=10, sticky="ew") # Row 1 now
        profile_panel_title = ctk.CTkLabel(profile_panel_header, text="✨ ข้อมูลส่วนตัว", font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41")
        profile_panel_title.pack(pady=15)

        # --- ช่องกรอกข้อมูล (Adjust row numbers) ---
        self.profile_entries = {}
        current_user_data = None
        is_logged_in = self.session.is_logged_in() # Check login status once
        if is_logged_in:
            current_user_data = self.session.current_user
        else:
            print("WARNING: Accessing Profile page while not logged in.")

        # Full Name
        label_fullname = ctk.CTkLabel(profile_panel, text="ชื่อ-นามสกุล:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_fullname.grid(row=2, column=0, padx=30, pady=(15, 5), sticky="w") # Start at row 2
        entry_fullname = ctk.CTkEntry(profile_panel, height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        if current_user_data: entry_fullname.insert(0, getattr(current_user_data, 'full_name', "") or "")
        entry_fullname.grid(row=3, column=0, padx=30, pady=(0, 10), sticky="ew") # Row 3
        self.profile_entries['full_name'] = entry_fullname

        # Email (Disabled)
        label_email = ctk.CTkLabel(profile_panel, text="อีเมล:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_email.grid(row=4, column=0, padx=30, pady=(15, 5), sticky="w") # Row 4
        entry_email = ctk.CTkEntry(profile_panel, height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        if current_user_data: entry_email.insert(0, getattr(current_user_data, 'email', "") or "")
        entry_email.configure(state="disabled", text_color="gray50")
        entry_email.grid(row=5, column=0, padx=30, pady=(0, 10), sticky="ew") # Row 5
        self.profile_entries['email'] = entry_email

        # Phone
        label_phone = ctk.CTkLabel(profile_panel, text="เบอร์โทรศัพท์ (ตัวเลข 10 หลัก):", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_phone.grid(row=6, column=0, padx=30, pady=(15, 5), sticky="w") # Row 6
        entry_phone = ctk.CTkEntry(
            profile_panel, height=45, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5",
            font=ctk.CTkFont(size=14), validate="key", validatecommand=(self.validate_phone_cmd, '%P')
        )
        if current_user_data: entry_phone.insert(0, getattr(current_user_data, 'phone', "") or "")
        entry_phone.grid(row=7, column=0, padx=30, pady=(0, 10), sticky="ew") # Row 7
        self.profile_entries['phone'] = entry_phone

        # Address
        label_address = ctk.CTkLabel(profile_panel, text="ที่อยู่สำหรับจัดส่ง:", font=ctk.CTkFont(size=14), text_color="#6D4C41")
        label_address.grid(row=8, column=0, padx=30, pady=(15, 5), sticky="w") # Row 8
        entry_address = ctk.CTkTextbox(profile_panel, height=100, corner_radius=15, border_width=1, border_color="#FFEBEE", fg_color="#FFF0F5", font=ctk.CTkFont(size=14))
        if current_user_data: entry_address.insert("1.0", getattr(current_user_data, 'address', "") or "")
        entry_address.grid(row=9, column=0, padx=30, pady=(0, 10), sticky="ew") # Row 9
        self.profile_entries['address'] = entry_address

        # Save Button
        save_profile_button = ctk.CTkButton(
            profile_panel, text="💾 บันทึกข้อมูลส่วนตัว", command=self.save_profile,
            height=45, corner_radius=15, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FFB6C1", hover_color="#FFC0CB", text_color="white"
        )
        save_profile_button.configure(state="normal" if is_logged_in else "disabled") # Disable if not logged in
        save_profile_button.grid(row=10, column=0, sticky="ew", padx=30, pady=25) # Row 10

        # --- Panel ขวา (เปลี่ยนรหัสผ่าน) (Adjust row numbers) ---
        password_panel = ctk.CTkFrame(content_frame, fg_color="#FFFFFF", corner_radius=20, border_width=2, border_color="#FFEBEE")
        password_panel.grid(row=0, column=1, sticky="nsew", padx=(10, 0), pady=10)
        password_panel.grid_columnconfigure(0, weight=1)
        password_panel_header = ctk.CTkFrame(password_panel, fg_color="#FFE4E1", corner_radius=15)
        password_panel_header.grid(row=0, column=0, padx=20, pady=20, sticky="ew")
        password_panel_title = ctk.CTkLabel(password_panel_header, text="🔒 เปลี่ยนรหัสผ่าน", font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41")
        password_panel_title.pack(pady=15)
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

        change_password_button = ctk.CTkButton(
            password_panel, text="🔐 เปลี่ยนรหัสผ่าน", command=self.change_password,
            height=45, corner_radius=15, font=ctk.CTkFont(size=16, weight="bold"),
            fg_color="#FF6B9D", hover_color="#FF8FB3", text_color="white"
        )
        change_password_button.configure(state="normal" if is_logged_in else "disabled") # Disable if not logged in
        change_password_button.grid(row=7, column=0, sticky="ew", padx=30, pady=25)


    def save_profile(self):
        """บันทึกข้อมูลส่วนตัวที่แก้ไข (รวมรูปโปรไฟล์)"""
        if not self.session.is_logged_in():
             messagebox.showerror("ข้อผิดพลาด", "กรุณาเข้าสู่ระบบก่อนบันทึกข้อมูล", parent=self)
             return

        # Get data from entries
        full_name_input = self.profile_entries['full_name'].get().strip()
        phone_input = self.profile_entries['phone'].get().strip()
        address_input = self.profile_entries['address'].get("1.0", "end-1c").strip()

        # Determine the profile image filename to save
        profile_image_to_save = self.profile_image_filename # Use the newly uploaded filename if available
        if not profile_image_to_save:
            # Otherwise, use the existing filename from the session
            profile_image_to_save = getattr(self.session.current_user, 'profile_image_url', None)

        # Basic Validation
        if phone_input and (not phone_input.isdigit() or len(phone_input) != 10):
             messagebox.showwarning("เบอร์โทรศัพท์ไม่ถูกต้อง", "กรุณากรอกเบอร์โทรศัพท์เป็นตัวเลข 10 หลัก", parent=self)
             return
        if not full_name_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล", parent=self)
            return

        # Update Database
        current_user_id = self.session.current_user.user_id
        update_success = self.db.update_user_profile(
            current_user_id,
            full_name_input,
            phone_input,
            address_input,
            profile_image_to_save # Pass the determined image filename
        )

        # Handle Result
        if update_success:
            # --- Update session data ---
            self.session.current_user.full_name = full_name_input
            self.session.current_user.phone = phone_input
            self.session.current_user.address = address_input
            self.session.current_user.profile_image_url = profile_image_to_save # Update image URL in session
            messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลส่วนตัวเรียบร้อยแล้ว", parent=self)
            self.on_show() # Refresh the page (will reload image)
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลส่วนตัวได้ โปรดลองอีกครั้ง", parent=self)

    def change_password(self):
        """เปลี่ยนรหัสผ่าน"""
        if not self.session.is_logged_in():
             messagebox.showerror("ข้อผิดพลาด", "กรุณาเข้าสู่ระบบก่อนเปลี่ยนรหัสผ่าน", parent=self)
             return

        current_password_input = self.password_entries['current_password'].get()
        new_password_input = self.password_entries['new_password'].get()
        confirm_password_input = self.password_entries['confirm_password'].get()

        # Validation
        if not current_password_input or not new_password_input or not confirm_password_input:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกรหัสผ่านให้ครบทุกช่อง", parent=self)
            return
        if new_password_input != confirm_password_input:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่และการยืนยันไม่ตรงกัน", parent=self)
            return
        if len(new_password_input) < 8:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านใหม่ต้องมีอย่างน้อย 8 ตัวอักษร", parent=self)
            return

        current_user_id = self.session.current_user.user_id
        user_data_from_db = self.db.get_user_by_id(current_user_id)

        # Check current password
        password_correct = False
        if user_data_from_db:
             try:
                 # Try bcrypt first (assuming hashed passwords in DB)
                 current_password_bytes = current_password_input.encode('utf-8')
                 hashed_password_from_db = user_data_from_db['password'] # This should be bytes
                 if isinstance(hashed_password_from_db, str): # Handle if DB stores plain text
                     password_correct = (hashed_password_from_db == current_password_input)
                 elif isinstance(hashed_password_from_db, bytes):
                     password_correct = bcrypt.checkpw(current_password_bytes, hashed_password_from_db)
                 else:
                     password_correct = False # Cannot compare if type is wrong
             except Exception as e:
                 print(f"Error checking password during change: {e}")
                 # Fallback check for plain text if bcrypt fails unexpectedly
                 if isinstance(user_data_from_db.get('password'), str):
                     password_correct = (user_data_from_db['password'] == current_password_input)
                 else:
                     password_correct = False

        if not password_correct:
            messagebox.showerror("ผิดพลาด", "รหัสผ่านปัจจุบันไม่ถูกต้อง", parent=self)
            return

        # Update password in DB
        update_success = self.db.update_user_password(current_user_id, new_password_input) # DB handles hashing or storing plain

        if update_success:
            messagebox.showinfo("สำเร็จ", "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว", parent=self)
            for entry_widget in self.password_entries.values():
                entry_widget.delete(0, 'end')
        else:
            messagebox.showerror("ผิดพลาด", "ไม่สามารถเปลี่ยนรหัสผ่านได้ โปรดลองอีกครั้ง", parent=self)