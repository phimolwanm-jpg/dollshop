import customtkinter as ctk
from tkinter import messagebox
import os
import traceback
from datetime import datetime, timedelta # 👈 1. Import datetime และ timedelta

# นำเข้าตัวสร้าง PDF
try:
    from pdf_receipt_generator import generate_receipt_pdf
except ImportError:
    print("!!! ไม่พบไฟล์ 'pdf_receipt_generator.py' !!!")
    generate_receipt_pdf = None


class ReceiptWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F5F5F5")
        self.main_app = main_app
        self.db = main_app.db
        self.order_id_to_show = None

    def on_show(self, order_id=None):
        # เก็บเลข order ที่จะแสดง
        self.order_id_to_show = order_id
        
        # ลบของเก่าออกก่อน
        for widget in self.winfo_children():
            widget.destroy()
        
        # ตรวจสอบว่ามี order_id หรือไม่
        if not self.order_id_to_show:
            self.show_error_page()
        else:
            self.setup_ui()

    def show_error_page(self):
        # แสดงหน้า Error
        error_label = ctk.CTkLabel(
            self,
            text="⌛ ไม่พบข้อมูลคำสั่งซื้อ",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#F44336"
        )
        error_label.pack(expand=True)
        
        error_back_button = ctk.CTkButton(
            self,
            text="กลับไปหน้าหลัก",
            command=self.go_to_home,
            fg_color="#FF6B35",
            hover_color="#FF8C42"
        )
        error_back_button.pack(pady=20)

    def go_to_home(self):
        # ฟังก์ชันกลับหน้าหลัก
        self.main_app.navigate_to('HomeWindow')

    def setup_ui(self):
        # ตั้งค่า Grid หลัก
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        
        # สร้างส่วนหัว
        self.create_header()
        
        # สร้างส่วนเนื้อหาใบเสร็จ
        self.create_receipt_content()

    def create_header(self):
        # สร้างกรอบส่วนหัว
        header_frame = ctk.CTkFrame(
            self,
            fg_color="#FFFFFF",
            corner_radius=0,
            height=70,
            border_width=2,
            border_color="#E0E0E0"
        )
        header_frame.grid(row=0, column=0, sticky="ew", pady=(0, 10))
        header_frame.grid_columnconfigure(1, weight=1)
        
        # ข้อความหัวเรื่อง
        header_title = ctk.CTkLabel(
            header_frame,
            text="🧾 ใบเสร็จ / RECEIPT",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#FF6B35"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        # กรอบใส่ปุ่ม
        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.pack(side="right", padx=20)
        
        # ปุ่มบันทึก PDF
        save_pdf_button = ctk.CTkButton(
            header_buttons_frame,
            text="💾 บันทึก PDF (A4)", # <<< แก้ไขเล็กน้อย
            fg_color="#4CAF50",
            hover_color="#66BB6A",
            font=ctk.CTkFont(size=14, weight="bold"),
            command=self.print_receipt
        )
        save_pdf_button.pack(side="left", padx=5)
        
        # ปุ่มหน้าหลัก
        home_button = ctk.CTkButton(
            header_buttons_frame,
            text="🏠 หน้าหลัก",
            fg_color="transparent",
            text_color="#FF6B35",
            hover_color="#FFE4E1",
            border_width=2,
            border_color="#FF6B35",
            command=self.go_to_home
        )
        home_button.pack(side="left", padx=5)

    def create_receipt_content(self):
        # สร้างกรอบที่เลื่อนได้
        receipt_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            scrollbar_button_color="#FF6B35"
        )
        receipt_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        
        # การ์ดสลิป
        slip_card = ctk.CTkFrame(
            receipt_container,
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=2,
            border_color="#CCCCCC",
            width=800  # ### <<< แก้ไข >>> ### (เปลี่ยนจาก 400 เป็น 800)
        )
        slip_card.pack(pady=20, padx=100, expand=True) # ### <<< เพิ่ม expand=True >>> ###
        
        # ดึงข้อมูล Order จากฐานข้อมูล
        order_details = self.db.get_order_details(self.order_id_to_show)
        
        if not order_details:
            # ถ้าไม่มีข้อมูล
            error_label = ctk.CTkLabel(
                slip_card,
                text="ไม่พบข้อมูลคำสั่งซื้อ",
                text_color="#F44336"
            )
            error_label.pack(pady=50)
        else:
            # สร้างเนื้อหาสลิป
            self.build_receipt_slip(slip_card, order_details)

    def build_receipt_slip(self, slip_card, order_details):
        # สร้างส่วนหัวร้าน
        self.create_shop_header(slip_card)
        
        # เส้นคั่น
        self.create_separator(slip_card)
        
        # ข้อมูล Order
        self.create_order_info(slip_card, order_details)
        
        # เส้นคั่น
        self.create_separator(slip_card)
        
        # รายการสินค้า
        self.create_items_list(slip_card, order_details)
        
        # เส้นคั่นบาง
        self.create_thin_separator(slip_card)
        
        # สรุปยอดเงิน
        self.create_summary(slip_card, order_details)
        
        # เส้นคั่นหนา
        self.create_thick_separator(slip_card)
        
        # ยอดรวมทั้งสิ้น
        self.create_grand_total(slip_card, order_details)
        
        # เส้นคั่น
        self.create_separator(slip_card)
        
        # ข้อมูลเพิ่มเติม (สถานะและที่อยู่)
        self.create_extra_info(slip_card, order_details)
        
        # ส่วนท้าย
        self.create_footer(slip_card, order_details)

    def create_shop_header(self, slip_card):
        # โลโก้
        logo_label = ctk.CTkLabel(
            slip_card,
            text="🎀",
            font=ctk.CTkFont(size=48)
        )
        logo_label.pack(pady=(20, 5))
        
        # ชื่อร้าน
        shop_name = ctk.CTkLabel(
            slip_card,
            text="DOLLIE SHOP",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color="#FF6B35"
        )
        shop_name.pack()
        
        # คำบรรยาย
        shop_subtitle = ctk.CTkLabel(
            slip_card,
            text="ร้านขายตุ๊กตาน่ารัก",
            font=ctk.CTkFont(size=12),
            text_color="#666666"
        )
        shop_subtitle.pack()
        
        # ข้อมูลร้าน
        store_info_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
        store_info_frame.pack(pady=10)
        
        store_lines = [
            "123 ถนนสุขุมวิท แขวงคลองเตย",
            "เขตคลองเตย กรุงเทพฯ 10110",
            "โทร: 02-xxx-xxxx",
            "TAX ID: x-xxxx-xxxxx-xx-x"
        ]
        
        for line in store_lines:
            info_label = ctk.CTkLabel(
                store_info_frame,
                text=line,
                font=ctk.CTkFont(size=10),
                text_color="#666666"
            )
            info_label.pack()

    def create_separator(self, slip_card):
        # เส้นคั่นปกติ
        separator = ctk.CTkFrame(slip_card, height=2, fg_color="#DDDDDD")
        separator.pack(fill="x", padx=20, pady=15)

    def create_thin_separator(self, slip_card):
        # เส้นคั่นบาง
        separator = ctk.CTkFrame(slip_card, height=1, fg_color="#DDDDDD")
        separator.pack(fill="x", padx=20, pady=15)

    def create_thick_separator(self, slip_card):
        # เส้นคั่นหนา
        separator = ctk.CTkFrame(slip_card, height=3, fg_color="#333333")
        separator.pack(fill="x", padx=20, pady=10)

    def create_order_info(self, slip_card, order_details):
        # หัวข้อ
        receipt_title = ctk.CTkLabel(
            slip_card,
            text="ใบเสร็จรับเงิน / RECEIPT",
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#333333"
        )
        receipt_title.pack(pady=5)
        
        # กรอบข้อมูล Order
        order_info_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
        order_info_frame.pack(pady=10, padx=30, fill="x")
        
        # เลขที่
        self.create_info_row(
            order_info_frame,
            "เลขที่:",
            f"#{order_details['order_id']}"
        )
        
        # --- 🛠️ ปรับแก้: แปลงเวลา UTC เป็นเวลาไทย (UTC+7) ---
        order_date_str = order_details.get('created_at', '-')
        if order_date_str and order_date_str != '-':
            try:
                # 1. แปลง String (UTC) เป็น datetime object
                utc_dt = datetime.strptime(order_date_str, '%Y-%m-%d %H:%M:%S')
                # 2. บวก 7 ชั่วโมง
                thai_dt = utc_dt + timedelta(hours=7)
                # 3. แปลงกลับเป็น String (เวลาไทย)
                order_date = thai_dt.strftime('%Y-%m-%d %H:%M') # YYYY-MM-DD HH:MM
            except ValueError:
                order_date = order_date_str[:16] # ถ้าแปลงไม่สำเร็จ, ใช้แบบเดิม
        else:
            order_date = '-'
        # --- 🛠️ สิ้นสุดการปรับแก้ ---
        
        self.create_info_row(order_info_frame, "วันที่:", order_date)
        
        # ลูกค้า
        customer_name = order_details.get('full_name', 'ลูกค้าทั่วไป')
        self.create_info_row(order_info_frame, "ลูกค้า:", customer_name)
        
        # เบอร์โทรลูกค้า
        customer_phone = order_details.get('buyer_phone', '-')
        if not customer_phone: 
             customer_phone = order_details.get('phone', '-')
             
        self.create_info_row(order_info_frame, "เบอร์โทร:", customer_phone)
        
        # การชำระเงิน
        payment = order_details.get('payment_method', '-')
        self.create_info_row(order_info_frame, "ชำระโดย:", payment)

    def create_info_row(self, parent_frame, label_text, value_text):
        # สร้างแถวข้อมูล (ซ้าย: ป้ายกำกับ, ขวา: ค่า)
        row_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=2)
        
        label = ctk.CTkLabel(
            row_frame,
            text=label_text,
            font=ctk.CTkFont(size=11),
            text_color="#666666",
            anchor="w"
        )
        label.pack(side="left")
        
        value = ctk.CTkLabel(
            row_frame,
            text=value_text,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color="#333333",
            anchor="e"
        )
        value.pack(side="right")

    def create_items_list(self, slip_card, order_details):
        # หัวตาราง
        items_header = ctk.CTkLabel(
            slip_card,
            text="รายการสินค้า",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#333333",
            anchor="w"
        )
        items_header.pack(padx=30, pady=(5, 10), anchor="w")
        
        # กรอบรายการสินค้า
        items_container = ctk.CTkFrame(slip_card, fg_color="transparent")
        items_container.pack(fill="x", padx=30)
        
        # แปลง string รายการเป็น list
        items_list = self.parse_items_string(order_details.get('items', ''))
        
        # คำนวณราคา
        total_with_vat = float(order_details.get('total_amount', 0))
        subtotal = total_with_vat / 1.07
        
        # แสดงรายการสินค้า
        if items_list:
            total_quantity = sum(item['qty'] for item in items_list)
            if total_quantity == 0:
                 total_quantity = 1 
                 
            price_per_unit = subtotal / total_quantity
            
            for item in items_list:
                item_total = price_per_unit * item['qty']
                self.create_item_row(items_container, item, price_per_unit, item_total)

    def parse_items_string(self, items_string):
        # แปลง string รายการสินค้าเป็น list ของ dict
        items_list = []
        
        if not items_string:
            return items_list
        
        item_strings = items_string.split(', ')
        
        for item_str in item_strings:
            try:
                parts = item_str.rsplit(' x', 1)
                
                if len(parts) == 2:
                    item_name = parts[0]
                    quantity = int(parts[1])
                else:
                    item_name = item_str
                    quantity = 1
                
                items_list.append({'name': item_name, 'qty': quantity})
            except Exception:
                items_list.append({'name': item_str, 'qty': 1})
        
        return items_list

    def create_item_row(self, parent_frame, item, price_per_item, item_total):
        # ชื่อสินค้า
        item_name_label = ctk.CTkLabel(
            parent_frame,
            text=item['name'],
            font=ctk.CTkFont(size=11),
            text_color="#333333",
            anchor="w"
        )
        item_name_label.pack(anchor="w", pady=(5, 2))
        
        # แถวจำนวนและราคา
        item_detail_row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        item_detail_row.pack(fill="x", pady=(0, 8))
        
        # จำนวน x ราคา
        qty_price_text = f"  {item['qty']} x {price_per_item:,.2f}"
        qty_label = ctk.CTkLabel(
            item_detail_row,
            text=qty_price_text,
            font=ctk.CTkFont(size=10),
            text_color="#666666",
            anchor="w"
        )
        qty_label.pack(side="left")
        
        # รวม
        total_label = ctk.CTkLabel(
            item_detail_row,
            text=f"{item_total:,.2f}",
            font=ctk.CTkFont(size=10),
            text_color="#333333",
            anchor="e"
        )
        total_label.pack(side="right")

    def create_summary(self, slip_card, order_details):
        # คำนวณราคา
        total_with_vat = float(order_details.get('total_amount', 0))
        subtotal = total_with_vat / 1.07
        vat_amount = total_with_vat - subtotal
        
        # กรอบสรุปยอด
        summary_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30, pady=10)
        
        # ยอดรวม (ก่อน VAT)
        self.create_summary_row(summary_frame, "ยอดรวม (Subtotal)", subtotal)
        
        # VAT 7%
        self.create_summary_row(summary_frame, "VAT 7%", vat_amount)

    def create_summary_row(self, parent_frame, label_text, amount):
        # สร้างแถวสรุปยอด
        row_frame = ctk.CTkFrame(parent_frame, fg_color="transparent")
        row_frame.pack(fill="x", pady=3)
        
        label = ctk.CTkLabel(
            row_frame,
            text=label_text,
            font=ctk.CTkFont(size=11),
            text_color="#666666",
            anchor="w"
        )
        label.pack(side="left")
        
        value = ctk.CTkLabel(
            row_frame,
            text=f"{amount:,.2f}", 
            font=ctk.CTkFont(size=11),
            text_color="#333333",
            anchor="e"
        )
        value.pack(side="right")

    def create_grand_total(self, slip_card, order_details):
        # ยอดรวมทั้งสิ้น
        total_with_vat = float(order_details.get('total_amount', 0))
        
        summary_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
        summary_frame.pack(fill="x", padx=30, pady=5)
        
        total_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
        total_row.pack(fill="x", pady=5)
        
        total_label = ctk.CTkLabel(
            total_row,
            text="ยอดรวมทั้งสิ้น",
            font=ctk.CTkFont(size=14, weight="bold"),
            text_color="#333333",
            anchor="w"
        )
        total_label.pack(side="left")
        
        total_value = ctk.CTkLabel(
            total_row,
            text=f"{total_with_vat:,.2f}", 
            font=ctk.CTkFont(size=16, weight="bold"),
            text_color="#FF6B35",
            anchor="e"
        )
        total_value.pack(side="right")

    def create_extra_info(self, slip_card, order_details):
        # กรอบข้อมูลเพิ่มเติม
        extra_info_frame = ctk.CTkFrame(
            slip_card,
            fg_color="#F9F9F9",
            corner_radius=8
        )
        extra_info_frame.pack(fill="x", padx=20, pady=10)
        
        # สถานะ
        status_text = self.get_status_text(order_details.get('status', 'pending'))
        status_label = ctk.CTkLabel(
            extra_info_frame,
            text=f"สถานะ: {status_text}",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        status_label.pack(pady=(10, 5), padx=15)
        
        # ที่อยู่จัดส่ง
        shipping_address = order_details.get('buyer_address')
        if not shipping_address:
             shipping_address = order_details.get('shipping_address') 
        
        if shipping_address:
            address_title = ctk.CTkLabel(
                extra_info_frame,
                text="📍 ที่อยู่จัดส่ง:",
                font=ctk.CTkFont(size=10, weight="bold"),
                text_color="#666666",
                anchor="w"
            )
            address_title.pack(pady=(5, 3), padx=15, anchor="w")
            
            address_text = ctk.CTkLabel(
                extra_info_frame,
                text=shipping_address,
                font=ctk.CTkFont(size=9),
                text_color="#666666",
                anchor="w",
                justify="left",
                wraplength=700 # ### <<< แก้ไข >>> ### (เปลี่ยนจาก 320 เป็น 700)
            )
            address_text.pack(pady=(0, 10), padx=15, anchor="w")

    def get_status_text(self, status):
        # แปลงสถานะเป็นข้อความแสดง
        status_map = {
            'pending': '⏳ รอดำเนินการ',
            'confirmed': '✅ ยืนยันแล้ว',
            'shipped': '🚚 กำลังจัดส่ง',
            'delivered': '✔️ จัดส่งสำเร็จ',
            'cancelled': '❌ ยกเลิก'
        }
        
        return status_map.get(status, 'รอดำเนินการ')

    def create_footer(self, slip_card, order_details):
        # กรอบส่วนท้าย
        footer_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
        footer_frame.pack(pady=20)
        
        # ข้อความขอบคุณ
        thank_you = ctk.CTkLabel(
            footer_frame,
            text="*** ขอบคุณที่ใช้บริการ ***",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#FF6B35"
        )
        thank_you.pack()
        
        # เว็บไซต์
        website = ctk.CTkLabel(
            footer_frame,
            text="www.dollieshop.com",
            font=ctk.CTkFont(size=10),
            text_color="#666666"
        )
        website.pack(pady=(5, 10))
        
        # บาร์โค้ดจำลอง
        barcode_label = ctk.CTkLabel(
            footer_frame,
            text="| || ||| || | ||| | || ||| |",
            font=ctk.CTkFont(size=14, family="Courier"),
            text_color="#333333"
        )
        barcode_label.pack()
        
        barcode_number = ctk.CTkLabel(
            footer_frame,
            text=f"*{order_details['order_id']:08d}*",
            font=ctk.CTkFont(size=9),
            text_color="#666666"
        )
        barcode_number.pack(pady=(0, 15))

    def print_receipt(self):
        # ตรวจสอบว่ามี generator หรือไม่
        if not generate_receipt_pdf:
            messagebox.showerror(
                "เกิดข้อผิดพลาด",
                "ไม่พบโมดูลสำหรับสร้าง PDF (pdf_receipt_generator.py)\nกรุณาตรวจสอบการติดตั้ง",
                parent=self
            )
            return
        
        # ตรวจสอบว่ามี Order ID หรือไม่
        if not self.order_id_to_show:
            messagebox.showerror("ผิดพลาด", "ไม่พบ Order ID", parent=self)
            return
        
        try:
            # สร้างไฟล์ PDF
            print(f"กำลังสร้าง PDF สำหรับ Order ID: {self.order_id_to_show}")
            pdf_file_path = generate_receipt_pdf(self.order_id_to_show, self.db)
            
            if pdf_file_path:
                # สร้างสำเร็จ
                abs_path = os.path.abspath(pdf_file_path)
                messagebox.showinfo(
                    "สำเร็จ",
                    f"✅ บันทึกใบเสร็จ PDF สำเร็จ!\n\n📁 ที่: {abs_path}\n\n📄 กำลังเปิดไฟล์...",
                    parent=self
                )
                
                # เปิดไฟล์ PDF
                self.open_pdf_file(abs_path)
            else:
                # สร้างไม่สำเร็จ
                messagebox.showerror(
                    "ผิดพลาด",
                    "❌ ไม่สามารถสร้างไฟล์ PDF ได้\n(อาจไม่พบข้อมูล Order)",
                    parent=self
                )
        
        except Exception as e:
            # เกิด Error
            messagebox.showerror(
                "ผิดพลาดร้ายแรง",
                f"⚠️ เกิดข้อผิดพลาดขณะสร้าง PDF:\n\n{e}",
                parent=self
            )
            traceback.print_exc()

    def open_pdf_file(self, file_path):
        # เปิดไฟล์ PDF ตามระบบปฏิบัติการ
        try:
            # Windows
            os.startfile(file_path)
        except AttributeError:
            try:
                # macOS
                os.system(f'open "{file_path}"')
            except Exception:
                try:
                    # Linux
                    os.system(f'xdg-open "{file_path}"')
                except Exception as e:
                    # ไม่สามารถเปิดได้
                    print(f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้: {e}")
                    messagebox.showwarning(
                        "ไม่สามารถเปิดไฟล์",
                        f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้\n\nกรุณาไปที่:\n{file_path}",
                        parent=self
                    )