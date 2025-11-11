"""
หน้า Admin Dashboard - แสดงสถิติและข้อมูลสรุป
- สถิติรวม (ยอดขาย, รายได้, สินค้า, คำสั่งซื้อรอดำเนินการ)
- สรุปยอดขายตามช่วงเวลา (รายวัน/เดือน/ปี)
- สินค้าขายดี Top 5
- สินค้าสต็อกต่ำ
"""

import customtkinter as ctk
from tkinter import ttk, messagebox
from datetime import datetime, timedelta # 👈 1. Import timedelta
from tkcalendar import Calendar  # ใช้ปฏิทินแบบฝัง


class AdminDashboardWindow(ctk.CTkFrame):
    """หน้าจอแดชบอร์ดแอดมิน"""
    
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.db = main_app.db
        
        self.selected_date = datetime.now()
        self.selected_month = datetime.now().month
        self.selected_year = datetime.now().year
        
        self.calendar = None 
        
        # สร้าง UI
        self.create_layout()
    
    
    def on_show(self):
        """ฟังก์ชันนี้จะถูกเรียกทุกครั้งที่เปิดหน้านี้"""
        # ล้าง UI เดิมและสร้างใหม่ เพื่ออัปเดตข้อมูล
        for widget in self.winfo_children():
            widget.destroy()
        self.create_layout()
    
    
    def create_layout(self):
        """สร้างโครงสร้างหน้าจอ"""
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # สร้างส่วนต่างๆ
        self.create_top_menu()              # แถบเมนูด้านบน
        self.create_content_area()          # พื้นที่เนื้อหาหลัก
    
    
    # ==================== แถบเมนูด้านบน ====================
    def create_top_menu(self):
        """สร้างแถบเมนูด้านบน"""
        menu_bar = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=70)
        menu_bar.grid(row=0, column=0, sticky="ew")
        menu_bar.grid_columnconfigure(1, weight=1)
        
        title = ctk.CTkLabel(
            menu_bar, 
            text="📊 Admin Dashboard", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2E7D32"
        )
        title.pack(side="left", padx=30)
        
        button_area = ctk.CTkFrame(menu_bar, fg_color="transparent")
        button_area.pack(side="right", padx=20)
        
        btn_home = ctk.CTkButton(
            button_area,
            text="🏠 หน้าหลัก",
            command=self.go_to_home,
            fg_color="transparent",
            text_color="gray50",
            hover_color="#F5F5F5"
        )
        btn_home.pack(side="left", padx=5)
        
        btn_products = ctk.CTkButton(
            button_area,
            text="⚙️ จัดการสินค้า",
            command=self.go_to_products,
            fg_color="#FF6B9D",
            hover_color="#FF8FB3"
        )
        btn_products.pack(side="left", padx=5)
        
        btn_orders = ctk.CTkButton(
            button_area,
            text="📦 จัดการคำสั่งซื้อ",
            command=self.go_to_orders,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        )
        btn_orders.pack(side="left", padx=5)
        
        btn_history = ctk.CTkButton(
            button_area,
            text="📊 ประวัติการขาย",
            command=self.go_to_sales_history,
            fg_color="#9C27B0",
            hover_color="#BA68C8"
        )
        btn_history.pack(side="left", padx=5)
        
        btn_users = ctk.CTkButton(
            button_area,
            text="👥 จัดการผู้ใช้",
            command=self.go_to_users,
            fg_color="#FF9800",
            hover_color="#FFA726"
        )
        btn_users.pack(side="left", padx=5)
    
    
    # ฟังก์ชันไปหน้าต่างๆ
    def go_to_home(self):
        self.main_app.navigate_to('HomeWindow')
    
    def go_to_products(self):
        self.main_app.navigate_to('AdminWindow')
    
    def go_to_orders(self):
        self.main_app.navigate_to('AdminOrdersWindow')
    
    def go_to_sales_history(self):
        self.main_app.navigate_to('SalesHistoryWindow')
    
    def go_to_users(self):
        self.main_app.navigate_to('AdminUsersWindow')
    
    
    # ==================== พื้นที่เนื้อหาหลัก ====================
    def create_content_area(self):
        """สร้างพื้นที่เนื้อหาหลัก (เลื่อนได้)"""
        scroll_area = ctk.CTkScrollableFrame(self, fg_color="transparent")
        scroll_area.grid(row=1, column=0, sticky="nsew", padx=30, pady=20)
        scroll_area.grid_columnconfigure((0, 1, 2, 3), weight=1)
        
        # แถวที่ 0: การ์ดสถิติรวม (4 ใบ)
        self.create_stat_cards(scroll_area)
        
        # แถวที่ 1: สรุปยอดขายตามช่วงเวลา
        self.create_sales_summary_section(scroll_area)
        
        # แถวที่ 2: สินค้าขายดี + สต็อกต่ำ
        self.create_products_section(scroll_area)
        
        # แถวที่ 3: คำสั่งซื้อล่าสุด
        self.create_orders_table(scroll_area)
    
    
    # ==================== การ์ดสถิติรวม ====================
    def create_stat_cards(self, parent):
        """สร้างการ์ดแสดงสถิติรวม 4 ใบ"""
        stats = self.db.get_dashboard_stats()
        
        cards = [
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
        
        for i, card_info in enumerate(cards):
            card = self.make_stat_card(parent, card_info)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    
    def make_stat_card(self, parent, info):
        """สร้างการ์ดสถิติ 1 ใบ"""
        card = ctk.CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=15, 
            border_width=1, 
            border_color="#E0E0E0"
        )
        card.grid_columnconfigure(0, weight=1)
        
        icon = ctk.CTkLabel(
            card, 
            text=info['icon'], 
            font=ctk.CTkFont(size=40)
        )
        icon.grid(row=0, column=0, pady=(20, 10))
        
        title = ctk.CTkLabel(
            card, 
            text=info['title'], 
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        title.grid(row=1, column=0, pady=5)
        
        value = ctk.CTkLabel(
            card, 
            text=info['value'], 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color=info['color']
        )
        value.grid(row=2, column=0, pady=5)
        
        subtitle = ctk.CTkLabel(
            card, 
            text=info['subtitle'], 
            font=ctk.CTkFont(size=12),
            text_color="gray40"
        )
        subtitle.grid(row=3, column=0, pady=(5, 20))
        
        return card
    
    
    # ==================== สรุปยอดขายตามช่วงเวลา ====================
    def create_sales_summary_section(self, parent):
        """สร้างส่วนแสดงยอดขายตามช่วงเวลา"""
        section = ctk.CTkFrame(
            parent, 
            fg_color="white", 
            corner_radius=15, 
            border_width=1, 
            border_color="#E0E0E0"
        )
        section.grid(row=1, column=0, columnspan=4, sticky="ew", pady=(10, 20))
        section.grid_columnconfigure(0, weight=1)
        
        self.create_summary_header(section)
        self.create_time_selector(section)
        
        self.sales_cards_area = ctk.CTkFrame(section, fg_color="transparent")
        self.sales_cards_area.grid(row=2, column=0, sticky="ew", padx=20, pady=(0, 20))
        self.sales_cards_area.grid_columnconfigure((0, 1, 2), weight=1)
        
        self.update_sales_display()
    
    
    def create_summary_header(self, parent):
        """สร้างส่วนหัวของสรุปยอดขาย"""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.grid(row=0, column=0, sticky="ew", pady=(20, 10), padx=20)
        
        title = ctk.CTkLabel(
            header, 
            text="📈 สรุปยอดขายตามช่วงเวลา", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(side="left")
    
    
    def create_time_selector(self, parent):
        """สร้างส่วนเลือกช่วงเวลา"""
        selector_area = ctk.CTkFrame(parent, fg_color="transparent")
        selector_area.grid(row=1, column=0, sticky="ew", padx=20, pady=(0, 15))
        
        self.period_type = ctk.StringVar(value="รายวัน")
        
        period_buttons = ctk.CTkSegmentedButton(
            selector_area,
            values=["รายวัน", "รายเดือน", "รายปี"],
            command=self.on_period_changed,
            variable=self.period_type,
            fg_color="#E0E0E0",
            selected_color="#4CAF50",
            selected_hover_color="#66BB6A",
            unselected_color="white",
            unselected_hover_color="#F5F5F5"
        )
        period_buttons.pack(side="left", padx=(0, 20))
        
        self.date_picker_area = ctk.CTkFrame(selector_area, fg_color="transparent")
        self.date_picker_area.pack(side="left", fill="x", expand=True)
        
        self.create_date_picker()
    
    
    def create_date_picker(self):
        """สร้าง Date Picker ตามประเภทที่เลือก"""
        for widget in self.date_picker_area.winfo_children():
            widget.destroy()
            
        self.calendar = None 
        
        period = self.period_type.get()
        
        if period == "รายวัน":
            self.create_daily_picker()
        elif period == "รายเดือน":
            self.create_monthly_picker()
        else:  # รายปี
            self.create_yearly_picker()
    
    
    def create_daily_picker(self):
        """สร้าง Date Picker แบบรายวัน (ฝังปฏิทิน)"""
        
        btn_today = ctk.CTkButton(
            self.date_picker_area,
            text="ข้ามไปวันนี้",
            width=120,
            command=self.set_today,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        )
        btn_today.pack(side="top", anchor="e", pady=(0, 10))

        self.calendar = Calendar(
            self.date_picker_area,
            selectmode='day',
            date_pattern='dd/mm/yyyy', 
            mindate=datetime(2024, 1, 1), 
            maxdate=datetime.now(),
            background="#2E7D32",
            foreground="white",
            headersbackground="#81C784", 
            headersforeground="#2E7D32",
            selectbackground="#FFEB3B",
            selectforeground="#000000",
            normalbackground="white",
            normalforeground="black",
            othermonthbackground="#E0E0E0", 
            othermonthforeground="gray",
            weekendbackground="white",
            weekendforeground="black",
            disabledbackground="#F5F5F5",
            disabledforeground="#BDBDBD",
            year=self.selected_date.year,
            month=self.selected_date.month,
            day=self.selected_date.day
        )
        self.calendar.pack(fill="both", expand=True)
        
        # --- 🛠️ (แก้ไข) เปิดใช้งานฟังก์ชันมาร์คสี ---
        # (ฟังก์ชันนี้ถูกย้ายไปอยู่ข้างล่าง และมี try...except ครอบแล้ว)
        self.mark_sales_days_on_calendar() 
        
        self.calendar.bind("<<CalendarSelected>>", self.on_date_picked)

    
    def create_monthly_picker(self):
        """สร้าง Picker แบบรายเดือน"""
        label = ctk.CTkLabel(
            self.date_picker_area,
            text="เลือกเดือน:",
            font=ctk.CTkFont(size=13)
        )
        label.pack(side="left", padx=(0, 10))
        
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        
        current_month = datetime.now().month - 1
        self.month_dropdown = ctk.StringVar(value=months[current_month])
        
        menu_month = ctk.CTkOptionMenu(
            self.date_picker_area,
            values=months,
            variable=self.month_dropdown,
            command=lambda x: self.on_month_picked(),
            width=120,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        menu_month.pack(side="left", padx=(0, 10))
        
        current_year = datetime.now().year
        years = [str(y) for y in range(2024, current_year + 6)] 
        
        self.year_dropdown = ctk.StringVar(value=str(current_year))
        
        menu_year = ctk.CTkOptionMenu(
            self.date_picker_area,
            values=years,
            variable=self.year_dropdown,
            command=lambda x: self.on_month_picked(),
            width=100,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        menu_year.pack(side="left", padx=(0, 10))
        
        btn_this_month = ctk.CTkButton(
            self.date_picker_area,
            text="เดือนนี้",
            width=100,
            command=self.set_current_month,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        )
        btn_this_month.pack(side="left", padx=5)
    
    
    def create_yearly_picker(self):
        """สร้าง Picker แบบรายปี"""
        label = ctk.CTkLabel(
            self.date_picker_area,
            text="เลือกปี:",
            font=ctk.CTkFont(size=13)
        )
        label.pack(side="left", padx=(0, 10))
        
        current_year = datetime.now().year
        years = [str(y) for y in range(2024, current_year + 6)] 
        
        self.year_select = ctk.StringVar(value=str(current_year))
        
        menu_year = ctk.CTkOptionMenu(
            self.date_picker_area,
            values=years,
            variable=self.year_select,
            command=lambda x: self.on_year_picked(),
            width=120,
            fg_color="#4CAF50",
            button_color="#66BB6A",
            button_hover_color="#81C784"
        )
        menu_year.pack(side="left", padx=(0, 10))
        
        btn_this_year = ctk.CTkButton(
            self.date_picker_area,
            text="ปีนี้",
            width=80,
            command=self.set_current_year,
            fg_color="#2196F3",
            hover_color="#42A5F5"
        )
        btn_this_year.pack(side="left", padx=5)
    
    
    # ฟังก์ชัน Callback เมื่อเปลี่ยนวันที่/เดือน/ปี
    def on_period_changed(self, value):
        """เมื่อเปลี่ยนประเภทช่วงเวลา"""
        self.create_date_picker()
        self.update_sales_display()
    
    
    def on_date_picked(self, event=None):
        """เมื่อคลิกเลือกวันในปฏิทิน"""
        try:
            date_string = self.calendar.get_date() 
            self.selected_date = datetime.strptime(date_string, '%d/%m/%Y')
            self.update_sales_display()
        except Exception as e:
            print(f"Error parsing date: {e}")
            messagebox.showerror("ผิดพลาด", "ไม่สามารถอ่านวันที่จากปฏิทินได้")
    
    def on_month_picked(self):
        """เมื่อเลือกเดือน"""
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        
        month_name = self.month_dropdown.get()
        self.selected_month = months.index(month_name) + 1
        self.selected_year = int(self.year_dropdown.get())
        self.update_sales_display()
    
    def on_year_picked(self):
        """เมื่อเลือกปี"""
        self.selected_year = int(self.year_select.get())
        self.update_sales_display()
    
    
    # ฟังก์ชันตั้งค่าวันที่เร็ว
    def set_today(self):
        """ตั้งค่าเป็นวันนี้"""
        today = datetime.now()
        if self.calendar: 
            self.calendar.selection_set(today) 
            self.selected_date = today
            self.update_sales_display()
    
    def set_current_month(self):
        """ตั้งค่าเป็นเดือนปัจจุบัน"""
        now = datetime.now()
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        
        self.month_dropdown.set(months[now.month - 1])
        self.year_dropdown.set(str(now.year))
        self.selected_month = now.month
        self.selected_year = now.year
        self.update_sales_display()
    
    def set_current_year(self):
        """ตั้งค่าเป็นปีปัจจุบัน"""
        now = datetime.now()
        self.year_select.set(str(now.year))
        self.selected_year = now.year
        self.update_sales_display()
    
    
    def update_sales_display(self):
        """อัปเดตการแสดงยอดขาย"""
        for widget in self.sales_cards_area.winfo_children():
            widget.destroy()
        
        period = self.period_type.get()
        
        if period == "รายวัน":
            self.show_daily_sales()
        elif period == "รายเดือน":
            self.show_monthly_sales()
        else:  # รายปี
            self.show_yearly_sales()
    
    
    def show_daily_sales(self):
        """แสดงยอดขายรายวัน"""
        date_string = self.selected_date.strftime('%Y-%m-%d')
        
        data = self.db.get_sales_by_date(date_string)
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        items_data = self.db.get_items_sold_by_date(date_string)
        items_sold = items_data[0]['total_items'] if items_data else 0
        
        date_display = self.selected_date.strftime('%d/%m/%Y')
        
        cards = [
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
                'title': 'จำนวนสินค้าที่ขายได้', 
                'value': f"{items_sold} ชิ้น",  
                'icon': '📦',                   
                'color': '#9C27B0'
            }
        ]
        
        for i, card_info in enumerate(cards):
            card = self.make_sales_card(self.sales_cards_area, card_info)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    
    def show_monthly_sales(self):
        """แสดงยอดขายรายเดือน"""
        date_string = f"{self.selected_year}-{self.selected_month:02d}"
        
        data = self.db.get_sales_by_month(date_string)
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        items_data = self.db.get_items_sold_by_month(date_string)
        items_sold = items_data[0]['total_items'] if items_data else 0
        
        months = ["มกราคม", "กุมภาพันธ์", "มีนาคม", "เมษายน", "พฤษภาคม", "มิถุนายน",
                  "กรกฎาคม", "สิงหาคม", "กันยายน", "ตุลาคม", "พฤศจิกายน", "ธันวาคม"]
        month_name = months[self.selected_month - 1]
        
        cards = [
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
                'title': 'จำนวนสินค้าที่ขายได้', 
                'value': f"{items_sold} ชิ้น",  
                'icon': '📦',                   
                'color': '#9C27B0'
            }
        ]
        
        for i, card_info in enumerate(cards):
            card = self.make_sales_card(self.sales_cards_area, card_info)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    
    def show_yearly_sales(self):
        """แสดงยอดขายรายปี"""
        year_string = str(self.selected_year)
        
        data = self.db.get_sales_by_year(year_string)
        revenue = data[0]['total_revenue'] if data else 0.0
        orders = data[0]['order_count'] if data else 0
        
        items_data = self.db.get_items_sold_by_year(year_string)
        items_sold = items_data[0]['total_items'] if items_data else 0
        
        cards = [
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
                'title': 'จำนวนสินค้าที่ขายได้', 
                'value': f"{items_sold} ชิ้น", 
                'icon': '📦',                   
                'color': '#9C27B0'
            }
        ]
        
        for i, card_info in enumerate(cards):
            card = self.make_sales_card(self.sales_cards_area, card_info)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew")
    
    
    def make_sales_card(self, parent, info):
        """สร้างการ์ดยอดขาย 1 ใบ"""
        card = ctk.CTkFrame(parent, fg_color="#F8F9FA", corner_radius=10)
        card.grid_columnconfigure(1, weight=1)
        
        icon = ctk.CTkLabel(
            card, 
            text=info['icon'], 
            font=ctk.CTkFont(size=30)
        )
        icon.grid(row=0, column=0, padx=(15, 5), pady=15, sticky="nsw")
        
        info_area = ctk.CTkFrame(card, fg_color="transparent")
        info_area.grid(row=0, column=1, padx=(5, 15), pady=10, sticky="ew")
        info_area.grid_columnconfigure(0, weight=1)
        
        title = ctk.CTkLabel(
            info_area, 
            text=info['title'], 
            font=ctk.CTkFont(size=13),
            text_color="gray50",
            anchor="w"
        )
        title.pack(anchor="w")
        
        value = ctk.CTkLabel(
            info_area, 
            text=info['value'], 
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=info['color'],
            anchor="w"
        )
        value.pack(anchor="w")
        
        return card
    
    
    # ==================== สินค้าขายดี + สต็อกต่ำ ====================
    def create_products_section(self, parent):
        """สร้างส่วนแสดงสินค้าขายดีและสต็อกต่ำ"""
        products_area = ctk.CTkFrame(parent, fg_color="transparent")
        products_area.grid(row=2, column=0, columnspan=4, sticky="ew", pady=20)
        products_area.grid_columnconfigure((0, 1), weight=1)
        
        self.create_top_products(products_area)
        self.create_low_stock(products_area)
    
    
    def create_top_products(self, parent):
        """สร้างส่วนแสดงสินค้าขายดี"""
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        box.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            box, 
            text="🏆 สินค้าขายดี Top 5", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        top_products = self.db.get_top_selling_products(5)
        
        if top_products:
            for i, product in enumerate(top_products, 1):
                item = ctk.CTkFrame(box, fg_color="#F5F5F5", corner_radius=10)
                item.pack(fill="x", padx=20, pady=5)
                
                rank = ctk.CTkLabel(
                    item, 
                    text=f"#{i}", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FF6B9D",
                    width=40
                )
                rank.pack(side="left", padx=10, pady=10)
                
                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=10)
                
                name = ctk.CTkLabel(
                    info, 
                    text=product['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name.pack(anchor="w")
                
                details = ctk.CTkLabel(
                    info, 
                    text=f"ขายได้: {product['total_sold']} ชิ้น | รายได้: ฿{product['total_revenue']:,.2f}", 
                    font=ctk.CTkFont(size=12),
                    text_color="gray50",
                    anchor="w"
                )
                details.pack(anchor="w")
        else:
            no_data = ctk.CTkLabel(
                box, 
                text="ยังไม่มีข้อมูลการขาย", 
                text_color="gray50"
            )
            no_data.pack(pady=20)
        
        spacer = ctk.CTkLabel(box, text="")
        spacer.pack(pady=10)
    
    
    def create_low_stock(self, parent):
        """สร้างส่วนแสดงสินค้าสต็อกต่ำ"""
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        box.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        title = ctk.CTkLabel(
            box, 
            text="⚠️ สินค้าสต็อกต่ำ", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F44336"
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        low_stock = self.db.get_low_stock_products(10)
        
        if low_stock:
            for product in low_stock[:5]:
                item = ctk.CTkFrame(box, fg_color="#FFEBEE", corner_radius=10)
                item.pack(fill="x", padx=20, pady=5)
                
                info = ctk.CTkFrame(item, fg_color="transparent")
                info.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                name = ctk.CTkLabel(
                    info, 
                    text=product['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name.pack(anchor="w")
                
                stock_color = "#F44336" if product['stock'] < 5 else "#FF9800"
                
                stock = ctk.CTkLabel(
                    info, 
                    text=f"เหลือ: {product['stock']} ชิ้น", 
                    font=ctk.CTkFont(size=12),
                    text_color=stock_color,
                    anchor="w"
                )
                stock.pack(anchor="w")
        else:
            ok = ctk.CTkLabel(
                box, 
                text="สต็อกสินค้าเพียงพอทั้งหมด ✓", 
                text_color="#4CAF50"
            )
            ok.pack(pady=20)
        
        spacer = ctk.CTkLabel(box, text="")
        spacer.pack(pady=10)
    
    
    # ==================== ตารางคำสั่งซื้อล่าสุด ====================
    def create_orders_table(self, parent):
        """สร้างตารางแสดงคำสั่งซื้อล่าสุด"""
        box = ctk.CTkFrame(parent, fg_color="white", corner_radius=15)
        box.grid(row=3, column=0, columnspan=4, sticky="nsew", pady=20)
        
        title = ctk.CTkLabel(
            box, 
            text="📋 คำสั่งซื้อล่าสุด", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        title.pack(pady=(20, 10), padx=20, anchor="w")
        
        style = ttk.Style()
        style.configure("Dashboard.Treeview", rowheight=35, font=('Arial', 11))
        style.configure("Dashboard.Treeview.Heading", font=('Arial', 12, 'bold'))
        
        columns = ("order_id", "customer", "amount", "status", "date")
        
        table = ttk.Treeview(
            box, 
            columns=columns, 
            show="headings", 
            height=8, 
            style="Dashboard.Treeview"
        )
        
        table.heading("order_id", text="Order ID")
        table.heading("customer", text="ลูกค้า")
        table.heading("amount", text="ยอดเงิน")
        table.heading("status", text="สถานะ")
        table.heading("date", text="วันที่")
        
        table.column("order_id", width=80, anchor="center")
        table.column("customer", width=200)
        table.column("amount", width=120, anchor="e")
        table.column("status", width=120, anchor="center")
        table.column("date", width=150, anchor="center")
        
        table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        
        # (DB ใหม่จะเรียงตาม Order ID DESC)
        recent_orders = self.db.get_recent_orders(10)
        
        status_thai = {
            'pending': 'รอดำเนินการ',
            'confirmed': 'ยืนยันแล้ว',
            'shipped': 'จัดส่งแล้ว',
            'delivered': 'ส่งสำเร็จ',
            'cancelled': 'ยกเลิก'
        }
        
        for order in recent_orders:
            order_id = f"#{order['order_id']}"
            customer = order['full_name']
            amount = f"฿{order['total_amount']:,.2f}"
            status = status_thai.get(order['status'], order['status'])
            
            # --- 🛠️ (แก้ไข) จัดรูปแบบเวลา (ปลอดภัยขึ้น) ---
            date_str = order.get('created_at', '-')
            if date_str and date_str != '-':
                try:
                    # ลองแปลงจาก 'YYYY-MM-DD HH:MM:SS'
                    dt_obj = datetime.strptime(date_str, '%Y-%m-%d %H:%M:%S')
                    date = dt_obj.strftime('%Y-%m-%d %H:%M') # แสดงผลแบบ HH:MM
                except ValueError:
                    date = date_str[:16] # ถ้าพลาด ให้ใช้วิธีตัด
            else:
                date = '-'
            # --- 🛠️ (สิ้นสุดการแก้ไข) ---
            
            table.insert("", "end", values=(order_id, customer, amount, status, date))

    # ==================== ฟังก์ชันใหม่สำหรับปฏิทิน ====================
    
    # --- 🛠️ (แก้ไข) นี่คือจุดที่แก้ Error (วิธีปลอดภัย) ---
    def mark_sales_days_on_calendar(self):
        """
        ดึงข้อมูลยอดขายทั้งหมดและมาร์คสีลงบนปฏิทิน
        (ใช้วิธีที่ปลอดภัยที่สุด)
        """
        if not self.calendar:
            return 

        try:
            # 1. ตั้งค่า tag สีก่อน
            self.calendar.tag_config('sales_day', background='#C8E6C9', foreground='black') 
            
            # 2. ดึงข้อมูล-ยอดขายทั้งหมด (แบบรายวัน)
            sales_data = self.db.get_sales_by_period('day')
            if not sales_data:
                return

            # 3. วนลูปและเพิ่ม event ลงในปฏิทิน
            for day_data in sales_data:
                if day_data['total_revenue'] > 0:
                    sale_date = datetime.strptime(day_data['sales_period'], '%Y-%m-%d').date()
                    
                    # (ลองใช้ .calevents ซึ่งเป็นวิธีของ tkcalendar)
                    self.calendar.calevents[sale_date] = {'text': '', 'tags': ('sales_day',)}

            # 4. สั่งวาดใหม่
            if hasattr(self.calendar, '_update_calendar'):
                self.calendar._update_calendar() 
                self.calendar._display_calendar()

        except Exception as e:
            # (ถ้าล้มเหลว) พิมพ์ Error ใน Terminal แต่ไม่แครช
            print(f"เกิดข้อผิดพลาดในการมาร์คสีปฏิทิน (จะข้ามไป): {e}")
            pass # (สำคัญ!) ปล่อยผ่าน เพื่อให้โค้ดส่วนอื่นทำงานต่อ
    # --- 🛠️ (สิ้นสุดการแก้ไข) ---