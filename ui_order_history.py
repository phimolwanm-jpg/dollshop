import customtkinter as ctk
from models import Order

class OrderHistoryWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")
        self.main_app = main_app
        self.session = main_app.session
        self.db = main_app.db
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui()

    def on_show(self):
        # ลบของเก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        
        # สร้าง UI ใหม่
        self.setup_ui()

    def setup_ui(self):
        # ตั้งค่า Grid หลัก
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # สร้างส่วนหัว
        self.create_header()
        
        # สร้างส่วนเนื้อหา
        self.create_content()

    def create_header(self):
        # กรอบส่วนหัว
        header_frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=1,
            border_color="#FFEBEE"
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 20))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # หัวข้อ
        header_title = ctk.CTkLabel(
            header_frame,
            text="📜 ประวัติการสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # ปุ่มกลับ
        back_button = ctk.CTkButton(
            header_frame,
            text="< กลับไปหน้าหลัก",
            command=self.go_to_home,
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        )
        back_button.pack(side="right", padx=30, pady=20)

    def go_to_home(self):
        # ฟังก์ชันกลับหน้าหลัก
        self.main_app.navigate_to('HomeWindow')

    def create_content(self):
        # กรอบที่เลื่อนได้
        orders_frame = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        orders_frame.grid(row=1, column=0, sticky="nsew", padx=30, pady=10)
        
        # ดึงข้อมูล orders
        orders_list = self.get_user_orders()
        
        # ตรวจสอบว่ามีข้อมูลหรือไม่
        if not orders_list:
            self.show_empty_message(orders_frame)
        else:
            self.show_orders_list(orders_frame, orders_list)

    def get_user_orders(self):
        # ดึงข้อมูล orders ของ user
        orders_list = []
        
        # ตรวจสอบว่า login อยู่หรือไม่
        if self.session.is_logged_in():
            user_id = self.session.current_user.user_id
            orders_list = self.db.get_user_orders(user_id)
        
        return orders_list

    def show_empty_message(self, parent_frame):
        # แสดงข้อความเมื่อไม่มี orders
        empty_frame = ctk.CTkFrame(
            parent_frame,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        empty_frame.pack(expand=True, fill="both", padx=10, pady=50)
        
        # ไอคอน
        empty_icon = ctk.CTkLabel(
            empty_frame,
            text="📦",
            font=ctk.CTkFont(size=60)
        )
        empty_icon.pack(pady=(40, 20))
        
        # ข้อความหลัก
        empty_text1 = ctk.CTkLabel(
            empty_frame,
            text="คุณยังไม่มีประวัติการสั่งซื้อ",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color="#FFB6C1"
        )
        empty_text1.pack(pady=(0, 10))
        
        # ข้อความรอง
        empty_text2 = ctk.CTkLabel(
            empty_frame,
            text="เริ่มช้อปปิ้งเลยตอนนี้!",
            font=ctk.CTkFont(size=14),
            text_color="gray50"
        )
        empty_text2.pack(pady=(0, 40))

    def show_orders_list(self, parent_frame, orders_list):
        # แสดงรายการ orders
        for order_dict in orders_list:
            # แปลง dict เป็น Order object
            order = Order.from_dict(order_dict)
            
            # สร้างการ์ดสำหรับ order นี้
            self.create_order_card(parent_frame, order)

    def create_order_card(self, parent_frame, order):
        # กรอบการ์ดหลัก
        order_card = ctk.CTkFrame(
            parent_frame,
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=2,
            border_color="#FFEBEE"
        )
        order_card.pack(fill="x", pady=10)
        
        # สร้างส่วนหัวการ์ด
        self.create_card_header(order_card, order)
        
        # สร้างส่วนเนื้อหาการ์ด
        self.create_card_body(order_card, order)

    def create_card_header(self, card_frame, order):
        # กรอบหัวการ์ด
        card_header = ctk.CTkFrame(
            card_frame,
            fg_color="#FFE4E1",
            corner_radius=15
        )
        card_header.pack(fill="x", padx=15, pady=15)
        
        # กรอบเนื้อหาภายใน
        header_content = ctk.CTkFrame(card_header, fg_color="transparent")
        header_content.pack(fill="x", padx=15, pady=10)
        
        # เลขที่ order (ซ้าย)
        order_id_label = ctk.CTkLabel(
            header_content,
            text=f"🛍️ หมายเลขคำสั่งซื้อ #{order.order_id}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#6D4C41"
        )
        order_id_label.pack(side="left")
        
        # วันที่ (ขวา)
        order_date = order.format_date()
        order_date_label = ctk.CTkLabel(
            header_content,
            text=f"📅 {order_date}",
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        order_date_label.pack(side="right")

    def create_card_body(self, card_frame, order):
        # กรอบเนื้อหาการ์ด
        card_body = ctk.CTkFrame(card_frame, fg_color="transparent")
        card_body.pack(fill="x", padx=20, pady=15)
        
        # ตั้งค่า Grid
        card_body.grid_columnconfigure(0, weight=3)
        card_body.grid_columnconfigure(1, weight=1)
        
        # ส่วนซ้าย: รายการสินค้า
        self.create_items_section(card_body, order)
        
        # ส่วนขวา: สรุปยอดและสถานะ
        self.create_summary_section(card_body, order)

    def create_items_section(self, parent_frame, order):
        # กรอบรายการสินค้า
        items_frame = ctk.CTkFrame(
            parent_frame,
            fg_color="#FFF0F5",
            corner_radius=10
        )
        items_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15))
        
        # จัดรูปแบบรายการสินค้า
        items_text = self.format_items_text(order.items)
        
        # ป้ายแสดงรายการ
        items_label = ctk.CTkLabel(
            items_frame,
            text=items_text,
            justify="left",
            anchor="nw",
            wraplength=500,
            font=ctk.CTkFont(size=14),
            text_color="#6D4C41"
        )
        items_label.pack(padx=15, pady=15)

    def format_items_text(self, items_string):
        # จัดรูปแบบข้อความรายการสินค้า
        if not items_string:
            return "รายการสินค้า:\n• ไม่มีรายการ"
        
        # แทนที่ , ด้วยขึ้นบรรทัดใหม่และเครื่องหมาย bullet
        formatted = items_string.replace(",", "\n• ")
        final_text = f"รายการสินค้า:\n• {formatted}"
        
        return final_text

    def create_summary_section(self, parent_frame, order):
        # กรอบสรุปยอด
        summary_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        summary_frame.grid(row=0, column=1, sticky="ne")
        
        # สร้างกล่องยอดรวม
        self.create_total_box(summary_frame, order)
        
        # สร้างป้ายสถานะ
        self.create_status_badge(summary_frame, order)
        
        # สร้างปุ่มดูใบเสร็จ
        self.create_receipt_button(summary_frame, order)

    def create_total_box(self, parent_frame, order):
        # กล่องยอดรวม
        total_container = ctk.CTkFrame(
            parent_frame,
            fg_color="#FFF0F5",
            corner_radius=10
        )
        total_container.pack(fill="x", pady=(0, 10))
        
        # ข้อความ "ยอดรวม"
        total_text = ctk.CTkLabel(
            total_container,
            text="ยอดรวม",
            font=ctk.CTkFont(size=12),
            text_color="gray50"
        )
        total_text.pack(pady=(10, 0))
        
        # ตัวเลขยอดรวม
        total_amount = order.format_total()
        total_value = ctk.CTkLabel(
            total_container,
            text=total_amount,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#FF6B9D"
        )
        total_value.pack(pady=(5, 10))

    def create_status_badge(self, parent_frame, order):
        # ดึงข้อมูลสถานะ
        status_color = order.get_status_color()
        status_text = order.get_status_text()
        
        # กรอบป้ายสถานะ
        status_badge = ctk.CTkFrame(
            parent_frame,
            fg_color=status_color,
            corner_radius=10
        )
        status_badge.pack(fill="x")
        
        # ข้อความสถานะ
        status_label = ctk.CTkLabel(
            status_badge,
            text=status_text,
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="white"
        )
        status_label.pack(padx=20, pady=10)

    def create_receipt_button(self, parent_frame, order):
        # ปุ่มดูใบเสร็จ
        receipt_button = ctk.CTkButton(
            parent_frame,
            text="🧾 ดูใบเสร็จ",
            fg_color="#FFB6C1",
            hover_color="#FFC0CB",
            corner_radius=10,
            height=35,
            command=lambda: self.view_receipt(order.order_id)
        )
        receipt_button.pack(fill="x", pady=(10, 0))

    def view_receipt(self, order_id):
        # ฟังก์ชันไปหน้าใบเสร็จ
        self.main_app.navigate_to('ReceiptWindow', order_id=order_id)