"""
หน้าจัดการผู้ใช้ (Admin Users Window)
- แสดงรายการผู้ใช้ทั้งหมด
- แก้ไขข้อมูลผู้ใช้
- เปลี่ยนบทบาท (customer/admin)
- ลบผู้ใช้
"""

import customtkinter as ctk
from tkinter import ttk, messagebox


class AdminUsersWindow(ctk.CTkFrame):
    """หน้าจอจัดการผู้ใช้"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.db = main_app.db
        
        # ตัวแปรเก็บ ID ผู้ใช้ที่เลือก
        self.selected_user_id = None
        
        # สร้าง UI
        self.create_page()
        
        # โหลดข้อมูลผู้ใช้
        self.load_all_users()
    
    
    def on_show(self):
        """ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เปิดหน้านี้"""
        self.clear_form()
        self.load_all_users()
    
    
    def create_page(self):
        """สร้างโครงสร้างหน้าจอ"""
        # ตั้งค่าการขยาย
        self.grid_columnconfigure(0, weight=3)  # ตารางผู้ใช้ (60%)
        self.grid_columnconfigure(1, weight=2)  # ฟอร์มแก้ไข (40%)
        self.grid_rowconfigure(1, weight=1)
        
        # สร้างส่วนต่างๆ
        self.create_header()           # หัวข้อด้านบน
        self.create_user_table()       # ตารางผู้ใช้ (ซ้าย)
        self.create_edit_form()        # ฟอร์มแก้ไข (ขวา)
    
    
    # ==================== หัวข้อด้านบน ====================
    def create_header(self):
        """สร้างส่วนหัวข้อ"""
        header = ctk.CTkFrame(self, fg_color="transparent")
        header.grid(row=0, column=0, columnspan=2, padx=30, pady=20, sticky="ew")
        
        # หัวข้อ
        title = ctk.CTkLabel(
            header,
            text="👥 จัดการข้อมูลผู้ใช้",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FF9800"
        )
        title.pack(side="left")
        
        # ปุ่มกลับ
        btn_back = ctk.CTkButton(
            header,
            text="< กลับไป Dashboard",
            fg_color="transparent",
            text_color="gray50",
            hover=False,
            command=self.go_back
        )
        btn_back.pack(side="right")
    
    
    def go_back(self):
        """กลับไปหน้า Dashboard"""
        self.main_app.navigate_to('AdminDashboardWindow')
    
    
    # ==================== ตารางผู้ใช้ (ซ้าย) ====================
    def create_user_table(self):
        """สร้างส่วนตารางรายการผู้ใช้"""
        # กรอบตาราง
        table_box = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        table_box.grid(row=1, column=0, padx=(30, 10), pady=10, sticky="nsew")
        table_box.grid_propagate(False)
        table_box.grid_rowconfigure(1, weight=1)
        table_box.grid_columnconfigure(0, weight=1)
        
        # หัวข้อ
        title = ctk.CTkLabel(
            table_box,
            text="รายการผู้ใช้ทั้งหมด",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # ตั้งค่าสไตล์ตาราง
        style = ttk.Style()
        style.configure("Users.Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("Users.Treeview", rowheight=35, font=('Arial', 12))
        
        # คอลัมน์ตาราง
        columns = ("id", "username", "full_name", "email", "role")
        
        # สร้างตาราง
        self.table = ttk.Treeview(
            table_box,
            columns=columns,
            show="headings",
            style="Users.Treeview"
        )
        
        # ตั้งหัวตาราง
        self.table.heading("id", text="ID")
        self.table.heading("username", text="Username")
        self.table.heading("full_name", text="ชื่อ-นามสกุล")
        self.table.heading("email", text="อีเมล")
        self.table.heading("role", text="บทบาท")
        
        # ตั้งความกว้างคอลัมน์
        self.table.column("id", width=50, anchor="center")
        self.table.column("username", width=120, anchor="w")
        self.table.column("full_name", width=180, anchor="w")
        self.table.column("email", width=200, anchor="w")
        self.table.column("role", width=100, anchor="center")
        
        self.table.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # ผูก event เมื่อคลิกเลือกแถว
        self.table.bind("<<TreeviewSelect>>", self.on_select_user)
    
    
    # ==================== ฟอร์มแก้ไข (ขวา) ====================
    def create_edit_form(self):
        """สร้างฟอร์มแก้ไขข้อมูลผู้ใช้"""
        # กรอบฟอร์ม
        form_box = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_box.grid(row=1, column=1, padx=(10, 30), pady=10, sticky="nsew")
        form_box.grid_columnconfigure(0, weight=1)
        
        # หัวข้อ
        title = ctk.CTkLabel(
            form_box,
            text="แก้ไขข้อมูลผู้ใช้",
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # พื้นที่ฟอร์ม
        form_area = ctk.CTkFrame(form_box, fg_color="transparent")
        form_area.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_area.grid_columnconfigure(1, weight=1)
        
        # Dictionary เก็บช่องกรอกข้อมูล
        self.inputs = {}
        
        # Username (แสดงอย่างเดียว ไม่ให้แก้)
        self.create_label(form_area, "Username:", row=0)
        self.username_display = ctk.CTkLabel(
            form_area,
            text="-",
            font=ctk.CTkFont(weight="bold")
        )
        self.username_display.grid(row=0, column=1, padx=5, pady=10, sticky="w")
        
        # ชื่อ-นามสกุล
        self.create_label(form_area, "ชื่อ-นามสกุล:", row=1)
        input_name = ctk.CTkEntry(form_area)
        input_name.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.inputs['full_name'] = input_name
        
        # อีเมล
        self.create_label(form_area, "อีเมล:", row=2)
        input_email = ctk.CTkEntry(form_area)
        input_email.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.inputs['email'] = input_email
        
        # เบอร์โทร
        self.create_label(form_area, "เบอร์โทร:", row=3)
        input_phone = ctk.CTkEntry(form_area)
        input_phone.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        self.inputs['phone'] = input_phone
        
        # ที่อยู่
        self.create_label(form_area, "ที่อยู่:", row=4, sticky="nw")
        input_address = ctk.CTkTextbox(form_area, height=100)
        input_address.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        self.inputs['address'] = input_address
        
        # บทบาท (Dropdown)
        self.create_label(form_area, "บทบาท:", row=5)
        self.role_choice = ctk.StringVar(value="customer")
        role_dropdown = ctk.CTkOptionMenu(
            form_area,
            values=["customer", "admin"],
            variable=self.role_choice
        )
        role_dropdown.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        
        # สร้างปุ่มควบคุม
        self.create_control_buttons(form_box)
    
    
    def create_label(self, parent, text, row, sticky="w"):
        """สร้าง Label สำหรับฟอร์ม"""
        label = ctk.CTkLabel(parent, text=text)
        label.grid(row=row, column=0, padx=5, pady=10, sticky=sticky)
        return label
    
    
    def create_control_buttons(self, parent):
        """สร้างปุ่มควบคุมฟอร์ม"""
        button_area = ctk.CTkFrame(parent, fg_color="transparent")
        button_area.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        button_area.grid_columnconfigure((0, 1, 2), weight=1)
        
        # ปุ่มบันทึก
        btn_save = ctk.CTkButton(
            button_area,
            text="💾 บันทึกการแก้ไข",
            command=self.save_changes,
            height=40,
            fg_color="#4CAF50"
        )
        btn_save.grid(row=0, column=0, padx=5, sticky="ew")
        
        # ปุ่มเคลียร์
        btn_clear = ctk.CTkButton(
            button_area,
            text="✨ เคลียร์ฟอร์ม",
            command=self.clear_form,
            fg_color="gray50",
            height=40
        )
        btn_clear.grid(row=0, column=1, padx=5, sticky="ew")
        
        # ปุ่มลบ
        btn_delete = ctk.CTkButton(
            button_area,
            text="🗑️ ลบผู้ใช้",
            command=self.delete_user,
            fg_color="#D22B2B",
            hover_color="#8B0000",
            height=40
        )
        btn_delete.grid(row=0, column=2, padx=5, sticky="ew")
    
    
    # ==================== ฟังก์ชันการทำงาน ====================
    def load_all_users(self):
        """โหลดข้อมูลผู้ใช้ทั้งหมดมาแสดงในตาราง"""
        # ลบข้อมูลเก่าในตาราง
        for item in self.table.get_children():
            self.table.delete(item)
        
        # ดึงข้อมูลจาก database
        users = self.db.get_all_users()
        
        # ใส่ข้อมูลลงตาราง
        for user in users:
            self.table.insert("", "end", values=(
                user['user_id'],
                user['username'],
                user['full_name'],
                user['email'],
                user['role']
            ))
    
    
    def on_select_user(self, event):
        """เมื่อคลิกเลือกผู้ใช้ในตาราง"""
        # เช็คว่ามีการเลือกหรือไม่
        selected = self.table.selection()
        if not selected:
            return
        
        # ดึงข้อมูลจากแถวที่เลือก
        item_data = self.table.item(selected[0])
        user_id = item_data['values'][0]
        
        # เก็บ ID ไว้
        self.selected_user_id = user_id
        
        # ดึงข้อมูลผู้ใช้ทั้งหมดจาก database
        user_info = self.db.get_user_by_id(user_id)
        
        if not user_info:
            self.clear_form()
            return
        
        # แสดงข้อมูลในฟอร์ม
        self.fill_form_with_data(user_info)
    
    
    def fill_form_with_data(self, user_info):
        """เติมข้อมูลผู้ใช้ลงในฟอร์ม"""
        # Username (แสดงอย่างเดียว)
        username = user_info.get('username', '-')
        self.username_display.configure(text=username)
        
        # ชื่อ-นามสกุล
        self.inputs['full_name'].delete(0, 'end')
        self.inputs['full_name'].insert(0, user_info.get('full_name', ''))
        
        # อีเมล
        self.inputs['email'].delete(0, 'end')
        self.inputs['email'].insert(0, user_info.get('email', ''))
        
        # เบอร์โทร
        self.inputs['phone'].delete(0, 'end')
        self.inputs['phone'].insert(0, user_info.get('phone', ''))
        
        # ที่อยู่
        self.inputs['address'].delete("1.0", 'end')
        self.inputs['address'].insert("1.0", user_info.get('address', ''))
        
        # บทบาท
        role = user_info.get('role', 'customer')
        self.role_choice.set(role)
    
    
    def save_changes(self):
        """บันทึกการแก้ไขข้อมูล"""
        # เช็คว่าเลือกผู้ใช้แล้วหรือยัง
        if not self.selected_user_id:
            messagebox.showwarning(
                "ยังไม่ได้เลือก",
                "กรุณาเลือกผู้ใช้ที่ต้องการแก้ไขจากตาราง",
                parent=self
            )
            return
        
        try:
            # ดึงข้อมูลจากฟอร์ม
            full_name = self.inputs['full_name'].get().strip()
            email = self.inputs['email'].get().strip()
            phone = self.inputs['phone'].get().strip()
            address = self.inputs['address'].get("1.0", "end-1c").strip()
            role = self.role_choice.get()
            
            # ตรวจสอบข้อมูลที่จำเป็น
            if not full_name or not email:
                messagebox.showwarning(
                    "ข้อมูลไม่ครบ",
                    "กรุณากรอกชื่อ-นามสกุล และอีเมล",
                    parent=self
                )
                return
            
            # ป้องกันไม่ให้เปลี่ยนบทบาท admin หลัก
            user_data = self.db.get_user_by_id(self.selected_user_id)
            if user_data.get('username') == 'admin' and role != 'admin':
                messagebox.showerror(
                    "ผิดพลาด",
                    "ไม่สามารถเปลี่ยนบทบาทของ 'admin' หลักได้",
                    parent=self
                )
                self.role_choice.set('admin')  # ตั้งค่ากลับ
                return
            
            # บันทึกลง database
            success = self.db.update_user_details_admin(
                self.selected_user_id,
                email,
                full_name,
                phone,
                address,
                role
            )
            
            if success:
                messagebox.showinfo(
                    "สำเร็จ",
                    "อัปเดตข้อมูลผู้ใช้เรียบร้อย!",
                    parent=self
                )
                self.on_show()  # รีเฟรชหน้า
            else:
                messagebox.showerror(
                    "ผิดพลาด",
                    "ไม่สามารถอัปเดตข้อมูลได้ (อาจมีอีเมลซ้ำ)",
                    parent=self
                )
        
        except Exception as e:
            messagebox.showerror(
                "ผิดพลาด",
                f"เกิดข้อผิดพลาด: {e}",
                parent=self
            )
    
    
    def delete_user(self):
        """ลบผู้ใช้"""
        # เช็คว่าเลือกผู้ใช้แล้วหรือยัง
        if not self.selected_user_id:
            messagebox.showwarning(
                "ยังไม่ได้เลือก",
                "กรุณาเลือกผู้ใช้ที่ต้องการลบ",
                parent=self
            )
            return
        
        # ป้องกันไม่ให้ลบ admin หลัก
        user_data = self.db.get_user_by_id(self.selected_user_id)
        if user_data.get('username') == 'admin':
            messagebox.showerror(
                "ผิดพลาด",
                "ไม่สามารถลบผู้ใช้ 'admin' หลักของระบบได้",
                parent=self
            )
            return
        
        # ถามยืนยัน
        confirm = messagebox.askyesno(
            "ยืนยันการลบ",
            f"คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้ ID: {self.selected_user_id}?",
            parent=self
        )
        
        if confirm:
            success = self.db.delete_user(self.selected_user_id)
            
            if success:
                messagebox.showinfo(
                    "สำเร็จ",
                    "ลบผู้ใช้เรียบร้อยแล้ว",
                    parent=self
                )
                self.on_show()  # รีเฟรชหน้า
            else:
                messagebox.showerror(
                    "ผิดพลาด",
                    "ไม่สามารถลบผู้ใช้ได้ (อาจมีคำสั่งซื้อผูกอยู่)",
                    parent=self
                )
    
    
    def clear_form(self):
        """ล้างข้อมูลในฟอร์ม"""
        # เคลียร์ ID ที่เลือก
        self.selected_user_id = None
        
        # ยกเลิกการเลือกในตาราง
        selected = self.table.selection()
        if selected:
            self.table.selection_remove(selected)
        
        # ล้างข้อมูลในฟอร์ม
        self.username_display.configure(text="-")
        self.inputs['full_name'].delete(0, 'end')
        self.inputs['email'].delete(0, 'end')
        self.inputs['phone'].delete(0, 'end')
        self.inputs['address'].delete("1.0", 'end')
        self.role_choice.set("customer")