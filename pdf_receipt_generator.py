"""
PDF Receipt Generator - สไตล์สลิปเซเว่น-อีเลฟเว่น
สร้างใบเสร็จแบบสลิปความร้อน พร้อม VAT 7%
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# ลงทะเบียนฟอนต์ไทย (ใช้ฟอนต์ default ของ ReportLab ที่รองรับไทย)
try:
    # ถ้ามีฟอนต์ TH Sarabun New ในเครื่อง
    pdfmetrics.registerFont(TTFont('THSarabun', 'THSarabunNew.ttf'))
    pdfmetrics.registerFont(TTFont('THSarabunBold', 'THSarabunNew Bold.ttf'))
    FONT_NAME = 'THSarabun'
    FONT_BOLD = 'THSarabunBold'
except:
    # ใช้ฟอนต์ default
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

def generate_receipt_pdf(order_id, db):
    """
    สร้างใบเสร็จ PDF แบบสลิปเซเว่น
    
    Args:
        order_id: รหัสคำสั่งซื้อ
        db: database object
    
    Returns:
        str: path ของไฟล์ PDF ที่สร้าง หรือ None ถ้าสร้างไม่สำเร็จ
    """
    
    # ดึงข้อมูล Order
    order_details = db.get_order_details(order_id)
    if not order_details:
        print(f"ไม่พบข้อมูล Order ID: {order_id}")
        return None
    
    # สร้างโฟลเดอร์เก็บ PDF
    output_folder = "receipts_pdf"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    
    # ชื่อไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"receipt_{order_id}_{timestamp}.pdf"
    pdf_path = os.path.join(output_folder, pdf_filename)
    
    # ขนาดกระดาษสลิป (80mm x 297mm - ยาวตามความต้องการ)
    slip_width = 80 * mm
    slip_height = 297 * mm
    
    # สร้าง Canvas
    c = canvas.Canvas(pdf_path, pagesize=(slip_width, slip_height))
    
    # ตำแหน่ง Y เริ่มต้น (จากบนลงล่าง)
    y_position = slip_height - 10 * mm
    left_margin = 5 * mm
    line_height = 4 * mm
    
    # ===== ส่วนหัว =====
    # โลโก้ร้าน (ใช้ตัวอักษรแทน)
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(slip_width / 2, y_position, "DOLLIE SHOP")
    y_position -= line_height * 1.2
    
    c.setFont(FONT_NAME, 10)
    c.drawCentredString(slip_width / 2, y_position, "ร้านขายตุ๊กตาน่ารัก")
    y_position -= line_height
    
    # ข้อมูลร้าน
    c.setFont(FONT_NAME, 8)
    store_info = [
        "123 ถนนสุขุมวิท แขวงคลองเตย",
        "เขตคลองเตย กรุงเทพฯ 10110",
        "โทร: 02-xxx-xxxx",
        "TAX ID: x-xxxx-xxxxx-xx-x"
    ]
    
    for info in store_info:
        c.drawCentredString(slip_width / 2, y_position, info)
        y_position -= line_height * 0.8
    
    # เส้นคั่น
    y_position -= line_height * 0.5
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    y_position -= line_height
    
    # ===== ข้อมูลใบเสร็จ =====
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(slip_width / 2, y_position, "ใบเสร็จรับเงิน / RECEIPT")
    y_position -= line_height * 1.2
    
    # เลขที่ใบเสร็จ
    c.setFont(FONT_NAME, 9)
    receipt_no = f"เลขที่: #{order_details['order_id']}"
    c.drawString(left_margin, y_position, receipt_no)
    y_position -= line_height
    
    # วันที่-เวลา
    order_date = order_details.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    if len(order_date) > 19:
        order_date = order_date[:19]
    c.drawString(left_margin, y_position, f"วันที่: {order_date}")
    y_position -= line_height
    
    # ลูกค้า
    customer_name = order_details.get('full_name', 'ลูกค้าทั่วไป')
    c.drawString(left_margin, y_position, f"ลูกค้า: {customer_name}")
    y_position -= line_height
    
    # การชำระเงิน
    payment_method = order_details.get('payment_method', '-')
    c.drawString(left_margin, y_position, f"ชำระโดย: {payment_method}")
    y_position -= line_height * 1.5
    
    # เส้นคั่น
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    y_position -= line_height
    
    # ===== รายการสินค้า =====
    c.setFont(FONT_BOLD, 9)
    c.drawString(left_margin, y_position, "รายการสินค้า")
    y_position -= line_height * 1.2
    
    # Parse รายการสินค้า
    items_string = order_details.get('items', '')
    items_list = []
    subtotal = 0.0
    
    if items_string:
        item_strings = items_string.split(', ')
        c.setFont(FONT_NAME, 8)
        
        for item_str in item_strings:
            parts = item_str.rsplit(' x', 1)
            if len(parts) == 2:
                item_name = parts[0]
                quantity = int(parts[1])
            else:
                item_name = item_str
                quantity = 1
            
            # คำนวณราคา (ในระบบจริงควรดึงจาก database)
            # ที่นี่เราจะคำนวณจาก total_amount แบ่งเฉลี่ย
            items_list.append({'name': item_name, 'qty': quantity})
    
    # คำนวณราคา
    total_with_vat = float(order_details.get('total_amount', 0))
    subtotal = total_with_vat / 1.07  # ถอด VAT 7%
    vat_amount = total_with_vat - subtotal
    
    # ถ้ามีหลายรายการ แบ่งราคาเฉลี่ย
    if items_list:
        price_per_item = subtotal / len(items_list)
        
        for item in items_list:
            item_total = price_per_item * item['qty']
            
            # แสดงชื่อสินค้า
            c.drawString(left_margin, y_position, f"{item['name']}")
            y_position -= line_height * 0.9
            
            # แสดงจำนวนและราคา
            qty_price_text = f"  {item['qty']} x {price_per_item:.2f}"
            c.drawString(left_margin + 3*mm, y_position, qty_price_text)
            c.drawRightString(slip_width - left_margin, y_position, f"{item_total:.2f}")
            y_position -= line_height * 1.2
    
    # เส้นคั่น
    y_position -= line_height * 0.5
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    y_position -= line_height
    
    # ===== สรุปยอดเงิน =====
    c.setFont(FONT_NAME, 9)
    
    # ยอดรวมสินค้า (ก่อน VAT)
    c.drawString(left_margin, y_position, "ยอดรวม (Subtotal)")
    c.drawRightString(slip_width - left_margin, y_position, f"{subtotal:.2f}")
    y_position -= line_height
    
    # VAT 7%
    c.drawString(left_margin, y_position, "VAT 7%")
    c.drawRightString(slip_width - left_margin, y_position, f"{vat_amount:.2f}")
    y_position -= line_height * 1.2
    
    # เส้นคั่นหนา
    c.setLineWidth(2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setLineWidth(1)
    y_position -= line_height
    
    # ยอดรวมทั้งสิ้น
    c.setFont(FONT_BOLD, 12)
    c.drawString(left_margin, y_position, "ยอดรวมทั้งสิ้น")
    c.drawRightString(slip_width - left_margin, y_position, f"{total_with_vat:.2f}")
    y_position -= line_height * 1.5
    
    # เส้นคั่น
    c.setLineWidth(1)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    y_position -= line_height
    
    # ===== ข้อมูลเพิ่มเติม =====
    c.setFont(FONT_NAME, 8)
    
    # สถานะ
    status_map = {
        'pending': 'รอดำเนินการ',
        'confirmed': 'ยืนยันแล้ว',
        'shipped': 'กำลังจัดส่ง',
        'delivered': 'จัดส่งสำเร็จ',
        'cancelled': 'ยกเลิก'
    }
    status = status_map.get(order_details.get('status', 'pending'), 'รอดำเนินการ')
    c.drawString(left_margin, y_position, f"สถานะ: {status}")
    y_position -= line_height * 1.2
    
    # ที่อยู่จัดส่ง
    shipping_address = order_details.get('shipping_address')
    if shipping_address:
        c.setFont(FONT_BOLD, 8)
        c.drawString(left_margin, y_position, "ที่อยู่จัดส่ง:")
        y_position -= line_height * 0.9
        
        c.setFont(FONT_NAME, 7)
        # แบ่งที่อยู่ยาวๆ เป็นหลายบรรทัด
        max_width = slip_width - (2 * left_margin)
        address_lines = wrap_text(shipping_address, c, max_width, 7)
        for addr_line in address_lines:
            c.drawString(left_margin, y_position, addr_line)
            y_position -= line_height * 0.8
    
    y_position -= line_height
    
    # ===== ส่วนท้าย =====
    c.setFont(FONT_NAME, 8)
    c.drawCentredString(slip_width / 2, y_position, "*** ขอบคุณที่ใช้บริการ ***")
    y_position -= line_height
    c.drawCentredString(slip_width / 2, y_position, "www.dollieshop.com")
    y_position -= line_height * 1.5
    
    # บาร์โค้ดจำลอง (ใช้เส้นแทน)
    c.setFont(FONT_NAME, 6)
    c.drawCentredString(slip_width / 2, y_position, "| || ||| || | ||| | || ||| |")
    y_position -= line_height * 0.7
    c.drawCentredString(slip_width / 2, y_position, f"*{order_id:08d}*")
    
    # บันทึก PDF
    c.save()
    
    print(f"สร้าง PDF สำเร็จ: {pdf_path}")
    return pdf_path


def wrap_text(text, canvas_obj, max_width, font_size):
    """แบ่งข้อความยาวเป็นหลายบรรทัด"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_width = canvas_obj.stringWidth(test_line, FONT_NAME, font_size)
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines