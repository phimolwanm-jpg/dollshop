import customtkinter as ctk
from models import Order 

class OrderHistoryWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5")  # สีชมพูอ่อน
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.session = main_app.session 
        self.db = main_app.db
        
        # สร้างหน้าจอ UI ทันที
        self.setup_ui() 

    def on_show(self):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: ลบของเก่า สร้าง UI ใหม่ทั้งหมด
        เพื่อให้รายการคำสั่งซื้อสดใหม่เสมอ
        """
        # ลบ widget เก่าทั้งหมด
        for widget in self.winfo_children():
            widget.destroy()
        # สร้าง UI ใหม่
        self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้าประวัติการสั่งซื้อ"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
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
        
        header_title = ctk.CTkLabel(
            header_frame,
            text="📜 ประวัติการสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        back_button = ctk.CTkButton(
            header_frame,
            text="< กลับไปหน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), 
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        )
        back_button.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (รายการ Order ที่เลื่อนได้) ---
        orders_frame_scrollable = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        orders_frame_scrollable.grid(row=1, column=0, sticky="nsew", padx=30, pady=10) 
        
        # --- 4. ดึงข้อมูลประวัติการสั่งซื้อ ---
        # --- เพิ่มการตรวจสอบตรงนี้ ---
        orders_data_list = [] # เริ่มต้นด้วย list ว่าง
        # เช็คก่อนว่ามี user login อยู่หรือไม่
        if self.session.is_logged_in(): 
            current_user_id = self.session.current_user.user_id 
            # ถ้า login อยู่ ค่อยไปดึงข้อมูล order จาก DB
            orders_data_list = self.db.get_user_orders(current_user_id) 
        # --- สิ้นสุดการตรวจสอบ ---

        # --- 5. ตรวจสอบว่ามีประวัติการสั่งซื้อหรือไม่ ---
        # (โค้ดส่วนนี้จะทำงานได้ถูกต้อง แม้ orders_data_list จะเป็น list ว่าง)
        if not orders_data_list:
            # --- ถ้าไม่มี: แสดงข้อความแจ้ง ---
            empty_frame = ctk.CTkFrame(orders_frame_scrollable, 
                                       fg_color="#FFFFFF", 
                                       corner_radius=20, 
                                       border_width=2, 
                                       border_color="#FFEBEE")
            empty_frame.pack(expand=True, fill="both", padx=10, pady=50) 
            
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📦",
                font=ctk.CTkFont(size=60)
            )
            empty_icon.pack(pady=(40, 20))
            
            empty_text1 = ctk.CTkLabel(
                empty_frame,
                text="คุณยังไม่มีประวัติการสั่งซื้อ",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFB6C1"
            )
            empty_text1.pack(pady=(0, 10))
            
            empty_text2 = ctk.CTkLabel(
                empty_frame,
                text="เริ่มช้อปปิ้งเลยตอนนี้!",
                font=ctk.CTkFont(size=14),
                text_color="gray50"
            )
            empty_text2.pack(pady=(0, 40))
            # --- จบกรณีไม่มีประวัติ ---
        else:
            # --- ถ้ามีประวัติ: วนลูปสร้างการ์ดสำหรับแต่ละ Order ---
            for order_dictionary in orders_data_list: 
                order_object = Order.from_dict(order_dictionary) 
                
                # --- สร้างการ์ดสำหรับ Order นี้ ---
                order_card = ctk.CTkFrame(
                    orders_frame_scrollable, 
                    fg_color="#FFFFFF",
                    corner_radius=20,
                    border_width=2,
                    border_color="#FFEBEE"
                )

                # 2. Header การ์ด
                card_header = ctk.CTkFrame(order_card, fg_color="#FFE4E1", corner_radius=15)
                card_header.pack(fill="x", padx=15, pady=15) 
                
                card_header_content = ctk.CTkFrame(card_header, fg_color="transparent")
                card_header_content.pack(fill="x", padx=15, pady=10)
                
                order_id_label = ctk.CTkLabel(
                    card_header_content,
                    text=f"🛍️ หมายเลขคำสั่งซื้อ #{order_object.order_id}",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#6D4C41"
                )
                order_id_label.pack(side="left")
                
                order_date_label = ctk.CTkLabel(
                    card_header_content,
                    text=f"📅 {order_object.format_date()}", 
                    font=ctk.CTkFont(size=14),
                    text_color="#6D4C41"
                )
                order_date_label.pack(side="right")

                # 3. Body การ์ด
                card_body_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                card_body_frame.pack(fill="x", padx=20, pady=15)
                card_body_frame.grid_columnconfigure(0, weight=3) 
                card_body_frame.grid_columnconfigure(1, weight=1)

                # 3.1 รายการสินค้า (ซ้าย)
                items_display_frame = ctk.CTkFrame(card_body_frame, fg_color="#FFF0F5", corner_radius=10)
                items_display_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15)) 
                
                items_string = order_object.items if order_object.items else "ไม่มีรายการ" 
                items_formatted_text = items_string.replace(",", "\n• ") 
                final_items_text = f"รายการสินค้า:\n• {items_formatted_text}" 
                
                items_label = ctk.CTkLabel(
                    items_display_frame,
                    text=final_items_text,
                    justify="left", anchor="nw", wraplength=500,
                    font=ctk.CTkFont(size=14), text_color="#6D4C41"
                )
                items_label.pack(padx=15, pady=15)

                # 3.2 สรุปยอด/สถานะ (ขวา)
                summary_status_frame = ctk.CTkFrame(card_body_frame, fg_color="transparent")
                summary_status_frame.grid(row=0, column=1, sticky="ne") 
                
                # 3.2.1 ยอดรวม
                total_container = ctk.CTkFrame(summary_status_frame, fg_color="#FFF0F5", corner_radius=10)
                total_container.pack(fill="x", pady=(0, 10)) 
                
                total_text_label = ctk.CTkLabel(
                    total_container, text="ยอดรวม",
                    font=ctk.CTkFont(size=12), text_color="gray50"
                )
                total_text_label.pack(pady=(10, 0))
                
                total_value_label = ctk.CTkLabel(
                    total_container, text=order_object.format_total(), 
                    font=ctk.CTkFont(size=22, weight="bold"), text_color="#FF6B9D"
                )
                total_value_label.pack(pady=(5, 10))

                # 3.2.2 สถานะ (Badge)
                status_badge_frame = ctk.CTkFrame(
                    summary_status_frame,
                    fg_color=order_object.get_status_color(), 
                    corner_radius=10
                )
                status_badge_frame.pack(fill="x") 
                
                status_text_label = ctk.CTkLabel(
                    status_badge_frame, text=order_object.get_status_text(), 
                    font=ctk.CTkFont(size=14, weight="bold"), text_color="white"
                )
                status_text_label.pack(padx=20, pady=10)
                
                # 3.2.3 ปุ่มดูใบเสร็จ
                view_receipt_button = ctk.CTkButton(
                    summary_status_frame, 
                    text="🧾 ดูใบเสร็จ",
                    fg_color="#FFB6C1", hover_color="#FFC0CB",
                    corner_radius=10, height=35,
                    command=lambda oid=order_object.order_id: self.main_app.navigate_to('ReceiptWindow', order_id=oid) 
                )
                view_receipt_button.pack(fill="x", pady=(10, 0)) 
                # --- จบการสร้างการ์ด Order ---
                
                order_card.pack(fill="x", pady=10) 
            # --- จบ Loop สร้างการ์ด ---
        # --- จบกรณีมีประวัติ ---