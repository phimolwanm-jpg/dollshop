import customtkinter as ctk
from tkinter import messagebox
import os # <-- (NEW) Import 
import traceback # <-- (NEW) Import สำหรับ Debug

# --- (NEW) Import ตัวสร้าง PDF ---
try:
    from pdf_receipt_generator import generate_receipt_pdf
except ImportError:
    print("!!! ไม่พบไฟล์ 'pdf_receipt_generator.py' !!!")
    generate_receipt_pdf = None # ตั้งเป็น None ถ้า Import ไม่ได้
# --- (จบส่วน NEW) ---


class ReceiptWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#FFF0F5") 
        self.main_app = main_app
        self.db = main_app.db 
        self.order_id_to_show = None 
        
    def on_show(self, order_id=None):
        """
        ทำงานทุกครั้งที่เปิดหน้านี้: รับ order_id, ลบ UI เก่า, สร้าง UI ใหม่
        """
        self.order_id_to_show = order_id 
        
        for widget in self.winfo_children():
            widget.destroy()
        
        if not self.order_id_to_show:
            # --- ถ้าไม่ได้รับ: แสดงหน้า Error ---
            error_label = ctk.CTkLabel(
                self, 
                text="❌ ไม่พบข้อมูลคำสั่งซื้อ",
                font=ctk.CTkFont(size=24, weight="bold"),
                text_color="#F44336"
            )
            error_label.pack(expand=True) 
            
            error_back_button = ctk.CTkButton(
                self,
                text="กลับไปหน้าหลัก",
                command=lambda: self.main_app.navigate_to('HomeWindow'), 
                fg_color="#FFB6C1", 
                hover_color="#FFC0CB"
            )
            error_back_button.pack(pady=20)
        else:
            # --- ถ้าได้รับ order_id: สร้างหน้า UI ใบเสร็จ ---
            self.setup_ui() 

    def setup_ui(self):
        """สร้างองค์ประกอบ UI ทั้งหมดของหน้าใบเสร็จ"""
        # ( ... โค้ดส่วน setup_ui ทั้งหมดเหมือนเดิม ... )
        # ( ... ตั้งแต่บรรทัด 55 ถึง 414 ในไฟล์เดิมของคุณ ... )
        
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
            text="🧾 ใบเสร็จการสั่งซื้อ",
            font=ctk.CTkFont(size=28, weight="bold"),
            text_color="#FFB6C1"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.pack(side="right", padx=20)
        
        # ปุ่ม "พิมพ์" (ยังกดไม่ได้จริง)
        print_button = ctk.CTkButton(
            header_buttons_frame,
            text="🖨️ พิมพ์ (PDF)", # (EDITED) เปลี่ยนข้อความ
            fg_color="#4CAF50", 
            hover_color="#66BB6A",
            command=self.print_receipt # (EDITED) เรียกฟังก์ชัน print_receipt (ที่เราจะแก้ไข)
        )
        print_button.pack(side="left", padx=5)
        
        home_button = ctk.CTkButton(
            header_buttons_frame,
            text="🏠 หน้าหลัก",
            fg_color="transparent",
            text_color="#FFB6C1",
            hover_color="#FFE4E1",
            command=lambda: self.main_app.navigate_to('HomeWindow') 
        )
        home_button.pack(side="left", padx=5)
        
        # --- 3. สร้าง Frame หลักสำหรับเนื้อหาใบเสร็จ (เลื่อนได้) ---
        receipt_container_scrollable = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#FFB6C1"
        )
        receipt_container_scrollable.grid(row=1, column=0, sticky="nsew", padx=30, pady=20) 
        
        # --- 4. สร้างการ์ดสีขาว (เหมือนกระดาษใบเสร็จ) ---
        receipt_card = ctk.CTkFrame(
            receipt_container_scrollable, 
            fg_color="#FFFFFF",
            corner_radius=20,
            border_width=3,
            border_color="#FFB6C1" 
        )
        receipt_card.pack(fill="both", expand=True, padx=50, pady=20) 
        
        # --- 5. สร้างเนื้อหาใบเสร็จ ---
        order_details_dict = self.db.get_order_details(self.order_id_to_show) 
        
        if not order_details_dict:
            error_label_inside_card = ctk.CTkLabel(
                receipt_card, 
                text="ไม่พบข้อมูลคำสั่งซื้อ",
                text_color="#F44336" 
            )
            error_label_inside_card.pack(pady=50)
        else:
            # ( ... โค้ดส่วนที่เหลือของ setup_ui (5.3 - 5.12) เหมือนเดิม ... )
            # --- 5.3 ส่วน Logo และชื่อร้าน ---
            shop_logo_frame = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=15)
            shop_logo_frame.pack(fill="x", padx=30, pady=(30, 20))
            shop_icon_label = ctk.CTkLabel(shop_logo_frame, text="🎀", font=ctk.CTkFont(size=60))
            shop_icon_label.pack(pady=(20, 10))
            shop_name_label = ctk.CTkLabel(shop_logo_frame, text="Dollie Shop", font=ctk.CTkFont(size=32, weight="bold"), text_color="#FF6B9D")
            shop_name_label.pack()
            shop_subtitle_label = ctk.CTkLabel(shop_logo_frame, text="ร้านขายตุ๊กตาน่ารัก", font=ctk.CTkFont(size=14), text_color="#6D4C41")
            shop_subtitle_label.pack(pady=(0, 20))
            
            # --- 5.4 ส่วน Title "ใบเสร็จรับเงิน" ---
            receipt_title_frame = ctk.CTkFrame(receipt_card, fg_color="transparent")
            receipt_title_frame.pack(fill="x", padx=30, pady=20)
            receipt_title_label = ctk.CTkLabel(receipt_title_frame, text="ใบเสร็จรับเงิน / RECEIPT", font=ctk.CTkFont(size=24, weight="bold"), text_color="#6D4C41")
            receipt_title_label.pack()
            
            # --- 5.5 ส่วนข้อมูล Order ---
            order_info_frame = ctk.CTkFrame(receipt_card, fg_color="#FFF0F5", corner_radius=15)
            order_info_frame.pack(fill="x", padx=30, pady=20)
            order_info_frame.grid_columnconfigure((0, 1), weight=1)
            
            left_info_container = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            left_info_container.grid(row=0, column=0, sticky="w", padx=20, pady=20) 
            
            label_order_id = ctk.CTkLabel(left_info_container, text="เลขที่ใบเสร็จ:", font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_order_id.grid(row=0, column=0, sticky="w", pady=3)
            value_order_id = ctk.CTkLabel(left_info_container, text=f"#{order_details_dict['order_id']}", font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_order_id.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)
            
            order_date_str = order_details_dict.get('created_at', '-') 
            if order_date_str and len(order_date_str) > 16:
                order_date_str = order_date_str[:16] 
            label_date = ctk.CTkLabel(left_info_container, text="วันที่:", font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_date.grid(row=1, column=0, sticky="w", pady=3)
            value_date = ctk.CTkLabel(left_info_container, text=order_date_str, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_date.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)
            
            label_customer = ctk.CTkLabel(left_info_container, text="ลูกค้า:", font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_customer.grid(row=2, column=0, sticky="w", pady=3)
            value_customer = ctk.CTkLabel(left_info_container, text=order_details_dict.get('full_name', '-'), font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_customer.grid(row=2, column=1, sticky="w", padx=(10, 0), pady=3)
            
            right_info_container = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            right_info_container.grid(row=0, column=1, sticky="w", padx=20, pady=20) 
            
            order_status = order_details_dict.get('status', 'unknown')
            status_text_map = {'pending': '⏳ รอดำเนินการ', 'confirmed': '✅ ยืนยันแล้ว', 'shipped': '🚚 กำลังจัดส่ง', 'delivered': '✔️ จัดส่งสำเร็จ', 'cancelled': '❌ ยกเลิก'}
            status_display_text = status_text_map.get(order_status, order_status)
            
            label_status = ctk.CTkLabel(right_info_container, text="สถานะ:", font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_status.grid(row=0, column=0, sticky="w", pady=3)
            value_status = ctk.CTkLabel(right_info_container, text=status_display_text, font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_status.grid(row=0, column=1, sticky="w", padx=(10, 0), pady=3)
            
            label_payment = ctk.CTkLabel(right_info_container, text="การชำระเงิน:", font=ctk.CTkFont(size=13), text_color="gray50", anchor="w")
            label_payment.grid(row=1, column=0, sticky="w", pady=3)
            value_payment = ctk.CTkLabel(right_info_container, text=order_details_dict.get('payment_method', '-'), font=ctk.CTkFont(size=13, weight="bold"), text_color="#6D4C41", anchor="w")
            value_payment.grid(row=1, column=1, sticky="w", padx=(10, 0), pady=3)
            
            # --- 5.6 เส้นคั่น ---
            separator1 = ctk.CTkFrame(receipt_card, height=2, fg_color="#FFEBEE")
            separator1.pack(fill="x", padx=30, pady=10)
            
            # --- 5.7 ส่วนหัวตารางรายการสินค้า ---
            items_table_header = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=10)
            items_table_header.pack(fill="x", padx=30, pady=(20, 10))
            
            header_grid_layout = ctk.CTkFrame(items_table_header, fg_color="transparent")
            header_grid_layout.pack(fill="x", padx=15, pady=10)
            header_grid_layout.grid_columnconfigure(0, weight=2) 
            header_grid_layout.grid_columnconfigure(1, weight=1) 
            header_grid_layout.grid_columnconfigure(2, weight=1) 
            
            header_label_item = ctk.CTkLabel(header_grid_layout, text="รายการสินค้า", font=ctk.CTkFont(size=14, weight="bold"), text_color="#6D4C41", anchor="w")
            header_label_item.grid(row=0, column=0, sticky="w", padx=5)
            header_label_qty = ctk.CTkLabel(header_grid_layout, text="จำนวน", font=ctk.CTkFont(size=14, weight="bold"), text_color="#6D4C41", anchor="center")
            header_label_qty.grid(row=0, column=1, padx=5)
            header_label_price = ctk.CTkLabel(header_grid_layout, text="ราคา", font=ctk.CTkFont(size=14, weight="bold"), text_color="#6D4C41", anchor="e")
            header_label_price.grid(row=0, column=2, sticky="e", padx=5)
            
            # --- 5.8 ส่วนแสดงรายการสินค้า ---
            items_list_container = ctk.CTkFrame(receipt_card, fg_color="transparent")
            items_list_container.pack(fill="x", padx=30)
            
            items_string_from_db = order_details_dict.get('items', '') 
            if items_string_from_db:
                item_strings = items_string_from_db.split(', ') 
                for single_item_string in item_strings:
                    parts = single_item_string.rsplit(' x', 1) 
                    if len(parts) == 2: 
                        item_name = parts[0]
                        item_quantity = parts[1]
                    else: 
                        item_name = single_item_string 
                        item_quantity = "1" 
                    
                    item_row_frame = ctk.CTkFrame(items_list_container, fg_color="#FFF0F5", corner_radius=10)
                    item_row_frame.pack(fill="x", pady=5)
                    
                    item_row_grid = ctk.CTkFrame(item_row_frame, fg_color="transparent")
                    item_row_grid.pack(fill="x", padx=15, pady=10)
                    item_row_grid.grid_columnconfigure(0, weight=2) 
                    item_row_grid.grid_columnconfigure(1, weight=1) 
                    item_row_grid.grid_columnconfigure(2, weight=1) 
                    
                    item_name_label_row = ctk.CTkLabel(item_row_grid, text=f"• {item_name}", font=ctk.CTkFont(size=14), text_color="#6D4C41", anchor="w")
                    item_name_label_row.grid(row=0, column=0, sticky="w", padx=5)
                    
                    item_qty_label_row = ctk.CTkLabel(item_row_grid, text=f"x{item_quantity}", font=ctk.CTkFont(size=14), text_color="#FFB6C1", anchor="center")
                    item_qty_label_row.grid(row=0, column=1, padx=5)
                    
                    item_price_label_row = ctk.CTkLabel(item_row_grid, text="-", font=ctk.CTkFont(size=14), text_color="#6D4C41", anchor="e")
                    item_price_label_row.grid(row=0, column=2, sticky="e", padx=5)

            # --- 5.9 เส้นคั่น ---
            separator2 = ctk.CTkFrame(receipt_card, height=2, fg_color="#FFEBEE")
            separator2.pack(fill="x", padx=30, pady=20)
            
            # --- 5.10 ส่วนแสดงยอดรวม ---
            total_display_frame_outer = ctk.CTkFrame(receipt_card, fg_color="#FFE4E1", corner_radius=15)
            total_display_frame_outer.pack(fill="x", padx=30, pady=20)
            
            total_grid_layout = ctk.CTkFrame(total_display_frame_outer, fg_color="transparent")
            total_grid_layout.pack(fill="x", padx=20, pady=15)
            
            total_text_label_receipt = ctk.CTkLabel(total_grid_layout, text="ยอดรวมทั้งสิ้น:", font=ctk.CTkFont(size=20, weight="bold"), text_color="#6D4C41")
            total_text_label_receipt.pack(side="left")
            
            total_value_label_receipt = ctk.CTkLabel(
                total_grid_layout,
                text=f"฿{order_details_dict.get('total_amount', 0):,.2f}", 
                font=ctk.CTkFont(size=28, weight="bold"),
                text_color="#FF6B9D"
            )
            total_value_label_receipt.pack(side="right")
            
            # --- 5.11 ส่วนแสดงที่อยู่จัดส่ง ---
            shipping_address_from_db = order_details_dict.get('shipping_address')
            if shipping_address_from_db: 
                shipping_address_frame = ctk.CTkFrame(receipt_card, fg_color="#FFF0F5", corner_radius=15)
                shipping_address_frame.pack(fill="x", padx=30, pady=20)
                
                address_title_label = ctk.CTkLabel(shipping_address_frame, text="📍 ที่อยู่จัดส่ง", font=ctk.CTkFont(size=16, weight="bold"), text_color="#6D4C41", anchor="w")
                address_title_label.pack(anchor="w", padx=20, pady=(15, 5))
                
                address_value_label = ctk.CTkLabel(shipping_address_frame, text=shipping_address_from_db, font=ctk.CTkFont(size=14), text_color="#6D4C41", anchor="w", justify="left")
                address_value_label.pack(anchor="w", padx=20, pady=(0, 15))
            
            # --- 5.12 ส่วน Footer ---
            receipt_footer_frame = ctk.CTkFrame(receipt_card, fg_color="transparent")
            receipt_footer_frame.pack(fill="x", padx=30, pady=(20, 30))
            
            footer_text1 = ctk.CTkLabel(receipt_footer_frame, text="ขอบคุณที่ใช้บริการ 💖", font=ctk.CTkFont(size=18, weight="bold"), text_color="#FFB6C1")
            footer_text1.pack()
            
            footer_text2 = ctk.CTkLabel(receipt_footer_frame, text="Dollie Shop | www.dollieshop.com | โทร: 02-xxx-xxxx", font=ctk.CTkFont(size=12), text_color="gray50")
            footer_text2.pack(pady=(5, 0))
    
    # --- (EDITED) แก้ไขฟังก์ชันพิมพ์ใบเสร็จ ---
    def print_receipt(self):
        """ฟังก์ชันพิมพ์ใบเสร็จ (สร้าง PDF และเปิดไฟล์)"""
        
        # 1. ตรวจสอบว่า Import generator มาได้หรือไม่
        if not generate_receipt_pdf:
            messagebox.showerror(
                "เกิดข้อผิดพลาด",
                "ไม่พบโมดูลสำหรับสร้าง PDF (pdf_receipt_generator.py)\nกรุณาตรวจสอบการติดตั้ง",
                parent=self
            )
            return

        # 2. ตรวจสอบว่ามี Order ID หรือไม่
        if not self.order_id_to_show:
            messagebox.showerror("ผิดพลาด", "ไม่พบ Order ID", parent=self)
            return
        
        try:
            # 3. เรียกใช้ generator (ส่ง self.db ไปด้วย)
            print(f"กำลังสร้าง PDF สำหรับ Order ID: {self.order_id_to_show}")
            pdf_file_path = generate_receipt_pdf(self.order_id_to_show, self.db)
            
            if pdf_file_path:
                # 4. ถ้าสร้างสำเร็จ
                abs_path = os.path.abspath(pdf_file_path)
                messagebox.showinfo(
                    "สำเร็จ",
                    f"บันทึกใบเสร็จ PDF ที่:\n{abs_path}\n\nกำลังพยายามเปิดไฟล์...",
                    parent=self
                )
                
                # 5. ลองเปิดไฟล์ PDF ด้วยโปรแกรม default ของเครื่อง
                try:
                    os.startfile(abs_path) # สำหรับ Windows
                except AttributeError:
                    try:
                        os.system(f'open "{abs_path}"') # สำหรับ macOS
                    except Exception:
                        try:
                            os.system(f'xdg-open "{abs_path}"') # สำหรับ Linux
                        except Exception as e_open:
                            print(f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้: {e_open}")
                            messagebox.showwarning("ไม่สามารถเปิดไฟล์", 
                                                   f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้\nกรุณาไปที่:\n{abs_path}", 
                                                   parent=self)
            else:
                # 6. ถ้า generator คืนค่า None (สร้างไม่สำเร็จ)
                messagebox.showerror("ผิดพลาด", "ไม่สามารถสร้างไฟล์ PDF ได้ (อาจไม่พบข้อมูล Order)", parent=self)
                
        except Exception as e:
            # 7. จัดการ Error ร้ายแรง
            messagebox.showerror("ผิดพลาดร้ายแรง", f"เกิดข้อผิดพลาดขณะสร้าง PDF: {e}", parent=self)
            traceback.print_exc() # พิมพ์ Error เต็มๆ ลงใน Console