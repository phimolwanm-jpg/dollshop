import customtkinter as ctk
# Order object is still needed to structure the data for display
from models import Order 
# Session and Database are accessed via main_app, direct import not strictly needed for UI

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
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (orders_frame_scrollable) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        # (ย้ายโค้ดจาก create_header มาไว้ตรงนี้)
        header_frame = ctk.CTkFrame(
            self, # ใส่ header ลงใน OrderHistoryWindow (self)
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
            text="📜 ประวัติการสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # ปุ่ม "< กลับไปหน้าหลัก"
        back_button = ctk.CTkButton(
            header_frame,
            text="< กลับไปหน้าหลัก",
            command=lambda: self.main_app.navigate_to('HomeWindow'), # กดแล้วกลับหน้า Home
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            font=ctk.CTkFont(size=14)
        )
        back_button.pack(side="right", padx=30, pady=20)
        # --- จบส่วน Header ---

        # --- 3. สร้าง Frame หลักสำหรับเนื้อหา (รายการ Order ที่เลื่อนได้) ---
        orders_frame_scrollable = ctk.CTkScrollableFrame(
            self, # ใส่ใน OrderHistoryWindow (self)
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        # วางในแถว 1 (ใต้ header) ยืดเต็มพื้นที่ (sticky="nsew")
        orders_frame_scrollable.grid(row=1, column=0, sticky="nsew", padx=30, pady=10) 
        
        # --- 4. ดึงข้อมูลประวัติการสั่งซื้อ ---
        # 4.1 เอา user_id ของคนที่ login อยู่
        current_user_id = self.session.current_user.user_id 
        # 4.2 ไปดึงข้อมูล order ทั้งหมดของ user นี้จาก DB
        orders_data_list = self.db.get_user_orders(current_user_id) 

        # --- 5. ตรวจสอบว่ามีประวัติการสั่งซื้อหรือไม่ ---
        if not orders_data_list:
            # --- ถ้าไม่มี: แสดงข้อความแจ้ง ---
            empty_frame = ctk.CTkFrame(orders_frame_scrollable, # ใส่ใน frame ที่เลื่อนได้
                                       fg_color="#FFFFFF", 
                                       corner_radius=20, 
                                       border_width=2, 
                                       border_color="#FFEBEE")
            # expand=True, fill="both" ให้ frame นี้ขยายเต็มพื้นที่ scrollable frame
            empty_frame.pack(expand=True, fill="both", padx=10, pady=50) 
            
            # ใส่ Emoji กล่อง
            empty_icon = ctk.CTkLabel(
                empty_frame,
                text="📦",
                font=ctk.CTkFont(size=60)
            )
            empty_icon.pack(pady=(40, 20))
            
            # ใส่ข้อความหลัก
            empty_text1 = ctk.CTkLabel(
                empty_frame,
                text="คุณยังไม่มีประวัติการสั่งซื้อ",
                font=ctk.CTkFont(size=20, weight="bold"),
                text_color="#FFB6C1"
            )
            empty_text1.pack(pady=(0, 10))
            
            # ใส่ข้อความรอง
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
            for order_dictionary in orders_data_list: # order_dictionary เป็น dict จาก DB
                # แปลง dict เป็น Order object (เพื่อให้เรียกใช้ง่ายขึ้น)
                order_object = Order.from_dict(order_dictionary) 
                
                # --- สร้างการ์ดสำหรับ Order นี้ (โค้ดจาก create_order_card เดิม) ---
                # (ย้ายโค้ดสร้างการ์ดมาไว้ใน loop นี้)
                
                # 1. สร้าง Frame หลักของการ์ด
                order_card = ctk.CTkFrame(
                    orders_frame_scrollable, # ใส่การ์ดลงใน frame ที่เลื่อนได้
                    fg_color="#FFFFFF",
                    corner_radius=20,
                    border_width=2,
                    border_color="#FFEBEE"
                )

                # 2. สร้าง Header ของการ์ด (สีชมพูอ่อน)
                card_header = ctk.CTkFrame(order_card, fg_color="#FFE4E1", corner_radius=15)
                card_header.pack(fill="x", padx=15, pady=15) # fill="x" ให้ยืดเต็มความกว้าง
                
                # Frame ภายใน Header เพื่อจัดวาง Label ซ้าย/ขวา
                card_header_content = ctk.CTkFrame(card_header, fg_color="transparent")
                card_header_content.pack(fill="x", padx=15, pady=10)
                
                # Label หมายเลข Order (ชิดซ้าย)
                order_id_label = ctk.CTkLabel(
                    card_header_content,
                    text=f"🛍️ หมายเลขคำสั่งซื้อ #{order_object.order_id}",
                    font=ctk.CTkFont(size=18, weight="bold"),
                    text_color="#6D4C41"
                )
                order_id_label.pack(side="left")
                
                # Label วันที่ (ชิดขวา)
                order_date_label = ctk.CTkLabel(
                    card_header_content,
                    # ใช้ format_date() จาก Order object
                    text=f"📅 {order_object.format_date()}", 
                    font=ctk.CTkFont(size=14),
                    text_color="#6D4C41"
                )
                order_date_label.pack(side="right")

                # 3. สร้าง Body ของการ์ด (Frame ใส)
                card_body_frame = ctk.CTkFrame(order_card, fg_color="transparent")
                card_body_frame.pack(fill="x", padx=20, pady=15)
                # แบ่ง Body เป็น 2 คอลัมน์: คอลัมน์ 0 กว้าง 3 ส่วน (รายการ), คอลัมน์ 1 กว้าง 1 ส่วน (สรุป)
                card_body_frame.grid_columnconfigure(0, weight=3) 
                card_body_frame.grid_columnconfigure(1, weight=1)

                # --- 3.1 ส่วนแสดงรายการสินค้า (คอลัมน์ 0) ---
                items_display_frame = ctk.CTkFrame(card_body_frame, fg_color="#FFF0F5", corner_radius=10)
                # วางในแถว 0, คอลัมน์ 0, ยืดเต็มพื้นที่แนวตั้งแนวนอน (sticky="nsew")
                items_display_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 15)) 
                
                # เตรียมข้อความรายการสินค้า (จาก order_object.items ที่เป็น string)
                # ถ้า order_object.items เป็น None หรือ "" ให้ใช้ "ไม่มีรายการ"
                items_string = order_object.items if order_object.items else "ไม่มีรายการ" 
                # แทนที่ ", " ด้วย "\n• " เพื่อให้เป็น bullet list
                items_formatted_text = items_string.replace(",", "\n• ") 
                # เพิ่มหัวข้อและ bullet แรก
                final_items_text = f"รายการสินค้า:\n• {items_formatted_text}" 
                
                # Label แสดงรายการสินค้า
                items_label = ctk.CTkLabel(
                    items_display_frame,
                    text=final_items_text,
                    justify="left", # จัดชิดซ้าย
                    anchor="nw",    # ให้ข้อความเริ่มที่มุมบนซ้าย (North-West)
                    wraplength=500, # กว้างสุด 500 ก่อนขึ้นบรรทัดใหม่
                    font=ctk.CTkFont(size=14),
                    text_color="#6D4C41"
                )
                items_label.pack(padx=15, pady=15)

                # --- 3.2 ส่วนแสดงยอดรวมและสถานะ (คอลัมน์ 1) ---
                summary_status_frame = ctk.CTkFrame(card_body_frame, fg_color="transparent")
                # วางในแถว 0, คอลัมน์ 1, ชิดมุมบนขวา (sticky="ne" North-East)
                summary_status_frame.grid(row=0, column=1, sticky="ne") 
                
                # --- 3.2.1 Frame แสดงยอดรวม ---
                total_container = ctk.CTkFrame(summary_status_frame, fg_color="#FFF0F5", corner_radius=10)
                total_container.pack(fill="x", pady=(0, 10)) # fill="x" ให้กว้างเท่า summary_frame
                
                # Label "ยอดรวม" (ตัวเล็ก)
                total_text_label = ctk.CTkLabel(
                    total_container,
                    text="ยอดรวม",
                    font=ctk.CTkFont(size=12),
                    text_color="gray50"
                )
                total_text_label.pack(pady=(10, 0))
                
                # Label แสดงยอดรวม (ตัวใหญ่)
                total_value_label = ctk.CTkLabel(
                    total_container,
                    # ใช้ format_total() จาก Order object
                    text=order_object.format_total(), 
                    font=ctk.CTkFont(size=22, weight="bold"),
                    text_color="#FF6B9D"
                )
                total_value_label.pack(pady=(5, 10))

                # --- 3.2.2 Frame แสดงสถานะ (Badge) ---
                status_badge_frame = ctk.CTkFrame(
                    summary_status_frame,
                    # ใช้ get_status_color() จาก Order object กำหนดสีพื้นหลัง
                    fg_color=order_object.get_status_color(), 
                    corner_radius=10
                )
                status_badge_frame.pack(fill="x") # fill="x" ให้กว้างเท่า summary_frame
                
                # Label แสดงข้อความสถานะ (สีขาว)
                status_text_label = ctk.CTkLabel(
                    status_badge_frame,
                    # ใช้ get_status_text() จาก Order object แปลสถานะ
                    text=order_object.get_status_text(), 
                    font=ctk.CTkFont(size=14, weight="bold"),
                    text_color="white"
                )
                status_text_label.pack(padx=20, pady=10)
                
                # --- 3.2.3 ปุ่ม "ดูใบเสร็จ" ---
                view_receipt_button = ctk.CTkButton(
                    summary_status_frame, # ใส่ใน frame เดียวกับยอดรวม/สถานะ
                    text="🧾 ดูใบเสร็จ",
                    fg_color="#FFB6C1", # สีชมพู
                    hover_color="#FFC0CB",
                    corner_radius=10,
                    height=35,
                    # เมื่อกด ให้ไปหน้า ReceiptWindow พร้อมส่ง order_id ไปด้วย
                    # ใช้ lambda capture (oid=order_object.order_id)
                    command=lambda oid=order_object.order_id: self.main_app.navigate_to('ReceiptWindow', order_id=oid) 
                )
                # วางปุ่มใต้ Status Badge
                view_receipt_button.pack(fill="x", pady=(10, 0)) 
                # --- จบส่วนสร้างการ์ดสำหรับ Order นี้ ---
                
                # วางการ์ดที่สร้างเสร็จ ลงใน frame ที่เลื่อนได้
                order_card.pack(fill="x", pady=10) 
            # --- จบ Loop สร้างการ์ด ---
        # --- จบกรณีมีประวัติ ---

    # --- (ลบฟังก์ชัน create_header และ create_order_card เพราะย้ายโค้ดไปแล้ว) ---