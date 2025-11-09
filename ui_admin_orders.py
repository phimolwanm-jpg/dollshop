import customtkinter as ctk
from tkinter import ttk, messagebox

class AdminOrdersWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        
        # ประกาศตัวแปรของคลาส
        # สร้าง widget จริงๆ ใน setup_ui
        self.tree = None
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 
    
    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้:
        (ปรับปรุง) แค่โหลดข้อมูลตารางใหม่ ไม่ต้องสร้าง UI ใหม่ทั้งหมด
        """
        self.load_orders() 
    
    # ============================================
    # ===== 1. "ผู้จัดการ" สร้าง UI หลัก =====
    # ============================================

    def setup_ui(self):
        """
        ฟังก์ชันหลักสำหรับสร้าง UI
        ทำหน้าที่เป็น "ผู้จัดการ" เรียกฟังก์ชันย่อยมาทำงาน
        """
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)    

        # === 1.1 สร้างส่วนหัว (Header) ===
        self.create_header()
        
        # === 1.2 สร้าง Frame หลักสำหรับเนื้อหา (ตารางและปุ่ม) ===
        main_frame = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF", 
            corner_radius=20, 
            border_width=2, 
            border_color="#FFEBEE"
        )
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        main_frame.grid_columnconfigure(0, weight=1) 
        main_frame.grid_rowconfigure(1, weight=1) 
        
        # === 1.3 สร้าง Title ของตาราง ===
        title_frame = ctk.CTkFrame(main_frame, fg_color="#FFE4E1", corner_radius=15)
        title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20) 
        ctk.CTkLabel(
            title_frame,
            text="📋 รายการคำสั่งซื้อทั้งหมด",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        ).pack(pady=15)
        
        # === 1.4 สร้างตาราง (Treeview) ===
        self.create_treeview(main_frame)
        
        # === 1.5 สร้างปุ่มควบคุม (Action Buttons) ===
        self.create_action_buttons(main_frame)
        
        # === 1.6 โหลดข้อมูลครั้งแรก (หลังจากสร้าง UI เสร็จ) ===
        self.load_orders() 

    # ============================================
    # ===== 2. "ผู้ช่วย" สร้างส่วนประกอบ UI =====
    # ============================================
    
    def create_header(self):
        """ สร้างส่วนหัว (Header) ของหน้า"""
        header = ctk.CTkFrame(
            self, 
            fg_color="#FFFFFF", 
            corner_radius=0, 
            height=70, 
            border_width=1, 
            border_color="#FFEBEE"
        )
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        header.grid_columnconfigure(1, weight=1) 
        
        ctk.CTkLabel(
            header,
            text="📦 จัดการคำสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        ).pack(side="left", padx=30, pady=20)
        
        header_btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        header_btn_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            header_btn_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), 
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            header_btn_frame,
            text="📊 Dashboard",
            command=lambda: self.main_app.navigate_to('AdminDashboardWindow'), 
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            font=ctk.CTkFont(size=14)
        ).pack(side="left", padx=5)

    def create_treeview(self, parent_frame):
        """สร้างตาราง Treeview และ Scrollbar ภายใน parent_frame"""
        # สร้าง Frame เพื่อห่อหุ้มตารางและ Scrollbar
        tree_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        tree_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
        tree_frame.grid_columnconfigure(0, weight=1) 
        tree_frame.grid_rowconfigure(0, weight=1) 
        
        # ตั้งค่า Style
        style = ttk.Style()
        style.configure("Orders.Treeview", rowheight=40, font=('Arial', 12)) 
        style.configure("Orders.Treeview.Heading", font=('Arial', 13, 'bold')) 
        
        # สร้าง Treeview
        columns = ("order_id", "customer", "amount", "payment", "status", "date") 
        self.tree = ttk.Treeview(tree_frame, 
                                 columns=columns, 
                                 show="headings", 
                                 style="Orders.Treeview")
        
        # ตั้งค่า Headings
        self.tree.heading("order_id", text="Order ID")
        self.tree.heading("customer", text="ลูกค้า")
        self.tree.heading("amount", text="ยอดเงิน")
        self.tree.heading("payment", text="การชำระเงิน")
        self.tree.heading("status", text="สถานะ")
        self.tree.heading("date", text="วันที่")
        
        # ตั้งค่า Columns
        self.tree.column("order_id", width=80, anchor="center")
        self.tree.column("customer", width=200, anchor="w")
        self.tree.column("amount", width=120, anchor="e")
        self.tree.column("payment", width=150, anchor="w")
        self.tree.column("status", width=120, anchor="center")
        self.tree.column("date", width=150, anchor="center")
        
        # สร้าง Scrollbar
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set) 
        
        # วาง Treeview และ Scrollbar
        self.tree.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    def create_action_buttons(self, parent_frame):
        """สร้างปุ่มควบคุม (Confirm, Ship, Deliver, Refresh)"""
        action_btn_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        action_btn_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20)) 

        
        # --- 1. ปุ่ม "ยืนยันคำสั่งซื้อ" ---
        confirm_button = ctk.CTkButton(
            action_btn_frame,
            text="✅ ยืนยันคำสั่งซื้อ",
            command=self.confirm_selected_order, 
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        confirm_button.pack(side="left", padx=5, fill="x", expand=True) 
        
        # --- 2. ปุ่ม "เริ่มจัดส่ง" ---
        ship_button = ctk.CTkButton(
            action_btn_frame,
            text="🚚 เริ่มจัดส่ง",
            command=self.ship_selected_order,
            fg_color="#2196F3",
            hover_color="#42A5F5",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        ship_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 3. ปุ่ม "จัดส่งสำเร็จ" ---
        deliver_button = ctk.CTkButton(
            action_btn_frame,
            text="✔️ จัดส่งสำเร็จ",
            command=self.deliver_selected_order,
            fg_color="#FF9800",
            hover_color="#FFA726",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        deliver_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 4. ปุ่ม "รีเฟรช" ---
        refresh_button = ctk.CTkButton(
            action_btn_frame,
            text="🔄 รีเฟรช",
            command=self.load_orders, 
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            height=40,
            corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        refresh_button.pack(side="left", padx=5, fill="x", expand=True)

    # ============================================
    # ===== 3. ฟังก์ชันจัดการข้อมูล (Data) =====
    # ============================================

    def load_orders(self):
        """โหลดข้อมูลคำสั่งซื้อทั้งหมดมาใส่ตาราง"""
        # ป้องกัน error ถ้า tree ยังไม่ถูกสร้าง
        if not self.tree: 
            return
            
        # ล้างข้อมูลเก่า
        for item_id in self.tree.get_children():
            self.tree.delete(item_id)
        
        orders_data = self.db.get_all_orders()
        
        status_text_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ จัดส่งสำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        for order in orders_data:
            status_display = status_text_map.get(order['status'], order['status'])
            
            # ตรวจสอบว่ามี created_at หรือไม่
            order_date = order['created_at']
            if order_date:
                order_date = order_date[:16] 
            else:
                order_date = '-'
                
            self.tree.insert("", "end", values=(
                f"#{order['order_id']}",
                order['full_name'],
                f"฿{order['total_amount']:,.2f}",
                order['payment_method'],
                status_display,
                order_date
            ))
    
    def change_status(self, new_status):
        """
        (ฟังก์ชันแกนกลาง) เปลี่ยนสถานะของคำสั่งซื้อที่เลือกในตาราง
        """
        selected_item_ids = self.tree.selection() 
        
        if not selected_item_ids:
            messagebox.showwarning("คำเตือน", "กรุณาเลือกคำสั่งซื้อที่ต้องการเปลี่ยนสถานะ", parent=self)
            return 
        
        status_names_map = {
            'confirmed': 'ยืนยันคำสั่งซื้อ',
            'shipped': 'เริ่มจัดส่ง',
            'delivered': 'จัดส่งสำเร็จ',
            'cancelled': 'ยกเลิก'
        }
        status_name_thai = status_names_map.get(new_status, new_status)
        confirm_message = f"ต้องการเปลี่ยนสถานะเป็น '{status_name_thai}' ใช่หรือไม่?"
        
        user_confirmed = messagebox.askyesno("ยืนยัน", confirm_message, parent=self)
        
        if user_confirmed:
            success_count = 0
            fail_count = 0
            
            for item_id in selected_item_ids:
                item_values = self.tree.item(item_id)['values']
                order_id_str = item_values[0] 
                order_id = int(order_id_str.replace('#', '')) 
                
                success = self.db.update_order_status(order_id, new_status)
                
                if success:
                    success_count += 1
                else:
                    fail_count += 1
                    messagebox.showerror("ผิดพลาด", f"ไม่สามารถเปลี่ยนสถานะคำสั่งซื้อ #{order_id} ได้", parent=self)
            
            if fail_count == 0 and success_count > 0:
                # แสดงข้อความสรุปแค่ครั้งเดียว (ถ้าสำเร็จทั้งหมด)
                messagebox.showinfo("สำเร็จ", f"เปลี่ยนสถานะ {success_count} รายการเรียบร้อย!", parent=self)
            
            # โหลดข้อมูลตารางใหม่เสมอ เพื่อให้เห็นการเปลี่ยนแปลง
            self.load_orders()

    # =================================================================
    # ===== 4. ฟังก์ชันสำหรับปุ่ม =====
    # =================================================================

    def confirm_selected_order(self):
        """
        (ปุ่ม 1) สั่งให้เปลี่ยนสถานะเป็น 'confirmed'
        """
        self.change_status("confirmed")

    def ship_selected_order(self):
        """
        (ปุ่ม 2) สั่งให้เปลี่ยนสถานะเป็น 'shipped'
        """
        self.change_status("shipped")

    def deliver_selected_order(self):
        """
        (ปุ่ม 3) สั่งให้เปลี่ยนสถานะเป็น 'delivered'
        """
        self.change_status("delivered")