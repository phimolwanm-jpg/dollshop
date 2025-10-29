import customtkinter as ctk
from tkinter import messagebox
# datetime is not directly used here anymore as formatting is done in models or DB
# from datetime import datetime 

class ReceiptWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5") # สีชมพูอ่อน
        self.main_app = main_app
        # ดึง object ที่จำเป็นจาก main_app
        self.db = main_app.db 
        # self.session = main_app.session # session ไม่ได้ใช้ในหน้านี้
        self.order_id_to_show = None # เปลี่ยนชื่อตัวแปรให้ชัดเจน
        
        # ไม่ต้องสร้าง UI ทันที รอ on_show เรียก
        # self.setup_ui() 
        
    def on_show(self, order_id=None):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: รับ order_id, ลบ UI เก่า, สร้าง UI ใหม่
        """
        # 1. เก็บ order_id ที่ได้รับมา
        self.order_id_to_show = order_id 
        
        # 2. ลบ widget เก่าทั้งหมดทิ้ง
        for widget in self.winfo_children():
            widget.destroy()
        
        # 3. ตรวจสอบว่าได้รับ order_id มาหรือไม่
        if not self.order_id_to_show:
            # --- ถ้าไม่ได้รับ: แสดงหน้า Error ---
            error_label = ctk.CTkLabel(
                self, # ใส่ใน ReceiptWindow (self)
                text="❌ ไม่พบข้อมูลคำสั่งซื้อ",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#F44336" # สีแดง
            )
            # expand=True ให้ label อยู่กลางจอ
            error_label.pack(expand=True) 
            
            error_back_button = ctk.CTkButton(
                self,
                text="กลับไปหน้าหลัก",
                command=lambda: self.main_app.navigate_to('HomeWindow'), # กดแล้วกลับ Home
                fg_color="#FFB6C1", # สีชมพู
                hover_color="#FFC0CB"
            )
            error_back_button.pack(pady=20)
            # --- จบหน้า Error ---
        else:
            # --- ถ้าได้รับ order_id: สร้างหน้า UI ใบเสร็จ ---
            self.setup_ui() 

    # --- (ลบฟังก์ชัน show_error เพราะรวมไว้ใน on_show แล้ว) ---
    
    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้าใบเสร็จ"""
        # --- 1. กำหนดการขยายตัวของ Grid หลัก ---
        # ให้คอลัมน์ 0 (คอลัมน์เดียว) ขยายเต็มความกว้าง
        self.grid_columnconfigure(0, weight=1) 
        # ให้แถวที่ 1 (receipt_container_scrollable) ขยายเต็มความสูง
        self.grid_rowconfigure(1, weight=1)    

        # --- 2. สร้างส่วนหัว (Header) ---
        # (ย้ายโค้ดจาก create_header มาไว้ตรงนี้)
        header_frame = ctk.CTkFrame(
            self, # ใส่ header ใน ReceiptWindow (self)
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
            text="🧾 ใบเสร็จการสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # Frame สำหรับวางปุ่มทางขวา
        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.pack(side="right", padx=20)
        
        # ปุ่ม "พิมพ์" (ยังกดไม่ได้จริง)
        print_button = ctk.CTkButton(
            header_buttons_frame,
            text="🖨️ พิมพ์",
            fg_color="#4CAF50", # สีเขียว
            hover_color="#66BB6A",
            command=self.print_receipt # กดแล้วเรียกฟังก์ชัน print_receipt
        )
        print_button.pack(side="left", padx=5)
        
        # ปุ่ม "หน้าหลัก"
        home_button = ctk.CTkButton(
            header_buttons_frame,
            text="🏠 หน้าหลัก",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            command=lambda: self.main_app.navigate_to('HomeWindow') # กดแล้วกลับ Home
        )
        home_button.pack(side="left", padx=5)
        # --- จบส่วน Header ---
        
        # --- 3. สร้าง Frame หลักสำหรับเนื้อหาใบเสร็จ (เลื่อนได้) ---
        receipt_container_scrollable = ctk.CTkScrollableFrame(
            self, # ใส่ใน ReceiptWindow (self)
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        # วางในแถว 1 (ใต้ header) ยืดเต็มพื้นที่ (sticky="nsew")
        receipt_container_scrollable.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        
        # --- 4. สร้างการ์ดสีขาว (เหมือนกระดาษใบเสร็จ) ---
        receipt_card = ctk.CTkFrame(
            receipt_container_scrollable, # ใส่การ์ดลงใน frame ที่เลื่อนได้
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=3,
            border_color="#FFB6C1" # ขอบสีชมพูเข้มขึ้น
        )
        # ให้การ์ดขยายเต็ม frame ที่เลื่อนได้
        receipt_card.pack(fill="both", expand=True, padx=50, pady=20) 
        
        # --- 5. สร้างเนื้อหาใบเสร็จ (ย้ายโค้ดจาก create_receipt_content) ---
        
        # --- 5.1 โหลดข้อมูล Order จาก DB ---
        # ใช้ self.order_id_to_show ที่ได้จาก on_show
        order_details_dict = self.db.get_order_details(self.order_id_to_show) 
        
        # --- 5.2 ตรวจสอบว่าเจอข้อมูลหรือไม่ ---
        if not order_details_dict:
            # ถ้าไม่เจอ (อาจเกิด error หรือ ID ผิด) ให้แสดงข้อความในการ์ด
            error_label_inside_card = ctk.CTkLabel(
                receipt_card, # ใส่ใน receipt_card
                text="ไม่พบข้อมูลคำสั่งซื้อ",
                text_color="#F44336" # สีแดง
            )
            error_label_inside_card.pack(pady=50)
            # --- จบการทำงาน ถ้าไม่เจอข้อมูล ---
        else:
            # --- ถ้าเจอข้อมูล: สร้างส่วนต่างๆ ของใบเสร็จ ---
            
            # --- 5.3 ส่วน Logo และชื่อร้าน ---
            shop_logo_frame = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=15)
            shop_logo_frame.pack(fill="x", padx=30, pady=(30, 20)) # fill="x" ยืดเต็มกว้าง
            
            shop_icon_label = ctk.CTkLabel(shop_logo_frame, text="🎀", font=ctk.CTkFont(size=60))
            shop_icon_label.pack(pady=(20, 10))
            
            shop_name_label = ctk.CTkLabel(shop_logo_frame, text="Dollie Shop", 
                                          font=ctk.CTkFont(size=32, weight="bold"), 
                                          text_color="#FF6B9D")
            shop_name_label.pack()
            
            shop_subtitle_label = ctk.CTkLabel(shop_logo_frame, text="ร้านขายตุ๊กตาน่ารัก", 
                                             font=ctk.CTkFont(size=14), 
                                             text_color="#6D4C41")
            shop_subtitle_label.pack(pady=(0, 20))
            
            # --- 5.4 ส่วน Title "ใบเสร็จรับเงิน" ---
            receipt_title_frame = ctk.CTkFrame(receipt_card, fg_color="transparent")
            receipt_title_frame.pack(fill="x", padx=30, pady=20)
            
            receipt_title_label = ctk.CTkLabel(receipt_title_frame, text="ใบเสร็จรับเงิน / RECEIPT", 
                                            font=ctk.CTkFont(size=24, weight="bold"), 
                                            text_color="#6D4C41")
            receipt_title_label.pack()
            
            # --- 5.5 ส่วนข้อมูล Order (เลขที่, วันที่, ลูกค้า, สถานะ, ...) ---
            order_info_frame = ctk.CTkFrame(receipt_card, fg_color="#FFF0F5", corner_radius=15)
            order_info_frame.pack(fill="x", padx=30, pady=20)
            # แบ่งเป็น 2 คอลัมน์เท่าๆ กัน
            order_info_frame.grid_columnconfigure((0, 1), weight=1) 
            
            # --- 5.5.1 คอลัมน์ซ้าย ---
            left_info_container = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            # วางในแถว 0, คอลัมน์ 0, ชิดซ้าย (sticky="w")
            left_info_container.grid(row=0, column=0, sticky="w", padx=20, pady=20) 
            
            # --- เพิ่มแถวข้อมูล (เขียนตรงๆ แทน add_info_row) ---
            # แถว 0: เลขที่ใบเสร็จ
            label_order_id = ctk.CTkLabel(left_info_container, text="เลขที่ใบเสร็จ:", 
                                         font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_order_id.grid(row=0, column=0, sticky="w", pady=3)
            value_order_id = ctk.CTkLabel(left_info_container, text=f"#{order_details_dict['order_id']}", 
                                         font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_order_id.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # แถว 1: วันที่
            order_date_str = order_details_dict.get('created_at', '-') # ดึงวันที่ (ถ้ามี)
            if order_date_str and len(order_date_str) > 16:
                order_date_str = order_date_str[:16] # ตัดวินาที
                
            label_date = ctk.CTkLabel(left_info_container, text="วันที่:", 
                                      font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_date.grid(row=1, column=0, sticky="w", pady=3)
            value_date = ctk.CTkLabel(left_info_container, text=order_date_str, 
                                      font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_date.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # แถว 2: ลูกค้า
            label_customer = ctk.CTkLabel(left_info_container, text="ลูกค้า:", 
                                          font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_customer.grid(row=2, column=0, sticky="w", pady=3)
            value_customer = ctk.CTkLabel(left_info_container, text=order_details_dict.get('full_name', '-'), 
                                          font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_customer.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # --- 5.5.2 คอลัมน์ขวา ---
            right_info_container = ctk.CTkFrame(order_info_frame, fg_color="transparent")
             # วางในแถว 0, คอลัมน์ 1, ชิดซ้าย (sticky="w")
            right_info_container.grid(row=0, column=1, sticky="w", padx=20, pady=20) 
            
            # --- เตรียมข้อมูลสถานะ (Text & Color) ---
            order_status = order_details_dict.get('status', 'unknown')
            status_text_map = {
                'pending': '⏳ รอดำเนินการ',
                'confirmed': '✅ ยืนยันแล้ว',
                'shipped': '🚚 กำลังจัดส่ง',
                'delivered': '✔️ จัดส่งสำเร็จ',
                'cancelled': '❌ ยกเลิก'
            }
            status_display_text = status_text_map.get(order_status, order_status) # ถ้าไม่เจอ ให้ใช้ค่าเดิม
            
            # แถว 0: สถานะ
            label_status = ctk.CTkLabel(right_info_container, text="สถานะ:", 
                                        font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_status.grid(row=0, column=0, sticky="w", pady=3)
            value_status = ctk.CTkLabel(right_info_container, text=status_display_text, 
                                        font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_status.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # แถว 1: การชำระเงิน
            label_payment = ctk.CTkLabel(right_info_container, text="การชำระเงิน:", 
                                         font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_payment.grid(row=1, column=0, sticky="w", pady=3)
            value_payment = ctk.CTkLabel(right_info_container, text=order_details_dict.get('payment_method', '-'), 
                                         font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_payment.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # --- 5.6 เส้นคั่น ---
            separator1 = ctk.CTkFrame(receipt_card, height=2, fg_color="#FFEBEE")
            separator1.pack(fill="x", padx=30, pady=10)
            
            # --- 5.7 ส่วนหัวตารางรายการสินค้า ---
            items_table_header = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=10)
            items_table_header.pack(fill="x", padx=30, pady=(20, 10))
            
            # Frame ภายใน Header สำหรับจัด Grid
            header_grid_layout = ctk.CTkFrame(items_table_header, fg_color="transparent")
            header_grid_layout.pack(fill="x", padx=15, pady=10)
            header_grid_layout.grid_columnconfigure(0, weight=2) # คอลัมน์ชื่อ กว้าง 2 ส่วน
            header_grid_layout.grid_columnconfigure(1, weight=1) # คอลัมน์จำนวน กว้าง 1 ส่วน
            header_grid_layout.grid_columnconfigure(2, weight=1) # คอลัมน์ราคา กว้าง 1 ส่วน
            
            # Label หัวข้อ "รายการสินค้า"
            header_label_item = ctk.CTkLabel(header_grid_layout, text="รายการสินค้า", 
                                             font=ctk.CTkFont(size=14, weight="bold"), 
                                             text_color="#6D4C41", anchor="w")
            header_label_item.grid(row=0, column=0, sticky="w", padx=5)
            
            # Label หัวข้อ "จำนวน"
            header_label_qty = ctk.CTkLabel(header_grid_layout, text="จำนวน", 
                                            font=ctk.CTkFont(size=14, weight="bold"), 
                                            text_color="#6D4C41", anchor="center")
            header_label_qty.grid(row=0, column=1, padx=5)
            
            # Label หัวข้อ "ราคา" (Placeholder)
            header_label_price = ctk.CTkLabel(header_grid_layout, text="ราคา", 
                                              font=ctk.CTkFont(size=14, weight="bold"), 
                                              text_color="#6D4C41", anchor="e")
            header_label_price.grid(row=0, column=2, sticky="e", padx=5)
            
            # --- 5.8 ส่วนแสดงรายการสินค้า ---
            items_list_container = ctk.CTkFrame(receipt_card, fg_color="transparent")
            items_list_container.pack(fill="x", padx=30)
            
            # --- แยก String รายการสินค้า (จาก GROUP_CONCAT) ---
            items_string_from_db = order_details_dict.get('items', '') # เช่น "Doll A x2, Doll B x1"
            if items_string_from_db:
                # แยกด้วย ", "
                item_strings = items_string_from_db.split(', ') 
                # วนลูปสร้างแถวสำหรับแต่ละรายการ
                for single_item_string in item_strings:
                    # --- สร้างแถวสินค้า 1 แถว (เขียนตรงๆ แทน add_item_row) ---
                    
                    # --- แยกชื่อและจำนวนออกจาก String ---
                    # ใช้ rsplit แยกจากขวา ด้วย ' x' แค่ 1 ครั้ง
                    parts = single_item_string.rsplit(' x', 1) 
                    if len(parts) == 2: # ถ้าแยกได้ 2 ส่วน (มี ' x')
                        item_name = parts[0]
                        item_quantity = parts[1]
                    else: # ถ้าแยกไม่ได้ (ไม่มี ' x' หรือ format ผิด)
                        item_name = single_item_string # ใช้ทั้ง string เป็นชื่อ
                        item_quantity = "1" # สมมติว่าจำนวนเป็น 1
                    
                    # --- สร้าง Frame สำหรับแถวนี้ ---
                    item_row_frame = ctk.CTkFrame(items_list_container, fg_color="#FFF0F5", corner_radius=10)
                    item_row_frame.pack(fill="x", pady=5)
                    
                    # --- Frame ภายในสำหรับจัด Grid ---
                    item_row_grid = ctk.CTkFrame(item_row_frame, fg_color="transparent")
                    item_row_grid.pack(fill="x", padx=15, pady=10)
                    item_row_grid.grid_columnconfigure(0, weight=2) # ชื่อ
                    item_row_grid.grid_columnconfigure(1, weight=1) # จำนวน
                    item_row_grid.grid_columnconfigure(2, weight=1) # ราคา
                    
                    # Label ชื่อสินค้า
                    item_name_label_row = ctk.CTkLabel(item_row_grid, text=f"• {item_name}", 
                                                      font=ctk.CTkFont(size=14), text_color="#6D4C41", anchor="w")
                    item_name_label_row.grid(row=0, column=0, sticky="w", padx=5)
                    
                    # Label จำนวน
                    item_qty_label_row = ctk.CTkLabel(item_row_grid, text=f"x{item_quantity}", 
                                                     font=ctk.CTkFont(size=14), text_color="#FFB6C1", anchor="center")
                    item_qty_label_row.grid(row=0, column=1, padx=5)
                    
                    # Label ราคา (Placeholder - ข้อมูลราคาต่อรายการไม่ได้ถูกดึงมา)
                    item_price_label_row = ctk.CTkLabel(item_row_grid, text="-", 
                                                       font=ctk.CTkFont(size=14), text_color="#6D4C41", anchor="e")
                    item_price_label_row.grid(row=0, column=2, sticky="e", padx=5)
                    # --- จบการสร้างแถวสินค้า 1 แถว ---
            # --- จบ Loop แสดงรายการสินค้า ---

            # --- 5.9 เส้นคั่น ---
            separator2 = ctk.CTkFrame(receipt_card, height=2, fg_color="#FFEBEE")
            separator2.pack(fill="x", padx=30, pady=20)
            
            # --- 5.10 ส่วนแสดงยอดรวม ---
            total_display_frame_outer = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=15)
            total_display_frame_outer.pack(fill="x", padx=30, pady=20)
            
            # Frame ภายในสำหรับจัดวาง
            total_grid_layout = ctk.CTkFrame(total_display_frame_outer, fg_color="transparent")
            total_grid_layout.pack(fill="x", padx=20, pady=15)
            
            # Label "ยอดรวมทั้งสิ้น:"
            total_text_label_receipt = ctk.CTkLabel(total_grid_layout, text="ยอดรวมทั้งสิ้น:", 
                                                   font=ctk.CTkFont(size=20, weight="bold"), 
                                                   text_color="#6D4C41")
            total_text_label_receipt.pack(side="left")
            
            # Label แสดงยอดรวม (ดึงจาก DB และจัดรูปแบบ)
            total_value_label_receipt = ctk.CTkLabel(
                total_grid_layout,
                text=f"฿{order_details_dict.get('total_amount', 0):,.2f}", 
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#FF6B9D"
            )
            total_value_label_receipt.pack(side="right")
            
            # --- 5.11 ส่วนแสดงที่อยู่จัดส่ง (ถ้ามี) ---
            shipping_address_from_db = order_details_dict.get('shipping_address')
            if shipping_address_from_db: # เช็คว่ามีข้อมูลที่อยู่หรือไม่
                shipping_address_frame = ctk.CTkFrame(receipt_card, fg_color="#FFF0F5", corner_radius=15)
                shipping_address_frame.pack(fill="x", padx=30, pady=20)
                
                # Label หัวข้อ "ที่อยู่จัดส่ง"
                address_title_label = ctk.CTkLabel(
                    shipping_address_frame, text="📍 ที่อยู่จัดส่ง", 
                    font=ctk.CTkFont(size=16, weight="bold"), 
                    text_color="#6D4C41", anchor="w"
                )
                address_title_label.pack(anchor="w", padx=20, pady=(15, 5))
                
                # Label แสดงที่อยู่
                address_value_label = ctk.CTkLabel(
                    shipping_address_frame, text=shipping_address_from_db, 
                    font=ctk.CTkFont(size=14), text_color="#6D4C41", 
                    anchor="w", justify="left" # anchor="w" และ justify="left"
                )
                address_value_label.pack(anchor="w", padx=20, pady=(0, 15))
            
            # --- 5.12 ส่วน Footer ---
            receipt_footer_frame = ctk.CTkFrame(receipt_card, fg_color="transparent")
            receipt_footer_frame.pack(fill="x", padx=30, pady=(20, 30))
            
            footer_text1 = ctk.CTkLabel(receipt_footer_frame, text="ขอบคุณที่ใช้บริการ 💖", 
                                        font=ctk.CTkFont(size=18, weight="bold"), 
                                        text_color="#FFB6C1")
            footer_text1.pack()
            
            footer_text2 = ctk.CTkLabel(
                receipt_footer_frame, 
                text="Dollie Shop | www.dollieshop.com | โทร: 02-xxx-xxxx", 
                font=ctk.CTkFont(size=12), text_color="gray50"
            )
            footer_text2.pack(pady=(5, 0))
            # --- จบการสร้างเนื้อหาใบเสร็จ ---

    # --- (ลบฟังก์ชัน create_header, create_receipt_content) ---
    # --- (ลบฟังก์ชัน add_info_row, add_item_row) ---
    
    def print_receipt(self):
        """ฟังก์ชันพิมพ์ใบเสร็จ (ยังทำไม่ได้จริง แค่แสดง popup)"""
        messagebox.showinfo(
            "พิมพ์ใบเสร็จ",
            "ฟีเจอร์พิมพ์ใบเสร็จยังไม่รองรับ\nคุณสามารถใช้การ Screenshot หน้าจอนี้แทนได้ค่ะ",
            parent=self # ให้ popup แสดงเหนือหน้าต่างนี้
        )