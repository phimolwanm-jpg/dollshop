import customtkinter as ctk
from tkinter import messagebox
import os
import traceback

# Import ตัวสร้าง PDF
try:
    from pdf_receipt_generator import generate_receipt_pdf
except ImportError:
    print("!!! ไม่พบไฟล์ 'pdf_receipt_generator.py' !!!")
    generate_receipt_pdf = None


class ReceiptWindow(ctk.CTkFrame):
    def __init__(self, parent, main_app):
        super().__init__(parent, fg_color="#F5F5F5")  # สีพื้นหลังสไตล์เซเว่น
        self.main_app = main_app
        self.db = main_app.db 
        self.order_id_to_show = None 
        
    def on_show(self, order_id=None):
        """ทำงานทุกครั้งที่เปิดหน้านี้"""
        self.order_id_to_show = order_id 
        
        for widget in self.winfo_children():
            widget.destroy()
        
        if not self.order_id_to_show:
            # แสดงหน้า Error
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
                fg_color="#FF6B35", 
                hover_color="#FF8C42"
            )
            error_back_button.pack(pady=20)
        else:
            self.setup_ui() 

    def setup_ui(self):
        """สร้าง UI ใบเสร็จสไตล์สลิปเซเว่น"""
        
        # Grid หลัก
        self.grid_columnconfigure(0, weight=1) 
        self.grid_rowconfigure(1, weight=1)    

        # ===== ส่วนหัว =====
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
        
        header_title = ctk.CTkLabel(
            header_frame,
            text="🧾 ใบเสร็จ / RECEIPT",
            font=ctk.CTkFont(size=26, weight="bold"),
            text_color="#FF6B35"
        )
        header_title.pack(side="left", padx=30, pady=20)
        
        header_buttons_frame = ctk.CTkFrame(header_frame, fg_color="transparent")
        header_buttons_frame.pack(side="right", padx=20)
        
        # ปุ่มบันทึก PDF
        save_pdf_button = ctk.CTkButton(
            header_buttons_frame,
            text="💾 บันทึก PDF",
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
            command=lambda: self.main_app.navigate_to('HomeWindow') 
        )
        home_button.pack(side="left", padx=5)
        
        # ===== ส่วนเนื้อหาใบเสร็จ =====
        receipt_container = ctk.CTkScrollableFrame(
            self, 
            fg_color="transparent",
            scrollbar_button_color="#FF6B35"
        )
        receipt_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10) 
        
        # การ์ดสลิป (แคบเหมือนสลิปจริง)
        slip_card = ctk.CTkFrame(
            receipt_container, 
            fg_color="#FFFFFF",
            corner_radius=8,
            border_width=2,
            border_color="#CCCCCC",
            width=400  # กว้างประมาณ 400px เหมือนสลิป
        )
        slip_card.pack(pady=20, padx=100)  # Padding ซ้าย-ขวาเยอะเพื่อให้ดูเป็นสลิปแคบๆ
        
        # ดึงข้อมูล Order
        order_details = self.db.get_order_details(self.order_id_to_show) 
        
        if not order_details:
            error_label = ctk.CTkLabel(
                slip_card, 
                text="ไม่พบข้อมูลคำสั่งซื้อ",
                text_color="#F44336" 
            )
            error_label.pack(pady=50)
        else:
            # ===== เนื้อหาสลิป =====
            
            # โลโก้ร้าน
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
            
            store_info_lines = [
                "123 ถนนสุขุมวิท แขวงคลองเตย",
                "เขตคลองเตย กรุงเทพฯ 10110",
                "โทร: 02-xxx-xxxx",
                "TAX ID: x-xxxx-xxxxx-xx-x"
            ]
            
            for line in store_info_lines:
                info_label = ctk.CTkLabel(
                    store_info_frame,
                    text=line,
                    font=ctk.CTkFont(size=10),
                    text_color="#666666"
                )
                info_label.pack()
            
            # เส้นคั่น 1
            separator1 = ctk.CTkFrame(slip_card, height=2, fg_color="#DDDDDD")
            separator1.pack(fill="x", padx=20, pady=15)
            
            # หัวข้อใบเสร็จ
            receipt_title = ctk.CTkLabel(
                slip_card,
                text="ใบเสร็จรับเงิน / RECEIPT",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#333333"
            )
            receipt_title.pack(pady=5)
            
            # ข้อมูล Order
            order_info_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
            order_info_frame.pack(pady=10, padx=30, fill="x")
            
            # เลขที่
            order_id_row = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            order_id_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                order_id_row,
                text="เลขที่:",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                order_id_row,
                text=f"#{order_details['order_id']}",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # วันที่-เวลา
            order_date = order_details.get('created_at', '-')
            if order_date and len(order_date) > 19:
                order_date = order_date[:19]
            
            date_row = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            date_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                date_row,
                text="วันที่:",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                date_row,
                text=order_date,
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # ลูกค้า
            customer_row = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            customer_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                customer_row,
                text="ลูกค้า:",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                customer_row,
                text=order_details.get('full_name', 'ลูกค้าทั่วไป'),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # การชำระเงิน
            payment_row = ctk.CTkFrame(order_info_frame, fg_color="transparent")
            payment_row.pack(fill="x", pady=2)
            ctk.CTkLabel(
                payment_row,
                text="ชำระโดย:",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                payment_row,
                text=order_details.get('payment_method', '-'),
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # เส้นคั่น 2
            separator2 = ctk.CTkFrame(slip_card, height=2, fg_color="#DDDDDD")
            separator2.pack(fill="x", padx=20, pady=15)
            
            # หัวตารางสินค้า
            items_header = ctk.CTkLabel(
                slip_card,
                text="รายการสินค้า",
                font=ctk.CTkFont(size=13, weight="bold"),
                text_color="#333333",
                anchor="w"
            )
            items_header.pack(padx=30, pady=(5, 10), anchor="w")
            
            # รายการสินค้า
            items_container = ctk.CTkFrame(slip_card, fg_color="transparent")
            items_container.pack(fill="x", padx=30)
            
            items_string = order_details.get('items', '')
            items_list = []
            
            if items_string:
                item_strings = items_string.split(', ')
                for item_str in item_strings:
                    parts = item_str.rsplit(' x', 1)
                    if len(parts) == 2:
                        item_name = parts[0]
                        quantity = int(parts[1])
                    else:
                        item_name = item_str
                        quantity = 1
                    
                    items_list.append({'name': item_name, 'qty': quantity})
            
            # คำนวณราคา (ถอด VAT)
            total_with_vat = float(order_details.get('total_amount', 0))
            subtotal = total_with_vat / 1.07  # ราคาก่อน VAT
            vat_amount = total_with_vat - subtotal  # ยอด VAT 7%
            
            # แสดงรายการสินค้า
            if items_list:
                price_per_item = subtotal / len(items_list)
                
                for item in items_list:
                    item_total = price_per_item * item['qty']
                    
                    # ชื่อสินค้า
                    item_name_label = ctk.CTkLabel(
                        items_container,
                        text=item['name'],
                        font=ctk.CTkFont(size=11),
                        text_color="#333333",
                        anchor="w"
                    )
                    item_name_label.pack(anchor="w", pady=(5, 2))
                    
                    # จำนวนและราคา
                    item_detail_row = ctk.CTkFrame(items_container, fg_color="transparent")
                    item_detail_row.pack(fill="x", pady=(0, 8))
                    
                    qty_price_text = f"  {item['qty']} x {price_per_item:.2f}"
                    ctk.CTkLabel(
                        item_detail_row,
                        text=qty_price_text,
                        font=ctk.CTkFont(size=10),
                        text_color="#666666",
                        anchor="w"
                    ).pack(side="left")
                    
                    ctk.CTkLabel(
                        item_detail_row,
                        text=f"{item_total:.2f}",
                        font=ctk.CTkFont(size=10),
                        text_color="#333333",
                        anchor="e"
                    ).pack(side="right")
            
            # เส้นคั่น 3
            separator3 = ctk.CTkFrame(slip_card, height=1, fg_color="#DDDDDD")
            separator3.pack(fill="x", padx=20, pady=15)
            
            # สรุปยอดเงิน
            summary_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
            summary_frame.pack(fill="x", padx=30, pady=10)
            
            # ยอดรวมสินค้า (ก่อน VAT)
            subtotal_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
            subtotal_row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                subtotal_row,
                text="ยอดรวม (Subtotal)",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                subtotal_row,
                text=f"{subtotal:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # VAT 7%
            vat_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
            vat_row.pack(fill="x", pady=3)
            ctk.CTkLabel(
                vat_row,
                text="VAT 7%",
                font=ctk.CTkFont(size=11),
                text_color="#666666",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                vat_row,
                text=f"{vat_amount:.2f}",
                font=ctk.CTkFont(size=11),
                text_color="#333333",
                anchor="e"
            ).pack(side="right")
            
            # เส้นคั่นหนา
            separator4 = ctk.CTkFrame(slip_card, height=3, fg_color="#333333")
            separator4.pack(fill="x", padx=20, pady=10)
            
            # ยอดรวมทั้งสิ้น
            total_row = ctk.CTkFrame(summary_frame, fg_color="transparent")
            total_row.pack(fill="x", pady=5)
            ctk.CTkLabel(
                total_row,
                text="ยอดรวมทั้งสิ้น",
                font=ctk.CTkFont(size=14, weight="bold"),
                text_color="#333333",
                anchor="w"
            ).pack(side="left")
            ctk.CTkLabel(
                total_row,
                text=f"{total_with_vat:.2f}",
                font=ctk.CTkFont(size=16, weight="bold"),
                text_color="#FF6B35",
                anchor="e"
            ).pack(side="right")
            
            # เส้นคั่น 5
            separator5 = ctk.CTkFrame(slip_card, height=2, fg_color="#DDDDDD")
            separator5.pack(fill="x", padx=20, pady=15)
            
            # สถานะและที่อยู่
            extra_info_frame = ctk.CTkFrame(slip_card, fg_color="#F9F9F9", corner_radius=8)
            extra_info_frame.pack(fill="x", padx=20, pady=10)
            
            # สถานะ
            status_map = {
                'pending': '⏳ รอดำเนินการ',
                'confirmed': '✅ ยืนยันแล้ว',
                'shipped': '🚚 กำลังจัดส่ง',
                'delivered': '✔️ จัดส่งสำเร็จ',
                'cancelled': '❌ ยกเลิก'
            }
            status_text = status_map.get(order_details.get('status', 'pending'), 'รอดำเนินการ')
            
            status_label = ctk.CTkLabel(
                extra_info_frame,
                text=f"สถานะ: {status_text}",
                font=ctk.CTkFont(size=10),
                text_color="#666666"
            )
            status_label.pack(pady=(10, 5), padx=15)
            
            # ที่อยู่จัดส่ง
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
                    wraplength=320
                )
                address_text.pack(pady=(0, 10), padx=15, anchor="w")
            
            # Footer
            footer_frame = ctk.CTkFrame(slip_card, fg_color="transparent")
            footer_frame.pack(pady=20)
            
            thank_you = ctk.CTkLabel(
                footer_frame,
                text="*** ขอบคุณที่ใช้บริการ ***",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#FF6B35"
            )
            thank_you.pack()
            
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
        """บันทึกใบเสร็จเป็น PDF และเปิดไฟล์"""
        
        # ตรวจสอบ generator
        if not generate_receipt_pdf:
            messagebox.showerror(
                "เกิดข้อผิดพลาด",
                "ไม่พบโมดูลสำหรับสร้าง PDF (pdf_receipt_generator.py)\nกรุณาตรวจสอบการติดตั้ง",
                parent=self
            )
            return

        # ตรวจสอบ Order ID
        if not self.order_id_to_show:
            messagebox.showerror("ผิดพลาด", "ไม่พบ Order ID", parent=self)
            return
        
        try:
            # สร้าง PDF
            print(f"กำลังสร้าง PDF สำหรับ Order ID: {self.order_id_to_show}")
            pdf_file_path = generate_receipt_pdf(self.order_id_to_show, self.db)
            
            if pdf_file_path:
                # สร้างสำเร็จ
                abs_path = os.path.abspath(pdf_file_path)
                messagebox.showinfo(
                    "สำเร็จ",
                    f"✅ บันทึกใบเสร็จ PDF สำเร็จ!\n\n📁 ที่: {abs_path}\n\n🔄 กำลังเปิดไฟล์...",
                    parent=self
                )
                
                # เปิดไฟล์ PDF
                try:
                    os.startfile(abs_path)  # Windows
                except AttributeError:
                    try:
                        os.system(f'open "{abs_path}"')  # macOS
                    except Exception:
                        try:
                            os.system(f'xdg-open "{abs_path}"')  # Linux
                        except Exception as e_open:
                            print(f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้: {e_open}")
                            messagebox.showwarning(
                                "ไม่สามารถเปิดไฟล์", 
                                f"ไม่สามารถเปิดไฟล์ PDF อัตโนมัติได้\n\nกรุณาไปที่:\n{abs_path}", 
                                parent=self
                            )
            else:
                # สร้างไม่สำเร็จ
                messagebox.showerror(
                    "ผิดพลาด", 
                    "❌ ไม่สามารถสร้างไฟล์ PDF ได้\n(อาจไม่พบข้อมูล Order)", 
                    parent=self
                )
                
        except Exception as e:
            # Error ร้ายแรง
            messagebox.showerror(
                "ผิดพลาดร้ายแรง", 
                f"⚠️ เกิดข้อผิดพลาดขณะสร้าง PDF:\n\n{e}", 
                parent=self
            )
            traceback.print_exc()