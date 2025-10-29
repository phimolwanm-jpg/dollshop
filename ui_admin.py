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
        self.image_filename = None # เก็บชื่อไฟล์รูปภาพ
        self.setup_ui() # สร้างหน้าจอ UI ทั้งหมด
        self.load_products_to_treeview() # โหลดข้อมูลสินค้าใส่ตาราง

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ล้างฟอร์ม, โหลดข้อมูลตารางใหม่
        """
        self.clear_form() 
        self.load_products_to_treeview()

    def setup_ui(self):
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # คอลัมน์ 0 (ตาราง) กว้าง 3 ส่วน, คอลัมน์ 1 (ฟอร์ม) กว้าง 2 ส่วน
        self.grid_columnconfigure(0, weight=3) 
        self.grid_columnconfigure(1, weight=2)
        # แถวที่ 1 (เนื้อหาหลัก) ให้ขยายตามแนวตั้ง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        # columnspan=2 คือให้ header กินพื้นที่ทั้ง 2 คอลัมน์
        header_frame.grid(row=0, column=0, columnspan=2, padx=30, pady=20, sticky="ew") 
        
        header_label = ctk.CTkLabel(header_frame, text="⚙️ จัดการสินค้าในร้าน", font=ctk.CTkFont(size=28, weight="bold"))
        header_label.pack(side="left")
        
        # ปุ่มกลับหน้าหลัก
        back_button = ctk.CTkButton(header_frame, text="< กลับไปหน้าหลัก", fg_color="transparent", text_color="gray50", hover=False,
                                    command=lambda: self.main_app.navigate_to('HomeWindow'))
        back_button.pack(side="right")

        # --- 3. สร้าง Panel ด้านซ้าย (รายการสินค้า) ---
        list_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        # วาง list_frame ลงใน แถว 1, คอลัมน์ 0
        list_frame.grid(row=1, column=0, padx=(30, 10), pady=10, sticky="nsew") 
        # grid_propagate(False) ป้องกันไม่ให้ frame หดตาม widget ข้างใน
        list_frame.grid_propagate(False) 
        list_frame.grid_rowconfigure(1, weight=1)    # ให้แถวที่ 1 (ตาราง) ขยายได้
        list_frame.grid_columnconfigure(0, weight=1) # ให้คอลัมน์ที่ 0 (ตาราง) ขยายได้

        list_title = ctk.CTkLabel(list_frame, text="รายการสินค้าทั้งหมด", font=ctk.CTkFont(size=18, weight="bold"))
        list_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # --- 3.1 สร้างตาราง Treeview ---
        style = ttk.Style()
        style.configure("Treeview.Heading", font=('Arial', 14, 'bold'))
        style.configure("Treeview", rowheight=30, font=('Arial', 12))
        
        columns = ("id", "name", "category", "price", "stock")
        # สร้าง Treeview ใส่ใน list_frame
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", style="Treeview") 

        # ตั้งชื่อหัวตาราง
        self.tree.heading("id", text="ID")
        self.tree.heading("name", text="ชื่อสินค้า")
        self.tree.heading("category", text="หมวดหมู่")
        self.tree.heading("price", text="ราคา")
        self.tree.heading("stock", text="สต็อก")
        
        # ตั้งค่าความกว้างคอลัมน์
        self.tree.column("id", width=50, anchor="center")
        self.tree.column("name", width=250, anchor="w") # anchor="w" คือชิดซ้าย
        self.tree.column("category", width=120, anchor="w")
        self.tree.column("price", width=100, anchor="e") # anchor="e" คือชิดขวา
        self.tree.column("stock", width=80, anchor="center")
        
        # วาง Treeview ลงใน list_frame (แถว 1, คอลัมน์ 0)
        self.tree.grid(row=1, column=0, sticky="nsew", padx=20, pady=10) 
        
        # ผูก event: ถ้าคลิกเลือกแถวในตาราง ให้ไปเรียกฟังก์ชัน on_product_select
        self.tree.bind("<<TreeviewSelect>>", self.on_product_select) 
        # --- จบส่วนสร้าง Treeview ---

        # --- 4. สร้าง Panel ด้านขวา (ฟอร์มกรอกข้อมูล) ---
        form_frame = ctk.CTkFrame(self, fg_color="white", corner_radius=15)
        # วาง form_frame ลงใน แถว 1, คอลัมน์ 1
        form_frame.grid(row=1, column=1, padx=(10, 30), pady=10, sticky="nsew") 
        form_frame.grid_columnconfigure(0, weight=1) # ให้คอลัมน์เดียวใน form ขยายได้

        form_title = ctk.CTkLabel(form_frame, text="เพิ่ม / แก้ไขข้อมูลสินค้า", font=ctk.CTkFont(size=18, weight="bold"))
        form_title.grid(row=0, column=0, padx=20, pady=15, sticky="w")
        
        # --- 4.1 สร้างฟอร์ม ---
        form_fields_container = ctk.CTkFrame(form_frame, fg_color="transparent")
        form_fields_container.grid(row=1, column=0, padx=20, pady=10, sticky="nsew")
        form_fields_container.grid_columnconfigure(1, weight=1) # ให้คอลัมน์ช่องกรอกขยายได้
        
        # เก็บ Entry widgets ไว้ใน dictionary เพื่อใช้อ้างอิงทีหลัง
        self.entries = {} 

        # --- ช่องกรอก "ชื่อสินค้า" (เขียนตรงๆ) ---
        label_name = ctk.CTkLabel(form_fields_container, text="ชื่อสินค้า:")
        label_name.grid(row=0, column=0, padx=5, pady=10, sticky="w")
        entry_name = ctk.CTkEntry(form_fields_container)
        entry_name.grid(row=0, column=1, padx=5, pady=10, sticky="ew")
        self.entries['name'] = entry_name # เก็บ entry ไว้

        # --- ช่องกรอก "หมวดหมู่" (เขียนตรงๆ) ---
        label_category = ctk.CTkLabel(form_fields_container, text="หมวดหมู่:")
        label_category.grid(row=1, column=0, padx=5, pady=10, sticky="w")
        entry_category = ctk.CTkEntry(form_fields_container)
        entry_category.grid(row=1, column=1, padx=5, pady=10, sticky="ew")
        self.entries['category'] = entry_category

        # --- ช่องกรอก "ราคา" (เขียนตรงๆ) ---
        label_price = ctk.CTkLabel(form_fields_container, text="ราคา:")
        label_price.grid(row=2, column=0, padx=5, pady=10, sticky="w")
        entry_price = ctk.CTkEntry(form_fields_container)
        entry_price.grid(row=2, column=1, padx=5, pady=10, sticky="ew")
        self.entries['price'] = entry_price

        # --- ช่องกรอก "จำนวน" (เขียนตรงๆ) ---
        label_stock = ctk.CTkLabel(form_fields_container, text="จำนวน:")
        label_stock.grid(row=3, column=0, padx=5, pady=10, sticky="w")
        entry_stock = ctk.CTkEntry(form_fields_container)
        entry_stock.grid(row=3, column=1, padx=5, pady=10, sticky="ew")
        self.entries['stock'] = entry_stock

        # --- ช่องกรอก "คำอธิบาย" (ใช้ Textbox) (เขียนตรงๆ) ---
        label_desc = ctk.CTkLabel(form_fields_container, text="คำอธิบาย:")
        label_desc.grid(row=4, column=0, padx=5, pady=10, sticky="w")
        entry_desc = ctk.CTkTextbox(form_fields_container, height=100)
        entry_desc.grid(row=4, column=1, padx=5, pady=10, sticky="ew")
        self.entries['description'] = entry_desc
        
        # --- ส่วนเลือกรูปภาพ ---
        label_image = ctk.CTkLabel(form_fields_container, text="รูปภาพ:")
        label_image.grid(row=5, column=0, padx=5, pady=10, sticky="w")
        # Label แสดงชื่อไฟล์รูป (เริ่มต้นเป็นข้อความ)
        self.image_label = ctk.CTkLabel(form_fields_container, text="ยังไม่ได้เลือกรูปภาพ", text_color="gray") 
        self.image_label.grid(row=5, column=1, padx=5, pady=10, sticky="w")
        # ปุ่มกดเพื่อเลือกไฟล์
        upload_btn = ctk.CTkButton(form_fields_container, text="เลือกรูปภาพ", command=self.upload_image) 
        upload_btn.grid(row=6, column=1, padx=5, pady=5, sticky="w")
        
        # --- 4.2 สร้างปุ่มควบคุม (บันทึก, เคลียร์, ลบ) ---
        btn_frame = ctk.CTkFrame(form_frame, fg_color="transparent")
        # วาง btn_frame ใต้ form_fields_container (แถว 2)
        btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=15) 
        # แบ่งเป็น 3 คอลัมน์เท่าๆ กัน
        btn_frame.grid_columnconfigure((0, 1, 2), weight=1) 

        # ปุ่มบันทึก
        save_button = ctk.CTkButton(btn_frame, text="💾 บันทึก", command=self.save_product, height=40)
        save_button.grid(row=0, column=0, padx=5, sticky="ew")
        # ปุ่มเคลียร์ฟอร์ม
        clear_button = ctk.CTkButton(btn_frame, text="✨ เคลียร์ฟอร์ม", command=self.clear_form, fg_color="gray50", height=40)
        clear_button.grid(row=0, column=1, padx=5, sticky="ew")
        # ปุ่มลบ
        delete_button = ctk.CTkButton(btn_frame, text="🗑️ ลบ", command=self.delete_product, fg_color="#D22B2B", hover_color="#8B0000", height=40)
        delete_button.grid(row=0, column=2, padx=5, sticky="ew")
        # --- จบส่วนสร้าง Form ---

    def load_products_to_treeview(self):
        # ล้างข้อมูลเก่าในตาราง
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # ดึงข้อมูลสินค้าทั้งหมดจาก DB
        products = self.db.get_all_products()
        # วนลูปเพื่อเพิ่มข้อมูลทีละแถว
        for p_dict in products: # p_dict เป็น dictionary อยู่แล้ว
            self.tree.insert(
                "", # parent item (ใส่ "" คืออยู่ระดับบนสุด)
                "end", # ตำแหน่งที่จะใส่ (end คือต่อท้าย)
                # ค่าที่จะใส่ในแต่ละคอลัมน์ (ต้องตรงลำดับกับ columns ตอนสร้าง tree)
                values=(
                    p_dict['product_id'], 
                    p_dict['name'], 
                    p_dict['category'], 
                    f"{p_dict['price']:.2f}", # จัดรูปแบบราคา
                    p_dict['stock']
                )
            )

    def on_product_select(self, event):
        # เอาแถวที่ถูกเลือก (อาจมีหลายแถว แต่เราเอาแค่แถวแรก)
        selected_items = self.tree.selection()
        if not selected_items: # ถ้าไม่มีแถวไหนถูกเลือก ก็ไม่ต้องทำอะไร
            return
        
        # ดึงข้อมูลจากแถวที่เลือก (แถวแรก)
        item_data = self.tree.item(selected_items[0])
        product_id_from_tree = item_data['values'][0] # ID อยู่คอลัมน์แรก (index 0)
        
        # เก็บ ID ที่เลือกไว้ในตัวแปรของคลาส
        self.selected_product_id = product_id_from_tree
        
        # ใช้ ID ไปดึงข้อมูลสินค้าทั้งหมดจาก DB อีกครั้ง (เพื่อให้ได้ description, image_url)
        product_data_from_db = self.db.get_product_by_id(self.selected_product_id)
        
        # ถ้าหาข้อมูลจาก DB ไม่เจอ (อาจถูกลบไปแล้ว) ให้เคลียร์ฟอร์ม
        if not product_data_from_db:
            self.clear_form()
            return
        
        # --- เติมข้อมูลลงในช่องกรอก ---
        # ชื่อสินค้า
        self.entries['name'].delete(0, 'end') # ลบของเก่าก่อน
        self.entries['name'].insert(0, product_data_from_db['name']) # เพิ่มของใหม่
        # หมวดหมู่
        self.entries['category'].delete(0, 'end')
        self.entries['category'].insert(0, product_data_from_db['category'])
        # ราคา
        self.entries['price'].delete(0, 'end')
        self.entries['price'].insert(0, product_data_from_db['price'])
        # จำนวน
        self.entries['stock'].delete(0, 'end')
        self.entries['stock'].insert(0, product_data_from_db['stock'])
        # คำอธิบาย (ใช้ index "1.0" สำหรับ Textbox)
        self.entries['description'].delete("1.0", 'end')
        # ใช้ .get() เพื่อป้องกันกรณี description เป็น None
        self.entries['description'].insert("1.0", product_data_from_db.get('description', "")) 
        
        # อัปเดตชื่อไฟล์รูปภาพ และ Label ที่แสดง
        self.image_filename = product_data_from_db.get('image_url')
        display_text = self.image_filename if self.image_filename else "ไม่มีรูปภาพ"
        self.image_label.configure(text=display_text)

    def upload_image(self):
        # เปิดหน้าต่างให้เลือกไฟล์รูป
        filepath = filedialog.askopenfilename(
            title="เลือกรูปภาพสินค้า", 
            # กำหนดประเภทไฟล์ที่เลือกได้
            filetypes=(("ไฟล์รูปภาพ", "*.jpg *.jpeg *.png"), ("ทุกไฟล์", "*.*")), 
            parent=self # ให้หน้าต่างนี้เป็น parent (เพื่อให้ focus ถูกต้อง)
        )
        # ถ้าผู้ใช้กด Cancel (filepath จะเป็น None หรือ "") ก็ไม่ต้องทำอะไร
        if not filepath:
            return

        # เอาเฉพาะชื่อไฟล์จาก path เต็ม (เช่น "my_image.png")
        filename = os.path.basename(filepath) 
        
        # สร้าง path ไปยังโฟลเดอร์ที่จะเก็บรูป ("assets/images" ในโปรเจกต์)
        # os.path.dirname(__file__) คือ path ของโฟลเดอร์ที่ไฟล์ ui_admin.py นี้อยู่
        images_dir = os.path.join(os.path.dirname(__file__), "assets", "images")
        
        # สร้างโฟลเดอร์ assets/images ถ้ายังไม่มี
        os.makedirs(images_dir, exist_ok=True) 
        
        # สร้าง path ปลายทางเต็มๆ ที่จะคัดลอกไฟล์ไป
        destination_path = os.path.join(images_dir, filename)
        
        # --- ป้องกันการคัดลอกไฟล์ทับตัวเอง ---
        # แปลง path ทั้งสองเป็น absolute path และตัวพิมพ์เล็กเพื่อเปรียบเทียบ
        src_path = os.path.abspath(filepath).lower()
        dst_path = os.path.abspath(destination_path).lower()
        
        # ถ้า path ต้นทางกับปลายทางไม่เหมือนกัน ถึงจะคัดลอก
        if src_path != dst_path:
            try:
                # คัดลอกไฟล์
                shutil.copy(filepath, destination_path) 
                messagebox.showinfo("สำเร็จ", f"อัปโหลดรูปภาพ '{filename}' เรียบร้อย!", parent=self)
            except Exception as e:
                messagebox.showerror("ผิดพลาด", f"ไม่สามารถคัดลอกไฟล์ได้: {e}", parent=self)
                return # ถ้าคัดลอกไม่ได้ ก็ไม่ต้องทำต่อ
        else:
            # ถ้าเป็นไฟล์เดียวกัน ก็แค่แจ้งเตือน
            messagebox.showinfo("แจ้งเตือน", "ไฟล์นี้อยู่ในโฟลเดอร์ปลายทางอยู่แล้ว", parent=self)
        
        # เก็บ *แค่ชื่อไฟล์* ไว้ในตัวแปร (เดี๋ยวจะใช้ตอน save_product)
        self.image_filename = filename 
        # อัปเดต Label ให้แสดงชื่อไฟล์ที่เลือก
        self.image_label.configure(text=self.image_filename) 

    def save_product(self):
        # ใช้ try...except ดักจับ error เวลาแปลงข้อมูล (เช่น กรอกราคาไม่ใช่ตัวเลข)
        try:
            # ดึงข้อมูลจากช่องกรอก และ .strip() เพื่อตัดช่องว่างหน้า/หลัง
            name = self.entries['name'].get().strip()
            category = self.entries['category'].get().strip()
            # แปลงราคาเป็น float (เลขทศนิยม)
            price = float(self.entries['price'].get()) 
            # แปลงสต็อกเป็น int (เลขจำนวนเต็ม)
            stock = int(self.entries['stock'].get()) 
            # ดึงคำอธิบายจาก Textbox
            description = self.entries['description'].get("1.0", "end-1c").strip() 

            # ตรวจสอบว่ากรอกข้อมูลที่จำเป็น (ชื่อ, หมวดหมู่) ครบหรือไม่
            if not name or not category:
                messagebox.showwarning("ข้อมูลไม่ครบ", "กรุณากรอกชื่อและหมวดหมู่สินค้า", parent=self)
                return # หยุดทำงานถ้าข้อมูลไม่ครบ

            # ใช้ชื่อไฟล์รูปภาพที่เก็บไว้ (ถ้าไม่ได้ upload ใหม่ ก็จะใช้ค่าเดิมจาก on_product_select)
            # ถ้า self.image_filename เป็น None ให้ใช้ "" (สตริงว่าง) แทน
            image_url_to_save = self.image_filename if self.image_filename else ""

            # --- สำคัญ: เช็คว่าเป็นการ "แก้ไข" หรือ "สร้างใหม่" ---
            if self.selected_product_id: 
                # ถ้า selected_product_id มีค่า (คือเคยคลิกเลือกจากตาราง) = แก้ไข
                success = self.db.update_product(
                    self.selected_product_id, # ID ที่จะแก้ไข
                    name, description, price, stock, category, image_url_to_save
                )
                if success:
                    messagebox.showinfo("สำเร็จ", "อัปเดตข้อมูลสินค้าเรียบร้อย!", parent=self)
                else:
                    messagebox.showerror("ผิดพลาด", "ไม่สามารถอัปเดตข้อมูลสินค้าได้", parent=self)
                    return # ถ้าอัปเดตไม่สำเร็จ ก็ไม่ต้อง refresh
            else:
                # ถ้า selected_product_id เป็น None = สร้างใหม่
                new_product_id = self.db.create_product(
                    name, description, price, stock, category, image_url_to_save
                )
                if new_product_id:
                    messagebox.showinfo("สำเร็จ", "เพิ่มสินค้าใหม่เรียบร้อย!", parent=self)
                else:
                     messagebox.showerror("ผิดพลาด", "ไม่สามารถเพิ่มสินค้าใหม่ได้", parent=self)
                     return # ถ้าเพิ่มไม่สำเร็จ ก็ไม่ต้อง refresh
            
            # ถ้าบันทึกสำเร็จ (ทั้งแก้ไขและสร้างใหม่) ให้ refresh หน้าจอ
            self.on_show() 
            
        except ValueError: # ดักจับ error ถ้าแปลง float() หรือ int() ไม่สำเร็จ
            messagebox.showerror("ผิดพลาด", "ราคาและจำนวนสต็อกต้องเป็นตัวเลขเท่านั้น", parent=self)
        except Exception as e: # ดักจับ error อื่นๆ ที่อาจเกิดขึ้น
            messagebox.showerror("ผิดพลาด", f"เกิดข้อผิดพลาด: {e}", parent=self)

    def delete_product(self):
        # เช็คว่ามีการเลือกสินค้าในตารางหรือยัง
        if not self.selected_product_id:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกสินค้าที่ต้องการลบ", parent=self)
            return
            
        # แสดงกล่องข้อความยืนยัน (askyesno คืนค่า True ถ้ากด Yes)
        if messagebox.askyesno("ยืนยันการลบ", "คุณแน่ใจหรือไม่ว่าต้องการลบสินค้านี้?", parent=self):
            # สั่งลบข้อมูลใน DB
            success = self.db.delete_product(self.selected_product_id)
            if success:
                messagebox.showinfo("สำเร็จ", "ลบสินค้าเรียบร้อยแล้ว", parent=self)
                self.on_show() # Refresh หน้าจอหลังลบสำเร็จ
            else:
                 messagebox.showerror("ผิดพลาด", "ไม่สามารถลบสินค้าได้", parent=self)

    def clear_form(self):
        # รีเซ็ต ID ที่เลือกอยู่
        self.selected_product_id = None 
        # รีเซ็ตชื่อไฟล์รูปภาพ
        self.image_filename = None 
        # ยกเลิกการเลือกแถวในตาราง (ถ้ามี)
        current_selection = self.tree.selection()
        if current_selection:
            self.tree.selection_remove(current_selection)

        # วนลูปใน dictionary self.entries เพื่อล้างค่าในช่องกรอก
        for key, entry_widget in self.entries.items():
            if isinstance(entry_widget, ctk.CTkTextbox):
                entry_widget.delete("1.0", 'end') # ลบข้อมูลใน Textbox
            elif isinstance(entry_widget, ctk.CTkEntry):
                entry_widget.delete(0, 'end') # ลบข้อมูลใน Entry
        
        # รีเซ็ต Label แสดงชื่อไฟล์รูปภาพ
        self.image_label.configure(text="ยังไม่ได้เลือกรูปภาพ")