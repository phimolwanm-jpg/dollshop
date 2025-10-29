import customtkinter as ctk
from tkinter import ttk, messagebox

class AdminOrdersWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 
    
    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ข้อมูลคำสั่งซื้อสดใหม่เสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 
    
    def setup_ui(self):
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (main_frame) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        # (ย้ายโค้ดจาก create_header มาไว้ตรงนี้)
        header = ctk.CTkFrame(
            self, # ใส่ header ลงใน AdminOrdersWindow (self)
            fg_color="#FFFFFF", 
            corner_radius=0, 
            height=70, 
            border_width=1, 
            border_color="#FFEBEE"
        )
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันปุ่มไปขวา)
        header.grid_columnconfigure(1, weight=1) 
        
        # Label ชื่อหน้า
        header_title = ctk.CTkLabel(
            header,
            text="📦 จัดการคำสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # Frame สำหรับวางปุ่มทางขวา
        header_btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        header_btn_frame.pack(side="right", padx=20)
        
        # ปุ่ม "หน้าหลัก"
        home_btn = ctk.CTkButton(
            header_btn_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), # กดแล้วไปหน้า Home
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        )
        home_btn.pack(side="left", padx=5)
        
        # ปุ่ม "Dashboard"
        dashboard_btn = ctk.CTkButton(
            header_btn_frame,
            text="📊 Dashboard",
            command=lambda: self.main_app.navigate_to('AdminDashboardWindow'), # กดแล้วไปหน้า Dashboard
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            font=ctk.CTkFont(size=14)
        )
        dashboard_btn.pack(side="left", padx=5)
        # --- จบส่วน Header ---
        
        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (ตารางและปุ่ม) ---
        main_frame = ctk.CTkFrame(
            self, # ใส่ main_frame ใน AdminOrdersWindow (self)
            fg_color="#FFFFFF", 
            corner_radius=20, 
            border_width=2, 
            border_color="#FFEBEE"
        )
        # วาง main_frame ในแถว 1 (ใต้ header) ยืดเต็มพื้นที่ (sticky="nsew")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        # ให้คอลัมน์ 0 ใน main_frame ขยายเต็มความกว้าง
        main_frame.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (tree_frame) ใน main_frame ขยายเต็มความสูง
        main_frame.grid_rowconfigure(1, weight=1) 
        
        # --- 3.1 สร้าง Title ของตาราง ---
        title_frame = ctk.CTkFrame(main_frame, fg_color="#FFE4E1", corner_radius=15)
        # วาง title_frame ในแถว 0 ของ main_frame ยืดเต็มความกว้าง
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20) 
        
        title_label = ctk.CTkLabel(
            title_frame,
            text="📋 รายการคำสั่งซื้อทั้งหมด",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        title_label.pack(pady=15)
        
        # --- 3.2 สร้าง Frame สำหรับตาราง Treeview และ Scrollbar ---
        # (ย้ายโค้ดส่วนใหญ่จาก create_orders_table มาไว้ตรงนี้)
        tree_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        # วาง tree_frame ในแถว 1 ของ main_frame ยืดเต็มพื้นที่
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
        # ให้คอลัมน์ 0 (ตาราง) ขยายเต็มความกว้าง
        tree_frame.grid_columnconfigure(0, weight=1) 
        # ให้แถว 0 (ตาราง) ขยายเต็มความสูง
        tree_frame.grid_rowconfigure(0, weight=1) 
        
        # --- 3.2.1 ตั้งค่า Style ให้กับตาราง ---
        style = ttk.Style()
        # ตั้งค่า font และความสูงของแถว
        style.configure("Orders.Treeview", rowheight=40, font=('Arial', 12)) 
        # ตั้งค่า font ของหัวตาราง
        style.configure("Orders.Treeview.Heading", font=('Arial', 13, 'bold')) 
        
        # --- 3.2.2 สร้างตาราง Treeview ---
        # กำหนดชื่อคอลัมน์ภายใน (Internal names)
        columns = ("order_id", "customer", "amount", "payment", "status", "date") 
        # สร้าง Treeview ใส่ใน tree_frame
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=columns, 
                                 show="headings", # ไม่แสดงคอลัมน์ #0 (Tree column)
                                 style="Orders.Treeview") # ใช้ style ที่ตั้งค่าไว้
        
        # --- 3.2.3 ตั้งค่าหัวตาราง (ที่แสดงผล) ---
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("customer", text="ลูกค้า")
        self.tree.heading("amount", text="ยอดเงิน")
        self.tree.heading("payment", text="การชำระเงิน")
        self.tree.heading("status", text="สถานะ")
        self.tree.heading("date", text="วันที่")
        
        # --- 3.2.4 ตั้งค่าความกว้าง และการจัดเรียง (Alignment) ของแต่ละคอลัมน์ ---
        self.tree.column("order_id", width=80, anchor="center") # center คือตรงกลาง
        self.tree.column("customer", width=200, anchor="w")    # w คือชิดซ้าย (West)
        self.tree.column("amount", width=120, anchor="e")    # e คือชิดขวา (East)
        self.tree.column("payment", width=150, anchor="w")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        
        # --- 3.2.5 สร้าง Scrollbar ---
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        # ผูก scrollbar เข้ากับ treeview
        self.tree.configure(yscrollcommand=scrollbar.set) 
        
        # วาง treeview และ scrollbar ลงใน tree_frame โดยใช้ grid
        self.tree.grid(row=0, column=0, sticky="nsew") # ตารางอยู่ คอลัมน์ 0
        scrollbar.grid(row=0, column=1, sticky="ns") # scrollbar อยู่ คอลัมน์ 1, ยืดแนวตั้ง (ns)
        
        # --- 3.2.6 โหลดข้อมูลใส่ตาราง (เรียกฟังก์ชัน load_orders) ---
        self.load_orders() 
        
        # --- 3.3 สร้าง Frame สำหรับวางปุ่มควบคุม ---
        action_btn_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        # วาง action_btn_frame ในแถว 2 (ใต้ตาราง) ของ main_frame
        action_btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20)) 
        
        # --- 3.3.1 สร้างปุ่ม "ยืนยันคำสั่งซื้อ" ---
        confirm_button = ctk.CTkButton(
            action_btn_frame,
            text="✅ ยืนยันคำสั่งซื้อ",
            # เมื่อกดปุ่ม ให้เรียกฟังก์ชัน change_status โดยส่ง 'confirmed' ไป
            command=lambda: self.change_status("confirmed"), 
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        # ใช้ pack วางปุ่มเรียงกันใน action_btn_frame
        # fill="x" ให้ปุ่มยืดเต็มความกว้าง, expand=True ให้แบ่งพื้นที่เท่าๆ กัน
        confirm_button.pack(side="left", padx=5, fill="x", expand=True) 
        
        # --- 3.3.2 สร้างปุ่ม "เริ่มจัดส่ง" ---
        ship_button = ctk.CTkButton(
            action_btn_frame,
            text="🚚 เริ่มจัดส่ง",
            command=lambda: self.change_status("shipped"), # ส่ง 'shipped'
            fg_color="#2196F3", # สีฟ้า
            hover_color="#42A5F5",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ship_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 3.3.3 สร้างปุ่ม "จัดส่งสำเร็จ" ---
        deliver_button = ctk.CTkButton(
            action_btn_frame,
            text="✔️ จัดส่งสำเร็จ",
            command=lambda: self.change_status("delivered"), # ส่ง 'delivered'
            fg_color="#FF9800", # สีส้ม
            hover_color="#FFA726",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        deliver_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 3.3.4 สร้างปุ่ม "รีเฟรช" ---
        refresh_button = ctk.CTkButton(
            action_btn_frame,
            text="🔄 รีเฟรช",
            command=self.on_show, # กดแล้วให้เรียก on_show (ลบ+สร้างใหม่)
            fg_color="#FFB6C1", # สีชมพู
            hover_color="#FFC0CB",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        refresh_button.pack(side="left", padx=5, fill="x", expand=True)
        # --- จบส่วนสร้าง UI ---

    # --- (ลบฟังก์ชัน create_header และ create_orders_table เพราะย้ายโค้ดไปแล้ว) ---
    
    def load_orders(self):
        """โหลดข้อมูลคำสั่งซื้อทั้งหมดมาใส่ตาราง"""
        # --- 1. ล้างข้อมูลเก่าในตารางก่อน ---
        # tree.get_children() จะได้ id ของทุกแถวในตาราง
        for item_id in self.tree.get_children():
            self.tree.delete(item_id) # ลบแถวด้วย id
        
        # --- 2. ดึงข้อมูลคำสั่งซื้อทั้งหมดจาก DB ---
        orders_data = self.db.get_all_orders()
        
        # --- 3. เตรียมข้อความสถานะภาษาไทย ---
        status_text_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ จัดส่งสำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        # --- 4. วนลูปเพื่อเพิ่มข้อมูลทีละแถว ---
        for order in orders_data:
            # แปลงสถานะเป็นภาษาไทย (ถ้าไม่มี key ให้ใช้ค่าเดิม)
            status_display = status_text_map.get(order['status'], order['status'])
            
            # ตัดวินาทีของวันที่ออก
            order_date = order['created_at']
            if order_date:
                order_date = order_date[:16] # เอาแค่ YYYY-MM-DD HH:MM
            else:
                order_date = '-'
                
            # เพิ่มแถวใหม่ลงในตาราง
            self.tree.insert(
                "",          # parent item (ว่างคือระดับบนสุด)
                "end",       # ตำแหน่ง (ต่อท้ายสุด)
                values=(     # ค่าที่จะใส่ในแต่ละคอลัมน์ (ต้องเรียงลำดับให้ถูก)
                    f"#{order['order_id']}",         # คอลัมน์ 0: order_id
                    order['full_name'],              # คอลัมน์ 1: customer
                    f"฿{order['total_amount']:,.2f}", # คอลัมน์ 2: amount (จัดรูปแบบ)
                    order['payment_method'],         # คอลัมน์ 3: payment
                    status_display,                  # คอลัมน์ 4: status (ภาษาไทย)
                    order_date                       # คอลัมน์ 5: date (ตัดวินาที)
                )
            )
    
    def change_status(self, new_status):
        """เปลี่ยนสถานะของคำสั่งซื้อที่เลือกในตาราง"""
        # --- 1. เอา ID ของแถวที่ถูกเลือก ---
        # self.tree.selection() จะคืนค่า tuple ของ id แถวที่เลือก (อาจมีหลายแถว)
        selected_item_ids = self.tree.selection() 
        
        # --- 2. เช็คว่ามีการเลือกแถวหรือไม่ ---
        if not selected_item_ids:
            # ถ้ายังไม่ได้เลือก ให้แสดง popup เตือน แล้วจบการทำงาน
            messagebox.showwarning("คำเตือน", "กรุณาเลือกคำสั่งซื้อที่ต้องการเปลี่ยนสถานะ", parent=self)
            return 
        
        # --- 3. เตรียมข้อความสำหรับ popup ยืนยัน ---
        status_names_map = {
            'confirmed': 'ยืนยันคำสั่งซื้อ',
            'shipped': 'เริ่มจัดส่ง',
            'delivered': 'จัดส่งสำเร็จ',
            'cancelled': 'ยกเลิก' # เผื่อมีปุ่มยกเลิกในอนาคต
        }
        # แปลง new_status เป็นชื่อสถานะภาษาไทย (ถ้าไม่มี ให้ใช้ new_status เดิม)
        status_name_thai = status_names_map.get(new_status, new_status)
        confirm_message = f"ต้องการเปลี่ยนสถานะเป็น '{status_name_thai}' ใช่หรือไม่?"
        
        # --- 4. แสดง popup ยืนยัน (askyesno คืนค่า True ถ้ากด Yes) ---
        user_confirmed = messagebox.askyesno("ยืนยัน", confirm_message, parent=self)
        
        # --- 5. ถ้าผู้ใช้กด Yes ---
        if user_confirmed:
            # วนลูปเผื่อผู้ใช้เลือกหลายแถว
            for item_id in selected_item_ids:
                # ดึงข้อมูลจากแถวที่เลือก (จาก Treeview)
                item_values = self.tree.item(item_id)['values']
                # Order ID อยู่คอลัมน์แรก (index 0), มี # นำหน้า
                order_id_str = item_values[0] 
                # เอา # ออก แล้วแปลงเป็นตัวเลข int
                order_id = int(order_id_str.replace('#', '')) 
                
                # --- 6. สั่งอัปเดตสถานะใน DB ---
                success = self.db.update_order_status(order_id, new_status)
                
                # --- 7. แสดงผลลัพธ์ ---
                if success:
                    # ถ้าสำเร็จ แสดง popup แจ้งเตือน (ชั่วคราว อาจเอาออกถ้ามันรกไป)
                    # messagebox.showinfo("สำเร็จ", f"เปลี่ยนสถานะคำสั่งซื้อ #{order_id} เรียบร้อย", parent=self)
                    pass # ไม่ต้องแสดง popup ทุกครั้งก็ได้
                else:
                    # ถ้าไม่สำเร็จ แสดง popup error
                    messagebox.showerror("ผิดพลาด", f"ไม่สามารถเปลี่ยนสถานะคำสั่งซื้อ #{order_id} ได้", parent=self)
            
            # --- 8. โหลดข้อมูลตารางใหม่ เพื่อให้เห็นสถานะที่เปลี่ยนไป ---
            self.load_orders()