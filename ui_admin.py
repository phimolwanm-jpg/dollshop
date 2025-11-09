import customtkinter as ctk
from tkinter import ttk, messagebox, filedialog
from PIL import Image
import os
import shutil

class AdminWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.db = main_app.db
        self.selected_product_id = None
        self.image_filename = None 
        
        # self.entries จะถูกเติมค่าใน 'create_right_panel'
        self.entries = {} 
        self.tree = None
        self.image_label = None

        # เริ่มสร้าง UI และโหลดข้อมูล
        self.setup_ui() 
        self.load_products_to_treeview() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ล้างฟอร์ม, โหลดข้อมูลตารางใหม่
        """
        self.clear_form() 
        self.load_products_to_treeview()

    # ============================================
    # ===== 1. "ผู้จัดการ" สร้าง UI หลัก =====
    # ============================================

    def setup_ui(self):
        """
        ฟังก์ชันหลักสำหรับสร้าง UI
        ทำหน้าที่เป็น "ผู้จัดการ" เรียกฟังก์ชันย่อยมาทำงาน
        """
        # คอลัมน์ 0 (ตาราง) กว้าง 3 ส่วน, คอลัมน์ 1 (ฟอร์ม) กว้าง 2 ส่วน
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=2)
        # แถวที่ 1 (เนื้อหาหลัก) ให้ขยายตามแนวตั้ง
        self.grid_rowconfigure(1, weight=1)    

        # เรียก "ผู้ช่วย" มาสร้างทีละส่วน
        self.create_header()
        self.create_left_panel()
        self.create_right_panel()

    # ============================================
    # ===== 2. "ผู้ช่วย" สร้างส่วนประกอบ UI =====
    # ============================================

    def create_header(self):
        """สร้างส่วนหัว (Header)"""
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=20, sticky="ew") 
        
        ctk.CTkLabel(
            header_frame, 
            text="⚙️ จัดการสินค้าในร้าน", 
            font=ctk.CTkFont(size=28, weight="bold")
        ).pack(side="left")
        
        ctk.CTkButton(
            header_frame, 
            text="< กลับไปหน้าหลัก", 
            fg_color="transparent", 
            text_color="gray50", 
            hover=False,
            command=lambda: self.main_app.navigate_to('HomeWindow')
        ).pack(side="right")

    def create_left_panel(self):
        """สร้าง Panel ด้านซ้าย (รายการสินค้า และ ตาราง Treeview)"""
        list_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        list_frame.grid(row=1, column=0, padx=(30, 10), pady=10, sticky="nsew") 
        list_frame.grid_propagate(False) 
        list_frame.grid_rowconfigure(1, weight=1)
        list_frame.grid_columnconfigure(0, weight=1) 

        ctk.CTkLabel(
            list_frame, 
            text="รายการสินค้าทั้งหมด", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # === สร้างตาราง Treeview ===
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("Treeview", rowheight=30, font=('Arial', 12))
        
        columns = ("id", "name", "category", "price", "stock")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview") 

        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ชื่อสินค้า")
        self.tree.heading("category", text="หมวดหมู่")
        self.tree.heading("price", text="ราคา")
        self.tree.heading("stock", text="สต็อก")
        
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w")
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("price", width=100, anchor="e")
        self.tree.column("stock", width=80, anchor="center")
        
        self.tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=10) 
        self.tree.bind("<<TreeviewSelect>>", self.on_product_select) 

    def create_right_panel(self):
        """สร้าง Panel ด้านขวา (ฟอร์มกรอกข้อมูล)"""
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        form_frame.grid(row=1, column=1, padx=(10, 30), pady=10, sticky="nsew") 
        form_frame.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            form_frame, 
            text="เพิ่ม / แก้ไขข้อมูลสินค้า", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # === สร้างฟอร์ม ===
        form_fields_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_fields_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_fields_container.grid_columnconfigure(1, weight=1) 
        
        # === ใช้ฟังก์ชัน Helper สร้างช่องกรอกที่ทำซ้ำๆ ===
        # เราจะเก็บ widget ที่ return กลับมาไว้ใน self.entries
        self.entries['name']     = self._create_form_field(form_fields_container, 0, "ชื่อสินค้า:")
        self.entries['category'] = self._create_form_field(form_fields_container, 1, "หมวดหมู่:")
        self.entries['price']    = self._create_form_field(form_fields_container, 2, "ราคา:")
        self.entries['stock']    = self._create_form_field(form_fields_container, 3, "จำนวน:")
        
        # === สร้างช่อง "คำอธิบาย" (ใช้ Textbox) ===
        label_desc = ctk.CTkLabel(form_fields_container, text="คำอธิบาย:")
        label_desc.grid(row=4, column=0, padx=5, pady=10, sticky="nw") # 'nw' = ชิดซ้ายบน
        entry_desc = ctk.CTkTextbox(form_fields_container, height=100)
        entry_desc.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        self.entries['description'] = entry_desc
        
        # === สร้างส่วน "เลือกรูปภาพ" ===
        label_image = ctk.CTkLabel(form_fields_container, text="รูปภาพ:")
        label_image.grid(row=5, column=0, padx=5, pady=10, sticky="w")
        self.image_label = ctk.CTkLabel(form_fields_container, text="ยังไม่ได้เลือกรูปภาพ", text_color="gray") 
        self.image_label.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        ctk.CTkButton(
            form_fields_container, 
            text="เลือกรูปภาพ", 
            command=self.upload_image
        ).grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        # === สร้าง "ปุ่มควบคุม" (บันทึก, เคลียร์, ลบ) ===
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15) 
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1) 

        ctk.CTkButton(btn_frame, text="💾 บันทึก", command=self.save_product, height=40).grid(row=0, column=0, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="✨ เคลียร์ฟอร์ม", command=self.clear_form, fg_color="gray50", height=40).grid(row=0, column=1, padx=5, sticky="ew")
        ctk.CTkButton(btn_frame, text="🗑️ ลบ", command=self.delete_product, fg_color="#D22B2B", hover_color="#8B0000", height=40).grid(row=0, column=2, padx=5, sticky="ew")

    def _create_form_field(self, parent, row, label_text):
        """
        (ฟังก์ชันผู้ช่วย) สร้าง Label และ Entry 1 แถว
        """
        label = ctk.CTkLabel(parent, text=label_text)
        label.grid(row=row, column=0, padx=5, pady=10, sticky="w")
        entry = ctk.CTkEntry(parent)
        entry.grid(row=row, column=1, padx=5, pady=10, sticky="ew")
        return entry # คืนค่า widget ของ entry เพื่อให้ข้างนอกเก็บ
        
    # ============================================
    # ===== 3. ฟังก์ชันจัดการข้อมูล (Data) =====
    # ============================================

    def load_products_to_treeview(self):
        """ล้างตาราง และ โหลดข้อมูลสินค้าทั้งหมดจาก DB มาใส่"""
        if not self.tree: # ป้องกัน error ถ้า tree ยังไม่ถูกสร้าง
            return
            
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        products = self.db.get_all_products()
        for p_dict in products: 
            self.tree.insert("", "end", values=(
                p_dict['product_id'], 
                p_dict['name'], 
                p_dict['category'], 
                f"{p_dict['price']:.2f}",
                p_dict['stock']
            ))

    def on_product_select(self, event):
        """
        ทำงานเมื่อคลิกเลือกแถวในตาราง
        ดึงข้อมูลจาก DB และเติมลงในฟอร์ม
        """
        selected_items = self.tree.selection()
        if not selected_items:
            return
        
        item_data = self.tree.item(selected_items[0])
        product_id_from_tree = item_data['values'][0]
        
        self.selected_product_id = product_id_from_tree
        
        product_data_from_db = self.db.get_product_by_id(self.selected_product_id)
        
        if not product_data_from_db:
            self.clear_form()
            return
        
        #เรียกฟังก์ชันย่อยมาเติมข้อมูล
        self._populate_form(product_data_from_db)

    def _populate_form(self, data: dict):
        """(ฟังก์ชันผู้ช่วย) เติมข้อมูลจาก dict ลงในฟอร์ม"""
        self.entries['name'].delete(0, 'end')
        self.entries['name'].insert(0, data['name'])
        
        self.entries['category'].delete(0, 'end')
        self.entries['category'].insert(0, data['category'])
        
        self.entries['price'].delete(0, 'end')
        self.entries['price'].insert(0, data['price'])
        
        self.entries['stock'].delete(0, 'end')
        self.entries['stock'].insert(0, data['stock'])
        
        self.entries['description'].delete("1.0", 'end')
        self.entries['description'].insert("1.0", data.get('description', "")) 
        
        self.image_filename = data.get('image_url')
        display_text = self.image_filename if self.image_filename else "ไม่มีรูปภาพ"
        self.image_label.configure(text=display_text)

    # ============================================
    # ===== 4. ฟังก์ชันจัดการปุ่ม (Actions) =====
    # ============================================

    def upload_image(self):
        """เปิดหน้าต่างเลือกไฟล์ และ คัดลอกไฟล์มาเก็บใน 'assets/images'"""
        filepath = filedialog.askopenfilename(
            title="เลือกรูปภาพสินค้า", 
            filetypes=(("Image files", "*.jpg *.jpeg *.png *.gif *.bmp *.webp"), ("All files", "*.*")), 
            parent=self 
        )
        if not filepath:
            return

        filename = os.path.basename(filepath) 
        
        # ใช้ self.main_app.base_path (จาก main.py) จะชัวร์กว่า
        images_dir = os.path.join(self.main_app.base_path, "assets", "images")
        os.makedirs(images_dir, exist_ok=True) 
        
        destination_path = os.path.join(images_dir, filename)
        
        src_path = os.path.abspath(filepath).lower()
        dst_path = os.path.abspath(destination_path).lower()
        
        if src_path != dst_path:
            try:
                shutil.copy(filepath, destination_path) 
                messagebox.showinfo("สำเร็จ", f"อัปโหลดรูปภาพ '{filename}' เรียบร้อย!", parent=self)
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถคัดลอกไฟล์ได้: {e}", parent=self)
                return
        else:
            messagebox.showinfo("แจ้งเตือน", "ไฟล์นี้อยู่ในโฟลเดอร์ปลายทางอยู่แล้ว", parent=self)
        
        self.image_filename = filename 
        self.image_label.configure(text=self.image_filename) 

    def save_product(self):
        """
        บันทึกข้อมูล (ทั้งสร้างใหม่ หรือ อัปเดต)
        """
        try:
            #  เรียกฟังก์ชันย่อยมาดึงข้อมูล
            form_data = self._get_form_data()
            if not form_data:
                return # หยุดทำงานถ้าข้อมูลไม่ครบ หรือ ผิดพลาด

            # ใช้ชื่อไฟล์รูปภาพที่เก็บไว้
            form_data['image_url'] = self.image_filename if self.image_filename else ""

            # --- เช็คว่าเป็นการ "แก้ไข" หรือ "สร้างใหม่" ---
            if self.selected_product_id: 
                # = แก้ไข =
                success = self.db.update_product(
                    self.selected_product_id, # ID ที่จะแก้ไข
                    form_data['name'], form_data['description'], 
                    form_data['price'], form_data['stock'], 
                    form_data['category'], form_data['image_url']
                )
                if success:
                    messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลสินค้าเรียบร้อย!", parent=self)
                else:
                    messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลสินค้าได้", parent=self)
                    return 
            else:
                # = สร้างใหม่ =
                new_product_id = self.db.create_product(
                    form_data['name'], form_data['description'], 
                    form_data['price'], form_data['stock'], 
                    form_data['category'], form_data['image_url']
                )
                if new_product_id:
                    messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าใหม่เรียบร้อย!", parent=self)
                else:
                     messagebox.showerror("ผิดพลาด", "ไม่สามารถเพิ่มสินค้าใหม่ได้", parent=self)
                     return 
            
            self.on_show() # Refresh หน้าจอ
            
        except ValueError: 
            messagebox.showerror("ผิดพลาด", "ราคาและจำนวนสต็อกต้องเป็นตัวเลขเท่านั้น", parent=self)
        except Exception as e: 
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}", parent=self)

    def _get_form_data(self):
        """
        (ฟังก์ชันผู้ช่วย) ดึงข้อมูลจากฟอร์ม, ตรวจสอบ, และแปลงประเภท
        """
        # (ValueError จะถูกดักจับโดย save_product ที่เรียกใช้)
        data = {
            'name': self.entries['name'].get().strip(),
            'category': self.entries['category'].get().strip(),
            'price': float(self.entries['price'].get()),
            'stock': int(self.entries['stock'].get()),
            'description': self.entries['description'].get("1.0", "end-1c").strip()
        }

        # ตรวจสอบว่ากรอกข้อมูลที่จำเป็นครบหรือไม่
        if not data['name'] or not data['category']:
            messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อและหมวดหมู่สินค้า", parent=self)
            return None # คืนค่า None ถ้าข้อมูลไม่ครบ

        return data

    def delete_product(self):
        """ลบสินค้า (หลังจากยืนยัน)"""
        if not self.selected_product_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกสินค้าที่ต้องการลบ", parent=self)
            return
            
        if messagebox.askyesno("ยืนยันการลบ", "คุณแน่ใจหรือไม่ว่าต้องการลบสินค้านี้?", parent=self):
            success = self.db.delete_product(self.selected_product_id)
            if success:
                messagebox.showinfo("สำเร็จ", "ลบสินค้าเรียบร้อยแล้ว", parent=self)
                self.on_show() # Refresh หน้าจอ
            else:
                 messagebox.showerror("ผิดพลาด", "ไม่สามารถลบสินค้าได้", parent=self)

    def clear_form(self):
        """ล้างฟอร์มทั้งหมด และ รีเซ็ตค่า"""
        self.selected_product_id = None 
        self.image_filename = None 
        
        if self.tree:
            current_selection = self.tree.selection()
            if current_selection:
                self.tree.selection_remove(current_selection)

        # ล้างค่าในช่องกรอก
        for key, entry_widget in self.entries.items():
            if isinstance(entry_widget, ctk.CTkTextbox):
                entry_widget.delete("1.0", 'end')
            elif isinstance(entry_widget, ctk.CTkEntry):
                entry_widget.delete(0, 'end')
        
        if self.image_label:
            self.image_label.configure(text="ยังไม่ได้เลือกรูปภาพ")