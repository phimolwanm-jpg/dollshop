import customtkinter as ctk
from tkinter import ttk

class SalesHistoryWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5") # สีชมพูอ่อน พื้นหลังหลัก
        self.main_app = main_app
        # ดึง object database จาก main_app
        self.db = main_app.db 
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 
    
    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ข้อมูลสถิติและตารางสดใหม่เสมอ
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
        # ให้แถวที่ 2 (main_frame) ขยายเต็มความสูง (แถว 0=header, 1=stats, 2=table)
        self.grid_rowconfigure(2, weight=1) 

        # --- 2. สร้างส่วนหัว (Header) ---
        # (ย้ายโค้ดจาก create_header มาไว้ตรงนี้)
        header_frame = ctk.CTkFrame(
            self, # ใส่ header ใน SalesHistoryWindow (self)
            fg_color="#FFFFFF", 
            corner_radius=0, 
            height=70, 
            border_width=1, 
            border_color="#FFEBEE"
        )
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20)) 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันปุ่มไปขวา)
        header_frame.grid_columnconfigure(1, weight=1) 
        
        # Label ชื่อหน้า
        header_title = ctk.CTkLabel(
            header_frame,
            text="📊 ประวัติการขาย",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # Frame สำหรับวางปุ่มทางขวา
        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.pack(side="right", padx=20)
        
        # ปุ่ม "หน้าหลัก"
        home_button = ctk.CTkButton(
            header_buttons_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), # กดแล้วกลับ Home
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        )
        home_button.pack(side="left", padx=5)
        
        # ปุ่ม "Dashboard"
        dashboard_button = ctk.CTkButton(
            header_buttons_frame,
            text="📊 Dashboard",
            command=lambda: self.main_app.navigate_to('AdminDashboardWindow'), # กดแล้วไป Dashboard
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            font=ctk.CTkFont(size=14)
        )
        dashboard_button.pack(side="left", padx=5)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame สำหรับวางการ์ดสถิติ ---
        # (ย้ายโค้ดส่วนใหญ่จาก create_stats_cards มาไว้ตรงนี้)
        stats_cards_frame = ctk.CTkFrame(self, fg_color="transparent")
        # วาง frame นี้ในแถว 1 (ใต้ header) ยืดเต็มกว้าง
        stats_cards_frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10)) 
        # แบ่ง frame นี้เป็น 4 คอลัมน์เท่าๆ กัน
        stats_cards_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) 
        
        # --- 3.1 ดึงข้อมูลสถิติจาก DB ---
        dashboard_stats = self.db.get_dashboard_stats() 
        # ดึงจำนวนสินค้าที่ขายได้ทั้งหมด (เรียกฟังก์ชันช่วย)
        total_items_sold_count = self.get_total_items_sold() 
        
        # --- 3.2 เตรียมข้อมูลสำหรับการ์ดแต่ละใบ ---
        all_cards_data = [
            { # การ์ด 1: ยอดขายรวม
                'title': 'ยอดขายรวม',
                'value': f"{dashboard_stats['total_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'icon': '🛒',
                'color': '#4CAF50' # สีเขียว
            },
            { # การ์ด 2: รายได้ทั้งหมด
                'title': 'รายได้ทั้งหมด',
                'value': f"฿{dashboard_stats['total_revenue']:,.2f}", # จัดรูปแบบ
                'subtitle': 'บาท',
                'icon': '💰',
                'color': '#2196F3' # สีฟ้า
            },
            { # การ์ด 3: ลูกค้าทั้งหมด
                'title': 'ลูกค้าทั้งหมด',
                'value': f"{dashboard_stats['total_customers']}",
                'subtitle': 'คน',
                'icon': '👥',
                'color': '#FF9800' # สีส้ม
            },
            { # การ์ด 4: สินค้าขายแล้ว
                'title': 'สินค้าขายแล้ว',
                'value': f"{total_items_sold_count}", # ใช้ค่าที่ดึงมา
                'subtitle': 'ชิ้น',
                'icon': '📦',
                'color': '#E91E63' # สีชมพูเข้ม
            }
        ]
        
        # --- 3.3 วนลูปสร้างการ์ดแต่ละใบ ---
        for i, single_card_data in enumerate(all_cards_data):
            # --- สร้างการ์ด 1 ใบ (โค้ดจาก create_stat_card เดิม) ---
            # (ย้ายโค้ดสร้างการ์ดมาไว้ใน loop นี้)
            
            # สร้าง Frame ของการ์ด
            stat_card = ctk.CTkFrame(
                stats_cards_frame, # ใส่การ์ดลงใน frame นี้
                fg_color="#FFFFFF",
                corner_radius=15,
                border_width=2,
                border_color="#FFEBEE"
            )
            
            # Icon (Emoji)
            icon_label = ctk.CTkLabel(
                stat_card,
                text=single_card_data['icon'],
                font=ctk.CTkFont(size=40)
            )
            icon_label.pack(pady=(15, 5))
            
            # Title (เช่น 'ยอดขายรวม')
            title_label = ctk.CTkLabel(
                stat_card,
                text=single_card_data['title'],
                font=ctk.CTkFont(size=12),
                text_color="gray50"
            )
            title_label.pack(pady=2)
            
            # Value (ตัวเลขสถิติ)
            value_label = ctk.CTkLabel(
                stat_card,
                text=single_card_data['value'],
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color=single_card_data['color'] # ใช้สีตามที่กำหนด
            )
            value_label.pack(pady=2)
            
            # Subtitle (เช่น 'คำสั่งซื้อ')
            subtitle_label = ctk.CTkLabel(
                stat_card,
                text=single_card_data['subtitle'],
                font=ctk.CTkFont(size=11),
                text_color="gray40"
            )
            subtitle_label.pack(pady=(2, 15))
            # --- จบการสร้างการ์ด 1 ใบ ---
            
            # วางการ์ดลงใน stats_cards_frame ตามคอลัมน์ i (0, 1, 2, 3)
            stat_card.grid(row=0, column=i, padx=10, sticky="nsew") 
        # --- จบส่วนสร้างการ์ดสถิติ ---

        # --- 4. สร้าง Frame หลักสำหรับเนื้อหา (ตารางและปุ่ม) ---
        main_content_frame = ctk.CTkFrame(
            self, # ใส่ใน SalesHistoryWindow (self)
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        # วาง frame นี้ในแถว 2 (ใต้การ์ดสถิติ) ยืดเต็มพื้นที่
        main_content_frame.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20)) 
        # ให้คอลัมน์ 0 ใน frame นี้ขยายเต็มความกว้าง
        main_content_frame.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (tree_frame) ใน frame นี้ขยายเต็มความสูง
        main_content_frame.grid_rowconfigure(1, weight=1) 

        # --- 4.1 สร้าง Title ของตาราง ---
        table_title_frame = ctk.CTkFrame(main_content_frame, fg_color="#FFE4E1", corner_radius=15)
        # วาง title frame ในแถว 0 ของ main_content_frame
        table_title_frame.grid(row=0, column=0, sticky="ew", padx=20, pady=20) 
        
        table_title_label = ctk.CTkLabel(
            table_title_frame,
            text="📋 ประวัติการขายทั้งหมด",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#6D4C41"
        )
        table_title_label.pack(pady=15)
        
        # --- 4.2 สร้าง Frame สำหรับตาราง Treeview และ Scrollbar ---
        # (ย้ายโค้ดส่วนใหญ่จาก create_sales_table มาไว้ตรงนี้)
        tree_view_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง frame นี้ในแถว 1 (ใต้ title) ยืดเต็มพื้นที่
        tree_view_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20)) 
        # ให้คอลัมน์ 0 (ตาราง) ขยายเต็มกว้าง
        tree_view_frame.grid_columnconfigure(0, weight=1) 
        # ให้แถว 0 (ตาราง) ขยายเต็มสูง
        tree_view_frame.grid_rowconfigure(0, weight=1) 
        
        # --- 4.2.1 ตั้งค่า Style ให้กับตาราง ---
        tree_style = ttk.Style()
        tree_style.configure("Sales.Treeview", rowheight=40, font=('Arial', 12)) 
        tree_style.configure("Sales.Treeview.Heading", font=('Arial', 13, 'bold'))
        
        # --- 4.2.2 สร้างตาราง Treeview ---
        # กำหนดชื่อคอลัมน์ภายใน
        table_columns = ("order_id", "date", "customer", "items", "amount", "payment", "status") 
        # สร้าง Treeview ใส่ใน tree_view_frame
        self.sales_history_tree = ttk.Treeview(
            tree_view_frame,
            columns=table_columns,
            show="headings", # ไม่แสดงคอลัมน์ #0
            style="Sales.Treeview" # ใช้ style ที่ตั้งไว้
        )
        
        # --- 4.2.3 ตั้งค่าหัวตาราง (ที่แสดงผล) และความกว้าง ---
        column_headings = {
            "order_id": "Order ID", "date": "วันที่", "customer": "ลูกค้า",
            "items": "รายการสินค้า", "amount": "ยอดเงิน", "payment": "ชำระเงิน",
            "status": "สถานะ"
        }
        column_widths = {
            "order_id": 80, "date": 150, "customer": 180, "items": 300,
            "amount": 120, "payment": 150, "status": 120
        }
        column_anchors = { # การจัดเรียงในคอลัมน์
            "order_id": "center", "amount": "e", "status": "center", 
            # ค่า default คือ "w" (ชิดซ้าย)
        }
        
        # วนลูปตั้งค่าหัวตารางแต่ละคอลัมน์
        for col_name in table_columns:
            self.sales_history_tree.heading(col_name, text=column_headings[col_name])
            self.sales_history_tree.column(
                col_name,
                width=column_widths[col_name],
                # ใช้ .get() เพื่อเอา anchor ถ้าไม่มี ใช้ 'w' (ชิดซ้าย) เป็น default
                anchor=column_anchors.get(col_name, "w") 
            )
        
        # --- 4.2.4 สร้าง Scrollbar ---
        tree_scrollbar = ttk.Scrollbar(tree_view_frame, orient="vertical", command=self.sales_history_tree.yview)
        # ผูก scrollbar เข้ากับ treeview
        self.sales_history_tree.configure(yscrollcommand=tree_scrollbar.set) 
        
        # วาง treeview และ scrollbar ลงใน tree_view_frame โดยใช้ grid
        self.sales_history_tree.grid(row=0, column=0, sticky="nsew") # ตารางอยู่ คอลัมน์ 0
        tree_scrollbar.grid(row=0, column=1, sticky="ns") # scrollbar อยู่ คอลัมน์ 1
        
        # --- 4.2.5 โหลดข้อมูลใส่ตาราง ---
        self.load_sales_data() # เรียกฟังก์ชันโหลดข้อมูล
        
        # --- 4.3 สร้าง Frame สำหรับวางปุ่มควบคุมใต้ตาราง ---
        action_buttons_frame = ctk.CTkFrame(main_content_frame, fg_color="transparent")
        # วาง frame นี้ในแถว 2 (ใต้ตาราง) ของ main_content_frame
        action_buttons_frame.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20)) 
        
        # --- 4.3.1 สร้างปุ่ม "รีเฟรช" ---
        refresh_button = ctk.CTkButton(
            action_buttons_frame,
            text="🔄 รีเฟรช",
            command=self.on_show, # กดแล้วเรียก on_show (ลบ+สร้างใหม่)
            fg_color="#FFB6C1", # สีชมพู
            hover_color="#FFC0CB",
            height=40, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        # ใช้ pack วางปุ่มเรียงกันใน action_buttons_frame
        refresh_button.pack(side="left", padx=5, fill="x", expand=True) 
        
        # --- 4.3.2 สร้างปุ่ม "ดูสถิติเพิ่มเติม" ---
        more_stats_button = ctk.CTkButton(
            action_buttons_frame,
            text="📊 ดูสถิติเพิ่มเติม",
            command=lambda: self.main_app.navigate_to('AdminDashboardWindow'), # ไปหน้า Dashboard
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            height=40, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        more_stats_button.pack(side="left", padx=5, fill="x", expand=True)
        
        # --- 4.3.3 สร้างปุ่ม "จัดการคำสั่งซื้อ" ---
        manage_orders_button = ctk.CTkButton(
            action_buttons_frame,
            text="📦 จัดการคำสั่งซื้อ",
            command=lambda: self.main_app.navigate_to('AdminOrdersWindow'), # ไปหน้า AdminOrders
            fg_color="#2196F3", # สีฟ้า
            hover_color="#42A5F5",
            height=40, corner_radius=10,
            font=ctk.CTkFont(size=14, weight="bold")
        )
        manage_orders_button.pack(side="left", padx=5, fill="x", expand=True)
        # --- จบส่วนสร้าง UI ---

    # --- (ลบฟังก์ชัน create_header, create_stats_cards, create_stat_card) ---
    # --- (ลบฟังก์ชัน create_sales_table) ---
    
    def get_total_items_sold(self):
        """คำนวณจำนวนสินค้าที่ขายไปทั้งหมด (Logic เดิม)"""
        db_cursor = None # ประกาศตัวแปร cursor ก่อน try
        total_sold = 0 # ค่าเริ่มต้น
        try:
            db_cursor = self.db.connect() # เปิด connection
            # สั่ง SQL รวม quantity ทั้งหมดใน order_items
            db_cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM order_items") 
            # ดึงผลลัพธ์ (แถวแรก, คอลัมน์แรก)
            result = db_cursor.fetchone() 
            if result:
                total_sold = result[0]
        except Exception as e:
            print(f"Error getting total items sold: {e}")
        finally:
            # --- สำคัญ: ต้อง close connection เสมอ ไม่ว่าจะสำเร็จหรือ error ---
            if self.db: # เช็คว่า self.db ถูกสร้างหรือยัง (อาจไม่จำเป็น แต่ปลอดภัย)
                self.db.close() 
        return total_sold
    
    def load_sales_data(self):
        """โหลดข้อมูลประวัติการขายมาใส่ตาราง (Logic เดิม)"""
        # --- 1. ล้างข้อมูลเก่าในตาราง ---
        for item_id in self.sales_history_tree.get_children():
            self.sales_history_tree.delete(item_id)
        
        # --- 2. ดึงข้อมูล Order ทั้งหมดจาก DB ---
        all_orders_data = self.db.get_all_orders()
        
        # --- 3. เตรียมข้อความสำหรับ Status และ Payment ---
        status_text_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ สำเร็จ', # เปลี่ยนจาก จัดส่งสำเร็จ
            'cancelled': '❌ ยกเลิก'
        }
        payment_text_map = {
            'โอนเงินผ่านธนาคาร': '🏦 โอนเงิน',
            'เก็บเงินปลายทาง': '📦 COD',
            'Credit Card': '💳 บัตร' # เผื่อมีในอนาคต
        }
        
        # --- 4. วนลูปเพิ่มข้อมูลทีละแถว ---
        for order_dict in all_orders_data:
            # --- 4.1 เตรียมข้อมูลสำหรับแต่ละคอลัมน์ ---
            
            # Order ID (ใส่ # นำหน้า)
            display_order_id = f"#{order_dict['order_id']}"
            
            # วันที่ (ตัดวินาที)
            order_date = order_dict.get('created_at', '-')
            if order_date and len(order_date) > 16:
                order_date = order_date[:16]
                
            # ลูกค้า (ใช้ full_name)
            customer_name = order_dict.get('full_name', '-') # ใช้ .get ปลอดภัยกว่า
            
            # รายการสินค้า (ตัดให้สั้นถ้าเกิน 50 ตัว)
            items_string = order_dict.get('items', '')
            if len(items_string) > 50:
                items_display = items_string[:47] + "..." # ตัดเหลือ 47 + ...
            elif not items_string:
                items_display = 'ไม่มีรายการ'
            else:
                items_display = items_string
            
            # ยอดเงิน (จัดรูปแบบ)
            amount_display = f"฿{order_dict.get('total_amount', 0):,.2f}"
            
            # การชำระเงิน (แปลภาษา)
            payment_method = order_dict.get('payment_method', '')
            payment_display = payment_text_map.get(payment_method, payment_method) # ถ้าไม่เจอ key ใช้ค่าเดิม
            
            # สถานะ (แปลภาษา)
            status = order_dict.get('status', '')
            status_display = status_text_map.get(status, status) # ถ้าไม่เจอ key ใช้ค่าเดิม
            
            # --- 4.2 เพิ่มแถวใหม่ลงในตาราง ---
            self.sales_history_tree.insert("", "end", values=(
                display_order_id,
                order_date,
                customer_name,
                items_display,
                amount_display,
                payment_display,
                status_display
            ))