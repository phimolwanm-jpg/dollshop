import customtkinter as ctk
from tkinter import ttk

class AdminDashboardWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F8F9FA")
        self.main_app = main_app
        self.db = main_app.db
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 
    
    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้ข้อมูลสถิติสดใหม่เสมอ
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
        header = ctk.CTkFrame(self, fg_color="white", corner_radius=0, height=70)
        # วาง header แถวบนสุด (row=0) ยืดเต็มความกว้าง (sticky="ew")
        header.grid(row=0, column=0, sticky="ew") 
        # ให้คอลัมน์ 1 ใน header ขยาย (ดันปุ่มไปขวา)
        header.grid_columnconfigure(1, weight=1) 
        
        # Label ชื่อหน้า
        header_title = ctk.CTkLabel(
            header, 
            text="📊 Admin Dashboard", 
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#2E7D32" # สีเขียว
        )
        header_title.pack(side="left", padx=30)
        
        # Frame สำหรับวางปุ่มทางขวา
        header_btn_frame = ctk.CTkFrame(header, fg_color="transparent")
        header_btn_frame.pack(side="right", padx=20)
        
        # ปุ่ม "หน้าหลัก"
        home_btn = ctk.CTkButton(
            header_btn_frame,
            text="🏠 หน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), # กดแล้วไปหน้า Home
            fg_color="transparent",
            text_color="gray50",
            hover_color="#F5F5F5"
        )
        home_btn.pack(side="left", padx=5)
        
        # ปุ่ม "จัดการสินค้า"
        product_btn = ctk.CTkButton(
            header_btn_frame,
            text="⚙️ จัดการสินค้า",
            command=lambda: self.main_app.navigate_to('AdminWindow'), # กดแล้วไปหน้า AdminWindow
            fg_color="#FF6B9D", # สีชมพู
            hover_color="#FF8FB3"
        )
        product_btn.pack(side="left", padx=5)
        
        # ปุ่ม "จัดการคำสั่งซื้อ"
        orders_btn = ctk.CTkButton(
            header_btn_frame,
            text="📦 จัดการคำสั่งซื้อ",
            command=lambda: self.main_app.navigate_to('AdminOrdersWindow'), # กดแล้วไปหน้า AdminOrdersWindow
            fg_color="#2196F3", # สีฟ้า
            hover_color="#42A5F5"
        )
        orders_btn.pack(side="left", padx=5)
        
        # ปุ่ม "ประวัติการขาย"
        sales_btn = ctk.CTkButton(
            header_btn_frame,
            text="📊 ประวัติการขาย",
            command=lambda: self.main_app.navigate_to('SalesHistoryWindow'), # กดแล้วไปหน้า SalesHistoryWindow
            fg_color="#9C27B0", # สีม่วง
            hover_color="#BA68C8"
        )
        sales_btn.pack(side="left", padx=5)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (เลื่อนได้) ---
        main_frame = ctk.CTkScrollableFrame(self, fg_color="transparent")
        # วาง main_frame ในแถว 1 (ใต้ header) ยืดเต็มพื้นที่ (sticky="nsew")
        main_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        # แบ่ง main_frame เป็น 4 คอลัมน์เท่าๆ กัน สำหรับวางการ์ดสถิติ
        main_frame.grid_columnconfigure((0, 1, 2, 3), weight=1) 

        # --- 4. สร้างการ์ดสถิติ ---
        # (ย้ายโค้ดจาก create_stats_cards มาไว้ตรงนี้)
        
        # 4.1 ดึงข้อมูลสถิติจาก DB
        stats = self.db.get_dashboard_stats()
        
        # 4.2 เตรียมข้อมูลสำหรับการ์ดแต่ละใบ
        cards_data = [
            {
                'title': 'ยอดขายรวม',
                'value': f"{stats['total_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'icon': '🛒',
                'color': '#4CAF50' # สีเขียว
            },
            {
                'title': 'รายได้ทั้งหมด',
                'value': f"฿{stats['total_revenue']:,.2f}",
                'subtitle': 'บาท',
                'icon': '💰',
                'color': '#2196F3' # สีฟ้า
            },
            {
                'title': 'สินค้าทั้งหมด',
                'value': f"{stats['total_products']}",
                'subtitle': 'รายการ',
                'icon': '📦',
                'color': '#FF9800' # สีส้ม
            },
            {
                'title': 'รอดำเนินการ',
                'value': f"{stats['pending_orders']}",
                'subtitle': 'คำสั่งซื้อ',
                'icon': '⏳',
                'color': '#F44336' # สีแดง
            }
        ]
        
        # 4.3 วนลูปสร้างการ์ดแต่ละใบ
        for i, card_data_item in enumerate(cards_data):
            # --- สร้างการ์ด 1 ใบ (โค้ดจาก create_stat_card เดิม) ---
            # (ย้ายโค้ดสร้างการ์ดมาไว้ใน loop นี้)
            card = ctk.CTkFrame(main_frame, # ใส่การ์ดลงใน main_frame
                                fg_color="white", 
                                corner_radius=15, 
                                border_width=1, 
                                border_color="#E0E0E0")
            card.grid_columnconfigure(0, weight=1) # ให้เนื้อหาอยู่กลางการ์ด
            
            # Icon (Emoji)
            icon_label = ctk.CTkLabel(
                card, 
                text=card_data_item['icon'], 
                font=ctk.CTkFont(size=40)
            )
            icon_label.grid(row=0, column=0, pady=(20, 10))
            
            # Title (เช่น 'ยอดขายรวม')
            title_label = ctk.CTkLabel(
                card, 
                text=card_data_item['title'], 
                font=ctk.CTkFont(size=14),
                text_color="gray50"
            )
            title_label.grid(row=1, column=0, pady=5)
            
            # Value (ตัวเลขสถิติ)
            value_label = ctk.CTkLabel(
                card, 
                text=card_data_item['value'], 
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color=card_data_item['color'] # ใช้สีตามที่กำหนด
            )
            value_label.grid(row=2, column=0, pady=5)
            
            # Subtitle (เช่น 'คำสั่งซื้อ')
            subtitle_label = ctk.CTkLabel(
                card, 
                text=card_data_item['subtitle'], 
                font=ctk.CTkFont(size=12),
                text_color="gray40"
            )
            subtitle_label.grid(row=3, column=0, pady=(5, 20))
            # --- จบการสร้างการ์ด 1 ใบ ---
            
            # วางการ์ดลงใน main_frame ตามคอลัมน์ i (0, 1, 2, 3)
            card.grid(row=0, column=i, padx=10, pady=10, sticky="nsew") 
        # --- จบส่วนสร้างการ์ดสถิติ ---

        # --- 5. สร้าง Frame สำหรับวางส่วน Top Selling และ Low Stock ข้างกัน ---
        chart_frame = ctk.CTkFrame(main_frame, fg_color="transparent")
        # วาง chart_frame ในแถว 1 (ใต้การ์ด) ให้กินพื้นที่ทั้ง 4 คอลัมน์
        chart_frame.grid(row=1, column=0, columnspan=4, sticky="ew", pady=20) 
        # แบ่ง chart_frame เป็น 2 คอลัมน์เท่าๆ กัน
        chart_frame.grid_columnconfigure((0, 1), weight=1) 

        # --- 6. สร้างส่วน "สินค้าขายดี" ---
        # (ย้ายโค้ดจาก create_top_products_section มาไว้ตรงนี้)
        top_product_section = ctk.CTkFrame(chart_frame, # ใส่ใน chart_frame คอลัมน์ 0
                                           fg_color="white", corner_radius=15)
        top_product_section.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)
        
        top_product_title = ctk.CTkLabel(
            top_product_section, 
            text="🏆 สินค้าขายดี Top 5", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        top_product_title.pack(pady=(20, 10), padx=20, anchor="w") # anchor="w" คือชิดซ้าย
        
        # ดึงข้อมูลสินค้าขายดีจาก DB
        top_products_list = self.db.get_top_selling_products(5)
        
        # เช็คว่ามีข้อมูลหรือไม่
        if top_products_list:
            # วนลูปสร้างรายการสินค้าขายดี
            for i, product_item in enumerate(top_products_list, 1): # เริ่มนับ i จาก 1
                item_frame = ctk.CTkFrame(top_product_section, fg_color="#F5F5F5", corner_radius=10)
                item_frame.pack(fill="x", padx=20, pady=5)
                
                # ลำดับ (#1, #2, ...)
                rank_label = ctk.CTkLabel(
                    item_frame, 
                    text=f"#{i}", 
                    font=ctk.CTkFont(size=16, weight="bold"),
                    text_color="#FF6B9D",
                    width=40
                )
                rank_label.pack(side="left", padx=10, pady=10)
                
                # Frame สำหรับชื่อและรายละเอียด
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=10)
                
                # ชื่อสินค้า
                name_label = ctk.CTkLabel(
                    info_frame, 
                    text=product_item['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name_label.pack(anchor="w")
                
                # รายละเอียด (ขายได้กี่ชิ้น / รายได้)
                details_label = ctk.CTkLabel(
                    info_frame, 
                    text=f"ขายได้: {product_item['total_sold']} ชิ้น | รายได้: ฿{product_item['total_revenue']:,.2f}", 
                    font=ctk.CTkFont(size=12),
                    text_color="gray50",
                    anchor="w"
                )
                details_label.pack(anchor="w")
        else:
            # ถ้าไม่มีข้อมูล
            no_data_label = ctk.CTkLabel(
                top_product_section, 
                text="ยังไม่มีข้อมูลการขาย", 
                text_color="gray50"
            )
            no_data_label.pack(pady=20)
        
        # Spacer เว้นวรรคด้านล่าง
        spacer1 = ctk.CTkLabel(top_product_section, text="")
        spacer1.pack(pady=10)
        # --- จบส่วนสินค้าขายดี ---
        
        # --- 7. สร้างส่วน "สินค้าสต็อกต่ำ" ---
        # (ย้ายโค้ดจาก create_low_stock_section มาไว้ตรงนี้)
        low_stock_section = ctk.CTkFrame(chart_frame, # ใส่ใน chart_frame คอลัมน์ 1
                                         fg_color="white", corner_radius=15)
        low_stock_section.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)
        
        low_stock_title = ctk.CTkLabel(
            low_stock_section, 
            text="⚠️ สินค้าสต็อกต่ำ", 
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#F44336" # สีแดง
        )
        low_stock_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # ดึงข้อมูลสินค้าสต็อกต่ำ (น้อยกว่า 10 ชิ้น) จาก DB
        low_stock_list = self.db.get_low_stock_products(10)
        
        # เช็คว่ามีข้อมูลหรือไม่
        if low_stock_list:
            # วนลูปแสดงผล (เอาแค่ 5 รายการแรก)
            for product_item in low_stock_list[:5]: 
                item_frame = ctk.CTkFrame(low_stock_section, fg_color="#FFEBEE", corner_radius=10) # พื้นหลังสีชมพูอ่อน
                item_frame.pack(fill="x", padx=20, pady=5)
                
                # Frame สำหรับชื่อและจำนวน
                info_frame = ctk.CTkFrame(item_frame, fg_color="transparent")
                info_frame.pack(side="left", fill="x", expand=True, padx=15, pady=10)
                
                # ชื่อสินค้า
                name_label = ctk.CTkLabel(
                    info_frame, 
                    text=product_item['name'], 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    anchor="w"
                )
                name_label.pack(anchor="w")
                
                # กำหนดสีตามจำนวนสต็อก
                stock_amount = product_item['stock']
                if stock_amount < 5:
                    stock_color = "#F44336" # สีแดง (น้อยกว่า 5)
                else:
                    stock_color = "#FF9800" # สีส้ม (5-9)
                    
                # จำนวนที่เหลือ
                stock_label = ctk.CTkLabel(
                    info_frame, 
                    text=f"เหลือ: {stock_amount} ชิ้น", 
                    font=ctk.CTkFont(size=12),
                    text_color=stock_color, # ใช้สีที่คำนวณไว้
                    anchor="w"
                )
                stock_label.pack(anchor="w")
        else:
            # ถ้าไม่มีสินค้าสต็อกต่ำ
            all_ok_label = ctk.CTkLabel(
                low_stock_section, 
                text="สต็อกสินค้าเพียงพอทั้งหมด ✓", 
                text_color="#4CAF50" # สีเขียว
            )
            all_ok_label.pack(pady=20)
        
        # Spacer เว้นวรรคด้านล่าง
        spacer2 = ctk.CTkLabel(low_stock_section, text="")
        spacer2.pack(pady=10)
        # --- จบส่วนสินค้าสต็อกต่ำ ---

        # --- 8. สร้างส่วน "คำสั่งซื้อล่าสุด" ---
        # (ย้ายโค้ดจาก create_recent_orders_section มาไว้ตรงนี้)
        recent_orders_section = ctk.CTkFrame(main_frame, # ใส่ใน main_frame (แถว 2 ใต้ chart_frame)
                                             fg_color="white", corner_radius=15)
        # columnspan=4 ให้กินพื้นที่ทั้ง 4 คอลัมน์
        recent_orders_section.grid(row=2, column=0, columnspan=4, sticky="nsew", pady=20) 
        
        recent_orders_title = ctk.CTkLabel(
            recent_orders_section, 
            text="📋 คำสั่งซื้อล่าสุด", 
            font=ctk.CTkFont(size=18, weight="bold")
        )
        recent_orders_title.pack(pady=(20, 10), padx=20, anchor="w")
        
        # --- สร้างตาราง Treeview ---
        style = ttk.Style()
        style.configure("Dashboard.Treeview", rowheight=35, font=('Arial', 11))
        style.configure("Dashboard.Treeview.Heading", font=('Arial', 12, 'bold'))
        
        columns = ("order_id", "customer", "amount", "status", "date")
        # สร้าง Treeview ใส่ใน recent_orders_section
        orders_tree = ttk.Treeview(recent_orders_section, 
                                   columns=columns, 
                                   show="headings", # ไม่แสดงคอลัมน์ #0
                                   height=8, # จำกัดความสูง 8 แถว
                                   style="Dashboard.Treeview")
        
        # ตั้งชื่อหัวตาราง
        orders_tree.heading("order_id", text="Order ID")
        orders_tree.heading("customer", text="ลูกค้า")
        orders_tree.heading("amount", text="ยอดเงิน")
        orders_tree.heading("status", text="สถานะ")
        orders_tree.heading("date", text="วันที่")
        
        # ตั้งค่าความกว้างและ alignment
        orders_tree.column("order_id", width=80, anchor="center")
        orders_tree.column("customer", width=200, anchor="w")
        orders_tree.column("amount", width=120, anchor="e")
        orders_tree.column("status", width=120, anchor="center")
        orders_tree.column("date", width=150, anchor="center")
        
        # วางตาราง (ต้องใช้ pack เพราะอยู่ใน section ที่ใช้ pack)
        orders_tree.pack(fill="both", expand=True, padx=20, pady=(0, 20)) 
        
        # ดึงข้อมูล 10 คำสั่งซื้อล่าสุดจาก DB
        recent_orders_list = self.db.get_recent_orders(10)
        
        # เตรียมข้อความสถานะภาษาไทย
        status_text_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 จัดส่งแล้ว',
            'delivered': '✔️ ส่งสำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        # วนลูปเพิ่มข้อมูลลงตาราง
        for order_item in recent_orders_list:
            # แปลงสถานะเป็นภาษาไทย (ถ้าไม่มี ให้ใช้ค่าเดิม)
            status_display = status_text_map.get(order_item['status'], order_item['status'])
            
            # ตัดเวลาวินาทีออก
            order_date = order_item['created_at']
            if order_date:
                order_date = order_date[:16] # เอาแค่ YYYY-MM-DD HH:MM
            else:
                order_date = '-'
                
            orders_tree.insert("", "end", values=(
                f"#{order_item['order_id']}",
                order_item['full_name'], # ใช้ full_name จาก DB
                f"฿{order_item['total_amount']:,.2f}", # จัดรูปแบบยอดเงิน
                status_display, # สถานะภาษาไทย
                order_date # วันที่ที่ตัดแล้ว
            ))
        # --- จบส่วนคำสั่งซื้อล่าสุด ---