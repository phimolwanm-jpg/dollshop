import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta # 👈 1. Import datetime และ timedelta

class SalesHistoryWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.db = main_app.db
        self.create_ui()
    
    def on_show(self):
        """เปิดหน้านี้ - ลบของเก่าสร้างใหม่"""
        for widget in self.winfo_children():
            widget.destroy()
        self.create_ui()

    def create_ui(self):
        """สร้างหน้าจอทั้งหมด"""
        # ตั้งค่าให้ขยายเต็มหน้าจอ
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        # สร้างส่วนต่างๆ
        self.create_header()
        self.create_stats_cards()
        self.create_table_area()

    def create_header(self):
        """สร้างส่วนหัวด้านบน"""
        header = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=0,
                             height=70, border_width=1, border_color="#FFEBEE")
        header.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header.grid_columnconfigure(1, weight=1)
        
        # ชื่อหน้า
        title = ctk.CTkLabel(header, text="📊 ประวัติการขาย",
                            font=ctk.CTkFont(size=28, weight="bold"),
                            text_color="#FFB6C1")
        title.pack(side="left", padx=30, pady=20)
        
        # กรอบปุ่มขวา
        btn_box = ctk.CTkFrame(header, fg_color="transparent")
        btn_box.pack(side="right", padx=20)
        
        # ปุ่มหน้าหลัก
        home_btn = ctk.CTkButton(btn_box, text="🏠 หน้าหลัก",
                                command=self.go_home,
                                fg_color="transparent", text_color="#FFB6C1",
                                hover_color="#FFE4E1",
                                font=ctk.CTkFont(size=14))
        home_btn.pack(side="left", padx=5)
        
        # ปุ่ม Dashboard
        dash_btn = ctk.CTkButton(btn_box, text="📊 Dashboard",
                                command=self.go_dashboard,
                                fg_color="#4CAF50", hover_color="#66BB6A",
                                font=ctk.CTkFont(size=14))
        dash_btn.pack(side="left", padx=5)

    def create_stats_cards(self):
        """สร้างการ์ดสถิติ 4 ใบ"""
        # กรอบวางการ์ด
        cards_box = ctk.CTkFrame(self, fg_color="transparent")
        cards_box.grid(row=1, column=0, sticky="ew", padx=30, pady=(0, 10))
        cards_box.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # ดึงข้อมูลสถิติ
        stats = self.db.get_dashboard_stats()
        total_sold = self.count_total_items()
        
        # ข้อมูลการ์ดทั้ง 4 ใบ
        cards = [
            {
                'icon': '🛒',
                'title': 'ยอดขายรวม',
                'value': f"{stats['total_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'color': '#4CAF50'
            },
            {
                'icon': '💰',
                'title': 'รายได้ทั้งหมด',
                'value': f"฿{stats['total_revenue']:,.2f}",
                'subtitle': 'บาท',
                'color': '#2196F3'
            },
            {
                'icon': '👥',
                'title': 'ลูกค้าทั้งหมด',
                'value': f"{stats['total_customers']}",
                'subtitle': 'คน',
                'color': '#FF9800'
            },
            {
                'icon': '📦',
                'title': 'สินค้าขายแล้ว',
                'value': f"{total_sold}",
                'subtitle': 'ชิ้น',
                'color': '#E91E63'
            }
        ]
        
        # สร้างการ์ดทีละใบ
        for i, card_info in enumerate(cards):
            self.make_card(cards_box, card_info, i)

    def make_card(self, parent, info, col):
        """สร้างการ์ดสถิติ 1 ใบ"""
        card = ctk.CTkFrame(parent, fg_color="#FFFFFF", corner_radius=15,
                           border_width=2, border_color="#FFEBEE")
        
        # ไอคอน
        icon = ctk.CTkLabel(card, text=info['icon'],
                           font=ctk.CTkFont(size=40))
        icon.pack(pady=(15, 5))
        
        # ชื่อ
        title = ctk.CTkLabel(card, text=info['title'],
                            font=ctk.CTkFont(size=12),
                            text_color="gray50")
        title.pack(pady=2)
        
        # ค่าตัวเลข
        value = ctk.CTkLabel(card, text=info['value'],
                            font=ctk.CTkFont(size=24, weight="bold"),
                            text_color=info['color'])
        value.pack(pady=2)
        
        # หน่วย
        subtitle = ctk.CTkLabel(card, text=info['subtitle'],
                               font=ctk.CTkFont(size=11),
                               text_color="gray40")
        subtitle.pack(pady=(2, 15))
        
        # วางการ์ด
        card.grid(row=0, column=col, padx=10, sticky="nsew")

    def create_table_area(self):
        """สร้างพื้นที่ตารางและปุ่ม"""
        # กรอบหลัก
        main_box = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=20,
                               border_width=2, border_color="#FFEBEE")
        main_box.grid(row=2, column=0, sticky="nsew", padx=30, pady=(0, 20))
        main_box.grid_columnconfigure(0, weight=1)
        main_box.grid_rowconfigure(1, weight=1)

        # หัวตาราง
        title_box = ctk.CTkFrame(main_box, fg_color="#FFE4E1", corner_radius=15)
        title_box.grid(row=0, column=0, sticky="ew", padx=20, pady=20)
        
        title = ctk.CTkLabel(title_box, text="📋 ประวัติการขายทั้งหมด",
                            font=ctk.CTkFont(size=20, weight="bold"),
                            text_color="#6D4C41")
        title.pack(pady=15)
        
        # สร้างตาราง
        self.create_table(main_box)
        
        # สร้างปุ่มควบคุม
        self.create_buttons(main_box)

    def create_table(self, parent):
        """สร้างตารางแสดงข้อมูล"""
        # กรอบตาราง
        table_box = ctk.CTkFrame(parent, fg_color="transparent")
        table_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(0, 20))
        table_box.grid_columnconfigure(0, weight=1)
        table_box.grid_rowconfigure(0, weight=1)
        
        # ตั้งค่าสไตล์
        style = ttk.Style()
        style.configure("Sales.Treeview", rowheight=40, font=('Arial', 12))
        style.configure("Sales.Treeview.Heading", font=('Arial', 13, 'bold'))
        
        # สร้างตาราง
        columns = ("order_id", "date", "customer", "items", 
                  "amount", "payment", "status")
        
        self.table = ttk.Treeview(table_box, columns=columns,
                                 show="headings", style="Sales.Treeview")
        
        # ตั้งค่าหัวตาราง
        headers = {
            "order_id": "Order ID",
            "date": "วันที่",
            "customer": "ลูกค้า",
            "items": "รายการสินค้า",
            "amount": "ยอดเงิน",
            "payment": "ชำระเงิน",
            "status": "สถานะ"
        }
        
        widths = {
            "order_id": 80, "date": 150, "customer": 180,
            "items": 300, "amount": 120, "payment": 150, "status": 120
        }
        
        aligns = {
            "order_id": "center",
            "amount": "e",
            "status": "center"
        }
        
        # ตั้งค่าแต่ละคอลัมน์
        for col in columns:
            self.table.heading(col, text=headers[col])
            self.table.column(col, width=widths[col],
                            anchor=aligns.get(col, "w"))
        
        # สร้าง scrollbar
        scrollbar = ttk.Scrollbar(table_box, orient="vertical",
                                 command=self.table.yview)
        self.table.configure(yscrollcommand=scrollbar.set)
        
        # วางตาราง
        self.table.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # โหลดข้อมูล
        self.load_table_data()

    def create_buttons(self, parent):
        """สร้างปุ่มควบคุม"""
        btn_box = ctk.CTkFrame(parent, fg_color="transparent")
        btn_box.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        
        # ปุ่มรีเฟรช
        refresh_btn = ctk.CTkButton(btn_box, text="🔄 รีเฟรช",
                                   command=self.on_show,
                                   fg_color="#FFB6C1", hover_color="#FFC0CB",
                                   height=40, corner_radius=10,
                                   font=ctk.CTkFont(size=14, weight="bold"))
        refresh_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # ปุ่มดูสถิติ
        stats_btn = ctk.CTkButton(btn_box, text="📊 ดูสถิติเพิ่มเติม",
                                 command=self.go_dashboard,
                                 fg_color="#4CAF50", hover_color="#66BB6A",
                                 height=40, corner_radius=10,
                                 font=ctk.CTkFont(size=14, weight="bold"))
        stats_btn.pack(side="left", padx=5, fill="x", expand=True)
        
        # ปุ่มจัดการ
        manage_btn = ctk.CTkButton(btn_box, text="📦 จัดการคำสั่งซื้อ",
                                  command=self.go_orders,
                                  fg_color="#2196F3", hover_color="#42A5F5",
                                  height=40, corner_radius=10,
                                  font=ctk.CTkFont(size=14, weight="bold"))
        manage_btn.pack(side="left", padx=5, fill="x", expand=True)

    def count_total_items(self):
        """นับจำนวนสินค้าที่ขายทั้งหมด"""
        total = 0
        cursor = None
        
        try:
            cursor = self.db.connect()
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) FROM order_items")
            result = cursor.fetchone()
            if result:
                total = result[0]
        except Exception as error:
            print(f"นับสินค้าไม่สำเร็จ: {error}")
        finally:
            if self.db:
                self.db.close()
        
        return total

    def load_table_data(self):
        """โหลดข้อมูลใส่ตาราง"""
        # ลบข้อมูลเก่า
        for item in self.table.get_children():
            self.table.delete(item)
        
        # ดึงข้อมูลทั้งหมด
        orders = self.db.get_all_orders()
        
        # แปลภาษาสถานะ
        status_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ สำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        payment_map = {
            'โอนเงินผ่านธนาคาร': '🏦 โอนเงิน',
            'เก็บเงินปลายทาง': '📦 COD',
            'Credit Card': '💳 บัตร'
        }
        
        # เพิ่มข้อมูลทีละแถว
        for order in orders:
            # Order ID
            order_id = f"#{order['order_id']}"
            
            # --- 🛠️ ปรับแก้: แปลงเวลา UTC เป็นเวลาไทย (UTC+7) ---
            date_str = order.get('created_at', '-')
            if date_str and date_str != '-':
                try:
                    # 1. แปลง String (UTC) เป็น datetime object
                    utc_dt = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    # 2. บวก 7 ชั่วโมง
                    thai_dt = utc_dt + timedelta(hours=7)
                    # 3. แปลงกลับเป็น String (เวลาไทย)
                    date = thai_dt.strftime('%Y-%m-%d %H:%M')
                except ValueError:
                    date = date_str[:16] # ถ้าแปลงไม่สำเร็จ, ใช้แบบเดิม
            else:
                date = '-'
            # --- 🛠️ สิ้นสุดการปรับแก้ ---
            
            # ลูกค้า
            customer = order.get('full_name', '-')
            
            # รายการสินค้า
            items = order.get('items', '')
            if len(items) > 50:
                items = items[:47] + "..."
            elif not items:
                items = 'ไม่มีรายการ'
            
            # ยอดเงิน
            amount = f"฿{order.get('total_amount', 0):,.2f}"
            
            # วิธีชำระเงิน
            payment = order.get('payment_method', '')
            payment = payment_map.get(payment, payment)
            
            # สถานะ
            status = order.get('status', '')
            status = status_map.get(status, status)
            
            # เพิ่มแถว
            self.table.insert("", "end", values=(
                order_id, date, customer, items,
                amount, payment, status
            ))

    def go_home(self):
        """กลับหน้าหลัก"""
        self.main_app.navigate_to('HomeWindow')

    def go_dashboard(self):
        """ไป Dashboard"""
        self.main_app.navigate_to('AdminDashboardWindow')

    def go_orders(self):
        """ไปหน้าจัดการคำสั่งซื้อ"""
        self.main_app.navigate_to('AdminOrdersWindow')