# สร้างไฟล์ใหม่ชื่อ: ui_admin_users.py
import customtkinter as ctk
from tkinter import ttk, messagebox

class AdminUsersWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA") # สีพื้นหลังเดียวกับ Dashboard
        self.main_app = main_app
        self.db = main_app.db
        self.selected_user_id = None
        
        self.setup_ui()
        self.load_users_to_treeview()

    def on_show(self):
        """ทำงานทุกครั้งที่เปิดหน้านี้"""
        self.clear_form()
        self.load_users_to_treeview()

    def setup_ui(self):
        # --- 1. กำหนด Grid หลัก (เหมือนหน้า Admin สินค้า) ---
        self.grid_columnconfigure(0, weight=3) # 3 ส่วนสำหรับตาราง
        self.grid_columnconfigure(1, weight=2) # 2 ส่วนสำหรับฟอร์ม
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้าง Header ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=20, sticky="ew")
        
        header_label = ctk.CTkLabel(header_frame, text="👥 จัดการข้อมูลผู้ใช้", font=ctk.CTkFont(size=28, weight="bold"), text_color="#FF9800") # สีส้ม
        header_label.pack(side="left")
        
        # ปุ่มกลับไป Dashboard
        back_button = ctk.CTkButton(header_frame, text="< กลับไป Dashboard", fg_color="transparent", text_color="gray50", hover=False,
                                    command=lambda: self.main_app.navigate_to('AdminDashboardWindow'))
        back_button.pack(side="right")

        # --- 3. Panel ด้านซ้าย (รายการผู้ใช้) ---
        list_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        list_frame.grid(row=1, column=0, padx=(30, 10), pady=10, sticky="nsew")
        list_frame.grid_propagate(False)
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        list_title = ctk.CTkLabel(list_frame, text="รายการผู้ใช้ทั้งหมด", font=ctk.CTkFont(size=18, weight="bold"))
        list_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # --- 3.1 สร้างตาราง Treeview ---
        style = ttk.Style()
        style.configure("Users.Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("Users.Treeview", rowheight=35, font=('Arial', 12))
        
        columns = ("id", "username", "full_name", "email", "role")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Users.Treeview")

        self.tree.heading("id", text="ID")
        self.tree.heading("username", text="Username")
        self.tree.heading("full_name", text="ชื่อ-นามสกุล")
        self.tree.heading("email", text="อีเมล")
        self.tree.heading("role", text="บทบาท")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("username", width=120, anchor="w")
        self.tree.column("full_name", width=180, anchor="w")
        self.tree.column("email", width=200, anchor="w")
        self.tree.column("role", width=100, anchor="center")
        
        self.tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # ผูก event คลิกเลือกแถว
        self.tree.bind("<<TreeviewSelect>>", self.on_user_select)

        # --- 4. Panel ด้านขวา (ฟอร์มแก้ไข) ---
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_frame.grid(row=1, column=1, padx=(10, 30), pady=10, sticky="nsew")
        form_frame.grid_columnconfigure(0, weight=1)

        form_title = ctk.CTkLabel(form_frame, text="แก้ไขข้อมูลผู้ใช้", font=ctk.CTkFont(size=18, weight="bold"))
        form_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # --- 4.1 สร้างฟอร์ม ---
        form_fields_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_fields_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_fields_container.grid_columnconfigure(1, weight=1)
        
        self.entries = {} # Dictionary เก็บ Entry widgets

        # Username (แสดงผลอย่างเดียว, แก้ไขไม่ได้)
        ctk.CTkLabel(form_fields_container, text="Username:").grid(row=0, column=0, padx=5, pady=10, sticky="w")
        self.username_label = ctk.CTkLabel(form_fields_container, text="-", font=ctk.CTkFont(weight="bold"))
        self.username_label.grid(row=0, column=1, padx=5, pady=10, sticky="w")

        # ชื่อ-นามสกุล
        ctk.CTkLabel(form_fields_container, text="ชื่อ-นามสกุล:").grid(row=1, column=0, padx=5, pady=10, sticky="w")
        entry_name = ctk.CTkEntry(form_fields_container)
        entry_name.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.entries['full_name'] = entry_name

        # อีเมล
        ctk.CTkLabel(form_fields_container, text="อีเมล:").grid(row=2, column=0, padx=5, pady=10, sticky="w")
        entry_email = ctk.CTkEntry(form_fields_container)
        entry_email.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.entries['email'] = entry_email
        
        # เบอร์โทร
        ctk.CTkLabel(form_fields_container, text="เบอร์โทร:").grid(row=3, column=0, padx=5, pady=10, sticky="w")
        entry_phone = ctk.CTkEntry(form_fields_container)
        entry_phone.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        self.entries['phone'] = entry_phone

        # ที่อยู่
        ctk.CTkLabel(form_fields_container, text="ที่อยู่:").grid(row=4, column=0, padx=5, pady=10, sticky="nw")
        entry_address = ctk.CTkTextbox(form_fields_container, height=100)
        entry_address.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        self.entries['address'] = entry_address
        
        # บทบาท (Role) - ใช้ OptionMenu
        ctk.CTkLabel(form_fields_container, text="บทบาท:").grid(row=5, column=0, padx=5, pady=10, sticky="w")
        self.role_var = ctk.StringVar(value="customer") # ค่าเริ่มต้น
        role_menu = ctk.CTkOptionMenu(
            form_fields_container,
            values=["customer", "admin"],
            variable=self.role_var
        )
        role_menu.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        self.entries['role_menu'] = role_menu # เก็บไว้เพื่ออ้างอิง

        # --- 4.2 สร้างปุ่มควบคุม (บันทึก, เคลียร์, ลบ) ---
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15)
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1)

        save_button = ctk.CTkButton(btn_frame, text="💾 บันทึกการแก้ไข", command=self.save_user, height=40, fg_color="#4CAF50")
        save_button.grid(row=0, column=0, padx=5, sticky="ew")
        
        clear_button = ctk.CTkButton(btn_frame, text="✨ เคลียร์ฟอร์ม", command=self.clear_form, fg_color="gray50", height=40)
        clear_button.grid(row=0, column=1, padx=5, sticky="ew")
        
        delete_button = ctk.CTkButton(btn_frame, text="🗑️ ลบผู้ใช้", command=self.delete_user, fg_color="#D22B2B", hover_color="#8B0000", height=40)
        delete_button.grid(row=0, column=2, padx=5, sticky="ew")

    def load_users_to_treeview(self):
        """โหลดข้อมูลผู้ใช้ทั้งหมดจาก DB มาใส่ตาราง"""
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        users = self.db.get_all_users() # ดึงผู้ใช้ทั้งหมด
        
        for user in users:
            # (ป้องกันไม่ให้แอดมินแก้ไข/ลบตัวเองโดยบังเอิญในฟอร์มนี้)
            # if user['username'] == 'admin':
            #     continue 
                
            self.tree.insert("", "end", values=(
                user['user_id'], 
                user['username'], 
                user['full_name'], 
                user['email'], 
                user['role']
            ))

    def on_user_select(self, event):
        """เมื่อคลิกเลือกผู้ใช้ในตาราง"""
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item_data = self.tree.item(selected_items[0])
        user_id_from_tree = item_data['values'][0]
        
        self.selected_user_id = user_id_from_tree
        
        # ดึงข้อมูลผู้ใช้จาก DB (เพื่อให้ได้ข้อมูลครบถ้วน เช่น ที่อยู่)
        user_data = self.db.get_user_by_id(self.selected_user_id)
        
        if not user_data:
            self.clear_form()
            return
            
        # --- เติมข้อมูลลงฟอร์ม ---
        self.username_label.configure(text=user_data.get('username', '-'))
        
        self.entries['full_name'].delete(0, 'end')
        self.entries['full_name'].insert(0, user_data.get('full_name', ''))
        
        self.entries['email'].delete(0, 'end')
        self.entries['email'].insert(0, user_data.get('email', ''))
        
        self.entries['phone'].delete(0, 'end')
        self.entries['phone'].insert(0, user_data.get('phone', ''))
        
        self.entries['address'].delete("1.0", 'end')
        self.entries['address'].insert("1.0", user_data.get('address', ''))
        
        # ตั้งค่า Dropdown 'role'
        self.role_var.set(user_data.get('role', 'customer'))

    def save_user(self):
        """บันทึกการแก้ไขข้อมูลผู้ใช้"""
        if not self.selected_user_id:
            messagebox.showwarning("ยังไม่ได้เลือก", "กรุณาเลือกผู้ใช้ที่ต้องการแก้ไขจากตาราง", parent=self)
            return
            
        # ดึงข้อมูลจากฟอร์ม
        try:
            full_name = self.entries['full_name'].get().strip()
            email = self.entries['email'].get().strip()
            phone = self.entries['phone'].get().strip()
            address = self.entries['address'].get("1.0", "end-1c").strip()
            role = self.role_var.get()
            
            if not full_name or not email:
                messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อ-นามสกุล และอีเมล", parent=self)
                return

            # (ป้องกันไม่ให้แอดมินเปลี่ยนบทบาทตัวเอง)
            user_data = self.db.get_user_by_id(self.selected_user_id)
            if user_data.get('username') == 'admin' and role != 'admin':
                messagebox.showerror("ผิดพลาด", "ไม่สามารถเปลี่ยนบทบาทของ 'admin' หลักได้", parent=self)
                self.role_var.set('admin') # ตั้งค่ากลับ
                return

            # เรียกฟังก์ชัน DB (ที่เรามีอยู่แล้วใน database.py)
            success = self.db.update_user_details_admin(
                self.selected_user_id,
                email, full_name, phone, address, role
            )
            
            if success:
                messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลผู้ใช้เรียบร้อย!", parent=self)
                self.on_show() # รีเฟรชหน้า
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลได้ (อาจมีอีเมลซ้ำ)", parent=self)
                
        except Exception as e:
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}", parent=self)

    def delete_user(self):
        """ลบผู้ใช้"""
        if not self.selected_user_id:
            messagebox.showwarning("ยังไม่ได้เลือก", "กรุณาเลือกผู้ใช้ที่ต้องการลบ", parent=self)
            return

        # (ป้องกันไม่ให้แอดมินลบตัวเอง)
        user_data = self.db.get_user_by_id(self.selected_user_id)
        if user_data.get('username') == 'admin':
            messagebox.showerror("ผิดพลาด", "ไม่สามารถลบผู้ใช้ 'admin' หลักของระบบได้", parent=self)
            return

        if messagebox.askyesno("ยืนยันการลบ", f"คุณแน่ใจหรือไม่ว่าต้องการลบผู้ใช้ ID: {self.selected_user_id}?", parent=self):
            success = self.db.delete_user(self.selected_user_id)
            if success:
                messagebox.showinfo("สำเร็จ", "ลบผู้ใช้เรียบร้อยแล้ว", parent=self)
                self.on_show() # รีเฟรชหน้า
            else:
                messagebox.showerror("ผิดพลาด", "ไม่สามารถลบผู้ใช้ได้ (อาจมีคำสั่งซื้อผูกอยู่)", parent=self)

    def clear_form(self):
        """ล้างข้อมูลในฟอร์มและยกเลิกการเลือก"""
        self.selected_user_id = None
        
        current_selection = self.tree.selection()
        if current_selection:
            self.tree.selection_remove(current_selection)

        self.username_label.configure(text="-")
        self.entries['full_name'].delete(0, 'end')
        self.entries['email'].delete(0, 'end')
        self.entries['phone'].delete(0, 'end')
        self.entries['address'].delete("1.0", 'end')
        self.role_var.set("customer") # รีเซ็ตเป็นค่าเริ่มต้น