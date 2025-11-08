import customtkinter as ctk
from tkinter import ttk
from datetime import datetime, timedelta
from tkcalendar import DateEntry

class AdminDashboardWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.db = main_app.db
        
        # ตัวแปรสำหรับเก็บวันที่/เดือน/ปีที่เลือก
        self.selected_date = datetime.now()
        self.selected_month = datetime.now().month
        self.selected_year = datetime.now().year
        
        self.setup_ui()
    
    def on_show(self):
        """รีเฟรชข้อมูลทุกครั้งที่เปิดหน้านี้"""
        # (ล้างและสร้าง UI ใหม่ทั้งหมด เพื่อให้ข้อมูลอัปเดต)
        for widget in self.winfo_children():
            widget.destroy()
        self.setup_ui()
    
    def setup_ui(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # Header
        self.create_header()
        
        # Main Content
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # Row 0: Stats Cards
        self.create_stats_cards(main_frame) # Row 0
        
        # Row 1: Sales History Summary (NEW SECTION)
        self.create_sales_history_summary(main_frame) # Row 1
        
        # Row 2: Charts Section (Low Stock / Top Selling)
        chart_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        chart_frame.grid(row=2, column=0, columnspan=4, sticky="ew", pady=20)
        chart_frame.grid_columnconfigure((0, 1), weight=1)
        
        # Top Selling Products
        self.create_top_products_section(chart_frame)
        
        # Low Stock Alert
        self.create_low_stock_section(chart_frame)
        
        # Row 3: Recent Orders
        self.create_recent_orders_section(main_frame) # Row 3
    
    def create_header(self):
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=70)
        header.grid(row=0, column=0, sticky="ew")
        header.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header, 
            text="📊 Admin Dashboard", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2E7D32"
        ).pack(side="left", padx=30)
        
        btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        btn_frame.pack(side="right", padx=20)
        
        ctk.CTkButton(
            btn_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'),
            fg_color="transparent",
            text_color="gray50",
            hover_color="#F5F5F5"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="⚙️ จัดการสินค้า",
            command=lambda: self.main_app.navigate_to('AdminWindow'),
            fg_color="#FF6B9D",
            hover_color="#FF8FB3"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📦 จัดการคำสั่งซื้อ",
            command=lambda: self.main_app.navigate_to('AdminOrdersWindow'),
            fg_color="#2196F3",
            hover_color="#42A5F5"
        ).pack(side="left", padx=5)
        
        ctk.CTkButton(
            btn_frame,
            text="📊 ประวัติการขาย",
            command=lambda: self.main_app.navigate_to('SalesHistoryWindow'),
            fg_color="#9C27B0",
            hover_color="#BA68C8"
        ).pack(side="left", padx=5)

    # vvvv ฟังก์ชันใหม่สำหรับสรุปยอดขาย (รายวัน/เดือน/ปี) พร้อม Date Selector vvvv
    def create_sales_history_summary(self, parent):
        """สร้างส่วนแสดงยอดขายรวมตามช่วงเวลา พร้อมเลือกวันที่"""
        section = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E0E0E0")
        section.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 20))
        section.grid_columnconfigure(0, weight=1)
        
        # Header
        header_frame = ctk.CTkFrame(section, fg_color="transparent")
        header_frame.grid(row=0, column=0, sticky="ew", pady=(20, 10), padx=20)
        header_frame.grid_columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            header_frame, 
            text="📈 สรุปยอดขายตามช่วงเวลา", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).grid(row=0, column=0, sticky="w")
        
        # Tab Selector
        tab_frame = ctk.CTkFrame(section, fg_color="transparent")
        tab_frame.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        self.period_var = ctk.StringVar(value="รายวัน")
        
        ctk.CTkSegmentedButton(
            tab_frame,
            values=["รายวัน", "รายเดือน", "รายปี"],
            command=self.on_period_change,
            variable=self.period_var,
            fg_color="#E0E0E0",
            selected_color="#4CAF50",
            selected_hover_color="#66BB6A",
            unselected_color="white",
            unselected_hover_color="#F5F5F5"
        ).pack(side="left", padx=(0, 20))
        
        # Date Selector Frame (จะเปลี่ยนตามประเภทที่เลือก)
        self.date_selector_frame = ctk.CTkFrame(tab_frame, fg_color="transparent")
        self.date_selector_frame.pack(side="left", fill="x", expand=True)
        
        # สร้าง Date Selector เริ่มต้น
        self.create_date_selector()
        
        # Cards Container
        self.cards_container = ctk.CTkFrame(section, fg_color="transparent")
        self.cards_container.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.cards_container.grid_columnconfigure((0, 1, 2), weight=1)
        
        # แสดงข้อมูลเริ่มต้น
        self.update_sales_display()
    
    def create_date_selector(self):
        """สร้าง Date Selector ตามประเภทที่เลือก"""
        # ลบ widgets เดิมออก
        for widget in self.date_selector_frame.winfo_children():
            widget.destroy()
        
        period = self.period_var.get()
        
        if period == "รายวัน":
            self.create_daily_selector()
        elif period == "รายเดือน":
            self.create_monthly_selector()
        else:  # รายปี
            self.create_yearly_selector()
    
    def create_daily_selector(self):
        """สร้าง Date Picker สำหรับเลือกวัน"""
        ctk.CTkLabel(
            self.date_selector_frame,
            text="เลือกวันที่:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        # DateEntry (จาก tkcalendar)
        self.date_picker = DateEntry(
            self.date_selector_frame,
            width=15,
            background='#4CAF50',
            foreground='white',
            borderwidth=2,
            date_pattern='dd/mm/yyyy',
            mindate=datetime(2024, 1, 1),  # เริ่มร้าน 1 ม.ค. 2567
            maxdate=datetime.now(),
            font=('Arial', 11)
        )
        self.date_picker.pack(side="left", padx=(0, 10))
        self.date_picker.bind("<<DateEntrySelected>>", lambda e: self.on_date_selected())
        
        ctk.CTkButton(
            self.date_selector_frame,
            text="วันนี้",
            width=80,
            command=self.set_today,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        ).pack(side="left", padx=5)
    
    def create_monthly_selector(self):
        """สร้าง Dropdown สำหรับเลือกเดือน/ปี"""
        ctk.CTkLabel(
            self.date_selector_frame,
            text="เลือกเดือน:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        # Dropdown เดือน
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                     "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        
        current_month_idx = datetime.now().month - 1
        self.month_var = ctk.StringVar(value=months_th[current_month_idx])
        
        month_menu = ctk.CTkOptionMenu(
            self.date_selector_frame,
            values=months_th,
            variable=self.month_var,
            command=lambda _: self.on_month_selected(),
            width=120,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        month_menu.pack(side="left", padx=(0, 10))
        
        # Dropdown ปี (2024-ปีปัจจุบัน)
        current_year = datetime.now().year
        years = [str(y) for y in range(2024, current_year + 1)]
        
        self.year_var = ctk.StringVar(value=str(current_year))
        
        year_menu = ctk.CTkOptionMenu(
            self.date_selector_frame,
            values=years,
            variable=self.year_var,
            command=lambda _: self.on_month_selected(),
            width=100,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        year_menu.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            self.date_selector_frame,
            text="เดือนนี้",
            width=100,
            command=self.set_current_month,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        ).pack(side="left", padx=5)
    
    def create_yearly_selector(self):
        """สร้าง Dropdown สำหรับเลือกปี"""
        ctk.CTkLabel(
            self.date_selector_frame,
            text="เลือกปี:",
            font=ctk.CTkFont(size=13)
        ).pack(side="left", padx=(0, 10))
        
        # Dropdown ปี
        current_year = datetime.now().year
        years = [str(y) for y in range(2024, current_year + 1)]
        
        self.year_select_var = ctk.StringVar(value=str(current_year))
        
        year_menu = ctk.CTkOptionMenu(
            self.date_selector_frame,
            values=years,
            variable=self.year_select_var,
            command=lambda _: self.on_year_selected(),
            width=120,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        year_menu.pack(side="left", padx=(0, 10))
        
        ctk.CTkButton(
            self.date_selector_frame,
            text="ปีนี้",
            width=80,
            command=self.set_current_year,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        ).pack(side="left", padx=5)
    
    def on_period_change(self, value):
        """เมื่อเปลี่ยนประเภทช่วงเวลา"""
        # value ที่ได้คือ "รายวัน", "รายเดือน", "รายปี" จาก Segmented Button
        self.create_date_selector()
        self.update_sales_display()
    
    def on_date_selected(self):
        """เมื่อเลือกวันที่"""
        self.selected_date = self.date_picker.get_date()
        self.update_sales_display()
    
    def on_month_selected(self):
        """เมื่อเลือกเดือน"""
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                     "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        self.selected_month = months_th.index(self.month_var.get()) + 1
        self.selected_year = int(self.year_var.get())
        self.update_sales_display()
    
    def on_year_selected(self):
        """เมื่อเลือกปี"""
        self.selected_year = int(self.year_select_var.get())
        self.update_sales_display()
    
    def set_today(self):
        """ตั้งค่าเป็นวันนี้"""
        self.date_picker.set_date(datetime.now())
        self.selected_date = datetime.now()
        self.update_sales_display()
    
    def set_current_month(self):
        """ตั้งค่าเป็นเดือนปัจจุบัน"""
        now = datetime.now()
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                     "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        self.month_var.set(months_th[now.month - 1])
        self.year_var.set(str(now.year))
        self.selected_month = now.month
        self.selected_year = now.year
        self.update_sales_display()
    
    def set_current_year(self):
        """ตั้งค่าเป็นปีปัจจุบัน"""
        now = datetime.now()
        self.year_select_var.set(str(now.year))
        self.selected_year = now.year
        self.update_sales_display()
    
    def update_sales_display(self):
        """อัปเดตการแสดงยอดขาย"""
        # ลบการ์ดเดิมออก
        for widget in self.cards_container.winfo_children():
            widget.destroy()
        
        period = self.period_var.get()
        
        # ตรวจสอบว่า period เป็นภาษาไทยหรือภาษาอังกฤษ
        if period == "รายวัน":
            self.show_daily_sales()
        elif period == "รายเดือน":
            self.show_monthly_sales()
        elif period == "รายปี":
            self.show_yearly_sales()
        else:
            # กรณีที่ยังไม่ได้เลือก แสดงรายวัน
            self.show_daily_sales()
    
    def show_daily_sales(self):
        """แสดงยอดขายรายวัน"""
        date_str = self.selected_date.strftime('%Y-%m-%d')
        data = self.db.get_sales_by_date(date_str)
        
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        date_display = self.selected_date.strftime('%d/%m/%Y')
        
        summary_cards = [
            {
                'title': f'รายได้วันที่ {date_display}',
                'value': f"฿{revenue:,.2f}",
                'icon': '☀️',
                'color': '#FF9800'
            },
            {
                'title': 'จำนวนคำสั่งซื้อ',
                'value': f"{orders}",
                'icon': '🛒',
                'color': '#2196F3'
            },
            {
                'title': 'ยอดเฉลี่ยต่อออเดอร์',
                'value': f"฿{(revenue / orders):,.2f}" if orders > 0 else "฿0.00",
                'icon': '📊',
                'color': '#9C27B0'
            }
        ]
        
        for i, card_data in enumerate(summary_cards):
            card = self.create_summary_card(self.cards_container, card_data)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    def show_monthly_sales(self):
        """แสดงยอดขายรายเดือน"""
        date_str = f"{self.selected_year}-{self.selected_month:02d}"
        data = self.db.get_sales_by_month(date_str)
        
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        months_th = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                     "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        month_name = months_th[self.selected_month - 1]
        
        summary_cards = [
            {
                'title': f'รายได้ {month_name} {self.selected_year}',
                'value': f"฿{revenue:,.2f}",
                'icon': '📅',
                'color': '#2196F3'
            },
            {
                'title': 'จำนวนคำสั่งซื้อ',
                'value': f"{orders}",
                'icon': '🛒',
                'color': '#FF9800'
            },
            {
                'title': 'ยอดเฉลี่ยต่อออเดอร์',
                'value': f"฿{(revenue / orders):,.2f}" if orders > 0 else "฿0.00",
                'icon': '📊',
                'color': '#9C27B0'
            }
        ]
        
        for i, card_data in enumerate(summary_cards):
            card = self.create_summary_card(self.cards_container, card_data)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    def show_yearly_sales(self):
        """แสดงยอดขายรายปี"""
        data = self.db.get_sales_by_year(str(self.selected_year))
        
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        summary_cards = [
            {
                'title': f'รายได้รวมปี {self.selected_year}',
                'value': f"฿{revenue:,.2f}",
                'icon': '🗓️',
                'color': '#4CAF50'
            },
            {
                'title': 'จำนวนคำสั่งซื้อ',
                'value': f"{orders}",
                'icon': '🛒',
                'color': '#FF9800'
            },
            {
                'title': 'ยอดเฉลี่ยต่อออเดอร์',
                'value': f"฿{(revenue / orders):,.2f}" if orders > 0 else "฿0.00",
                'icon': '📊',
                'color': '#9C27B0'
            }
        ]
        
        for i, card_data in enumerate(summary_cards):
            card = self.create_summary_card(self.cards_container, card_data)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")

    def create_summary_card(self, parent, data):
        """สร้างการ์ดสรุปยอดขายแต่ละใบ"""
        card = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=10)
        card.grid_columnconfigure(1, weight=1)
        
        # Icon
        ctk.CTkLabel(
            card, 
            text=data['icon'], 
            font=ctk.CTkFont(size=30)
        ).grid(row=0, column=0, padx=(15, 5), pady=15, sticky="nsw")
        
        info_frame = ctk.CTkFrame(card, fg_color="transparent")
        info_frame.grid(row=0, column=1, padx=(5, 15), pady=10, sticky="ew")
        info_frame.grid_columnconfigure(0, weight=1)
        
        # Title
        ctk.CTkLabel(
            info_frame, 
            text=data['title'], 
            font=ctk.CTkFont(size=13),
            text_color="gray50",
            anchor="w"
        ).pack(anchor="w")
        
        # Value
        ctk.CTkLabel(
            info_frame, 
            text=data['value'], 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=data['color'],
            anchor="w"
        ).pack(anchor="w")
        
        return card
    # ^^^^ สิ้นสุดฟังก์ชันใหม่ ^^^^
    
    def create_stats_cards(self, parent):
        """สร้างการ์ดแสดงสถิติ"""
        stats = self.db.get_dashboard_stats()
        
        cards_data = [
            {
                'title': 'ยอดขายรวม',
                'value': f"{stats['total_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'icon': '🛒',
                'color': '#4CAF50'
            },
            {
                'title': 'รายได้ทั้งหมด',
                'value': f"฿{stats['total_revenue']:,.2f}",
                'subtitle': 'บาท',
                'icon': '💰',
                'color': '#2196F3'
            },
            {
                'title': 'สินค้าทั้งหมด',
                'value': f"{stats['total_products']}",
                'subtitle': 'รายการ',
                'icon': '📦',
                'color': '#FF9800'
            },
            {
                'title': 'รอดำเนินการ',
                'value': f"{stats['pending_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'icon': '⏳',
                'color': '#F44336'
            }
        ]
        
        for i, card_data in enumerate(cards_data):
            card = self.create_stat_card(parent, card_data)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    def create_stat_card(self, parent, data):
        """สร้างการ์ดสถิติแต่ละใบ"""
        card = ctk.CTkFrame(parent, fg_color="white", corner_radius=15, border_width=1, border_color="#E0E0E0")
        card.grid_columnconfigure(0, weight=1)
        
        # Icon
        icon_label = ctk.CTkLabel(
            card, 
            text=data['icon'], 
            font=ctk.CTkFont(size=40)
        )
        icon_label.grid(row=0, column=0, pady=(20, 10))
        
        # Title
        ctk.CTkLabel(
            card, 
            text=data['title'], 
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        ).grid(row=1, column=0, pady=5)
        
        # Value
        ctk.CTkLabel(
            card, 
            text=data['value'], 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=data['color']
        ).grid(row=2, column=0, pady=5)
        
        # Subtitle
        ctk.CTkLabel(
            card, 
            text=data['subtitle'], 
            font=ctk.CTkFont(size=12),
            text_color="gray40"
        ).grid(row=3, column=0, pady=(5, 20))
        
        return card
    
    def create_top_products_section(self, parent):
        """แสดงสินค้าขายดี"""
        section = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        section.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            section, 
            text="🏆 สินค้าขายดี Top 5", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        top_products = self.db.get_top_selling_products(5)
        
        if top_products:
            for i, product in enumerate(top_products, 1):
                item_frame = ctk.CTkFrame(section, fg_color="#F5F5F5", corner_radius=10)
                item_frame.pack(fill="x", padx=20, pady=5)
                
                rank_label = ctk.CTkLabel(
                    item_frame, 
                    text=f"#{i}", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FF6B9D",
                    width=40
                )
                rank_label.pack(side="left", padx=10, pady=10)
                
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10)
                
                ctk.CTkLabel(
                    info_frame, 
                    text=product['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                ).pack(anchor="w")
                
                ctk.CTkLabel(
                    info_frame, 
                    text=f"ขายได้: {product['total_sold']} ชิ้น | รายได้: ฿{product['total_revenue']:,.2f}", 
                    font=ctk.CTkFont(size=12),
                    text_color="gray50",
                    anchor="w"
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                section, 
                text="ยังไม่มีข้อมูลการขาย", 
                text_color="gray50"
            ).pack(pady=20)
        
        ctk.CTkLabel(section, text="").pack(pady=10)  # Spacer
    
    def create_low_stock_section(self, parent):
        """แสดงสินค้าที่สต็อกต่ำ"""
        section = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        section.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        ctk.CTkLabel(
            section, 
            text="⚠️ สินค้าสต็อกต่ำ", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F44336"
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        low_stock = self.db.get_low_stock_products(10)
        
        if low_stock:
            for product in low_stock[:5]:  # แสดงแค่ 5 รายการแรก
                item_frame = ctk.CTkFrame(section, fg_color="#FFEBEE", corner_radius=10)
                item_frame.pack(fill="x", padx=20, pady=5)
                
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                ctk.CTkLabel(
                    info_frame, 
                    text=product['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                ).pack(anchor="w")
                
                stock_color = "#F44336" if product['stock'] < 5 else "#FF9800"
                ctk.CTkLabel(
                    info_frame, 
                    text=f"เหลือ: {product['stock']} ชิ้น", 
                    font=ctk.CTkFont(size=12),
                    text_color=stock_color,
                    anchor="w"
                ).pack(anchor="w")
        else:
            ctk.CTkLabel(
                section, 
                text="สต็อกสินค้าเพียงพอทั้งหมด ✓", 
                text_color="#4CAF50"
            ).pack(pady=20)
        
        ctk.CTkLabel(section, text="").pack(pady=10)  # Spacer
    
    def create_recent_orders_section(self, parent):
        """แสดงคำสั่งซื้อล่าสุด"""
        section = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        section.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=20)
        
        ctk.CTkLabel(
            section, 
            text="📋 คำสั่งซื้อล่าสุด", 
            font=ctk.CTkFont(size=18, weight="bold")
        ).pack(pady=(20, 10), padx=20, anchor="w")
        
        # Treeview
        style = ttk.Style()
        style.configure("Dashboard.Treeview", rowheight=35, font=('Arial', 11))
        style.configure("Dashboard.Treeview.Heading", font=('Arial', 12, 'bold'))
        
        columns = ("order_id", "customer", "amount", "status", "date")
        tree = ttk.Treeview(section, columns=columns, show="headings", height=8, style="Dashboard.Treeview")
        
        tree.heading("order_id", text="Order ID")
        tree.heading("customer", text="ลูกค้า")
        tree.heading("amount", text="ยอดเงิน")
        tree.heading("status", text="สถานะ")
        tree.heading("date", text="วันที่")
        
        tree.column("order_id", width=80, anchor="center")
        tree.column("customer", width=200)
        tree.column("amount", width=120, anchor="e")
        tree.column("status", width=120, anchor="center")
        tree.column("date", width=150, anchor="center")
        
        tree.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        recent_orders = self.db.get_recent_orders(10)
        
        status_text = {
            'pending': 'รอดำเนินการ',
            'confirmed': 'ยืนยันแล้ว',
            'shipped': 'จัดส่งแล้ว',
            'delivered': 'ส่งสำเร็จ',
            'cancelled': 'ยกเลิก'
        }
        
        for order in recent_orders:
            tree.insert("", "end", values=(
                f"#{order['order_id']}",
                order['full_name'],
                f"฿{order['total_amount']:,.2f}",
                status_text.get(order['status'], order['status']),
                order['created_at'][:16] if order['created_at'] else '-'
            ))