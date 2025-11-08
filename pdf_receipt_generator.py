"""
PDF Receipt Generator - สไตล์สลิปเซเว่น-อีเลฟเว่น
สร้างใบเสร็จแบบสลิปความร้อน พร้อม VAT 7%
ใช้ฟอนต์ไทยที่มากับ Windows (Angsana New, Cordia New, Browallia New)
"""

from reportlab.lib.pagesizes import letter
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os
import sys

# ตัวแปรเก็บสถานะฟอนต์
FONT_NAME = 'ThaiFont'
FONT_BOLD = 'ThaiFontBold'

def find_thai_font():
    """หาฟอนต์ไทยที่มีอยู่ในระบบ"""
    
    # รายการฟอนต์ไทยที่มักมีใน Windows
    thai_fonts = [
        ('angsa.ttf', 'angsab.ttf', 'Angsana New'),      # Angsana New
        ('cordia.ttf', 'cordiab.ttf', 'Cordia New'),      # Cordia New
        ('browalia.ttf', 'browalib.ttf', 'Browallia New'), # Browallia New
    ]
    
    # path ของ Windows Fonts
    if sys.platform == 'win32':
        font_dir = r'C:\Windows\Fonts'
        
        for regular_file, bold_file, font_display_name in thai_fonts:
            regular_path = os.path.join(font_dir, regular_file)
            bold_path = os.path.join(font_dir, bold_file)
            
            if os.path.exists(regular_path):
                print(f"✓ พบฟอนต์: {font_display_name}")
                return regular_path, bold_path, font_display_name
    
    # สำหรับ Mac/Linux - ใช้ฟอนต์สำรอง
    return None, None, None

def setup_thai_font():
    """ตั้งค่าฟอนต์ไทยจากระบบ"""
    
    # ตรวจสอบว่าฟอนต์ถูกลงทะเบียนแล้วหรือยัง
    try:
        pdfmetrics.getFont('ThaiFont')
        print("✓ ฟอนต์ไทยพร้อมใช้งานแล้ว")
        return True
    except:
        pass
    
    # หาฟอนต์ในระบบ
    regular_path, bold_path, font_name = find_thai_font()
    
    if regular_path and os.path.exists(regular_path):
        try:
            # ลงทะเบียนฟอนต์ปกติ
            pdfmetrics.registerFont(TTFont('ThaiFont', regular_path))
            
            # ลงทะเบียนฟอนต์หนา (ถ้ามี)
            if bold_path and os.path.exists(bold_path):
                pdfmetrics.registerFont(TTFont('ThaiFontBold', bold_path))
            else:
                # ถ้าไม่มี Bold ให้ใช้ปกติแทน
                pdfmetrics.registerFont(TTFont('ThaiFontBold', regular_path))
            
            print(f"✓ ลงทะเบียนฟอนต์ {font_name} สำเร็จ")
            return True
            
        except Exception as e:
            print(f"❌ ไม่สามารถลงทะเบียนฟอนต์: {e}")
    else:
        print("⚠ ไม่พบฟอนต์ไทยในระบบ")
    
    return False

def generate_receipt_pdf(order_id, db):
    """
    สร้างใบเสร็จ PDF แบบสลิปเซเว่น (ภาษาไทย)
    
    Args:
        order_id: รหัสคำสั่งซื้อ
        db: database object
    
    Returns:
        str: path ของไฟล์ PDF ที่สร้าง หรือ None ถ้าสร้างไม่สำเร็จ
    """
    
    # ตั้งค่าฟอนต์ก่อนทุกครั้ง
    font_success = setup_thai_font()
    
    # กำหนดฟอนต์ที่จะใช้
    if font_success:
        font_regular = 'ThaiFont'
        font_bold = 'ThaiFontBold'
    else:
        # ถ้าไม่สำเร็จ ใช้ฟอนต์สำรอง
        font_regular = 'Helvetica'
        font_bold = 'Helvetica-Bold'
        print("⚠ ใช้ฟอนต์สำรอง Helvetica (อาจแสดงภาษาไทยไม่ถูกต้อง)")
    
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
    
    # ขนาดกระดาษสลิป (80mm x 297mm)
    slip_width = 80 * mm
    slip_height = 297 * mm
    
    # สร้าง Canvas
    c = canvas.Canvas(pdf_path, pagesize=(slip_width, slip_height))
    
    # ตำแหน่ง Y เริ่มต้น (จากบนลงล่าง)
    y_position = slip_height - 10 * mm
    left_margin = 5 * mm
    line_height = 4 * mm
    
    # ===== ส่วนหัว =====
    c.setFont(font_bold, 20)
    c.drawCentredString(slip_width / 2, y_position, "DOLLIE SHOP")
    y_position -= line_height * 1.2
    
    c.setFont(font_regular, 10)
    c.drawCentredString(slip_width / 2, y_position, "ร้านขายตุ๊กตาน่ารัก")
    y_position -= line_height
    
    # ข้อมูลร้าน
    c.setFont(font_regular, 8)
    store_info = [
        "123 ถนนสุขุมวิท แขวงคลองเตย",
        "เขตคลองเตย กรุงเทพฯ 10110",
        "โทร: 02-xxx-xxxx",
        "เลขประจำตัวผู้เสียภาษี: x-xxxx-xxxxx-xx-x"
    ]
    
    for info in store_info:
        c.drawCentredString(slip_width / 2, y_position, info)
        y_position -= line_height * 0.8
    
    # เส้นคั่น
    y_position -= line_height * 0.5
    c.setDash(1, 2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setDash()
    y_position -= line_height
    
    # ===== ข้อมูลใบเสร็จ =====
    c.setFont(font_bold, 10)
    c.drawCentredString(slip_width / 2, y_position, "ใบเสร็จรับเงิน / RECEIPT")
    y_position -= line_height * 1.2
    
    # เลขที่ใบเสร็จ
    c.setFont(font_regular, 9)
    c.drawString(left_margin, y_position, f"เลขที่: #{order_details['order_id']}")
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
    c.setDash(1, 2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setDash()
    y_position -= line_height
    
    # ===== รายการสินค้า =====
    c.setFont(font_bold, 9)
    c.drawString(left_margin, y_position, "รายการสินค้า")
    y_position -= line_height * 1.2
    
    # Parse รายการสินค้า
    items_string = order_details.get('items', '')
    items_list = []
    
    if items_string:
        item_strings = items_string.split(', ')
        c.setFont(font_regular, 8)
        
        for item_str in item_strings:
            parts = item_str.rsplit(' x', 1)
            if len(parts) == 2:
                item_name = parts[0]
                quantity = int(parts[1])
            else:
                item_name = item_str
                quantity = 1
            
            items_list.append({'name': item_name, 'qty': quantity})
    
    # คำนวณราคา
    total_with_vat = float(order_details.get('total_amount', 0))
    subtotal = total_with_vat / 1.07  # ถอด VAT 7%
    vat_amount = total_with_vat - subtotal
    
    # แสดงรายการสินค้า
    if items_list:
        price_per_item = subtotal / len(items_list)
        
        for item in items_list:
            item_total = price_per_item * item['qty']
            
            # ชื่อสินค้า
            c.drawString(left_margin, y_position, f"{item['name']}")
            y_position -= line_height * 0.9
            
            # จำนวนและราคา
            qty_price_text = f"  {item['qty']} x {price_per_item:.2f} บาท"
            c.drawString(left_margin + 3*mm, y_position, qty_price_text)
            c.drawRightString(slip_width - left_margin, y_position, f"{item_total:.2f}")
            y_position -= line_height * 1.2
    
    # เส้นคั่น
    y_position -= line_height * 0.5
    c.setDash(1, 2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setDash()
    y_position -= line_height
    
    # ===== สรุปยอดเงิน =====
    c.setFont(font_regular, 9)
    
    # ยอดรวมสินค้า (ก่อน VAT)
    c.drawString(left_margin, y_position, "ยอดรวม")
    c.drawRightString(slip_width - left_margin, y_position, f"{subtotal:.2f} บาท")
    y_position -= line_height
    
    # VAT 7%
    c.drawString(left_margin, y_position, "ภาษีมูลค่าเพิ่ม 7%")
    c.drawRightString(slip_width - left_margin, y_position, f"{vat_amount:.2f} บาท")
    y_position -= line_height * 1.2
    
    # เส้นคั่นหนา
    c.setLineWidth(2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setLineWidth(1)
    y_position -= line_height
    
    # ยอดรวมทั้งสิ้น
    c.setFont(font_bold, 12)
    c.drawString(left_margin, y_position, "ยอดรวมทั้งสิ้น")
    c.drawRightString(slip_width - left_margin, y_position, f"{total_with_vat:.2f} บาท")
    y_position -= line_height * 1.5
    
    # เส้นคั่น
    c.setLineWidth(1)
    c.setDash(1, 2)
    c.line(left_margin, y_position, slip_width - left_margin, y_position)
    c.setDash()
    y_position -= line_height
    
    # ===== ข้อมูลเพิ่มเติม =====
    c.setFont(font_regular, 8)
    
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
        c.setFont(font_bold, 8)
        c.drawString(left_margin, y_position, "ที่อยู่จัดส่ง:")
        y_position -= line_height * 0.9
        
        c.setFont(font_regular, 7)
        # แบ่งที่อยู่ยาวๆ เป็นหลายบรรทัด
        max_width = slip_width - (2 * left_margin)
        address_lines = wrap_text(shipping_address, c, max_width, 7, font_regular)
        for addr_line in address_lines:
            c.drawString(left_margin, y_position, addr_line)
            y_position -= line_height * 0.8
    
    y_position -= line_height
    
    # ===== ส่วนท้าย =====
    c.setFont(font_regular, 8)
    c.drawCentredString(slip_width / 2, y_position, "*** ขอบคุณที่ใช้บริการ ***")
    y_position -= line_height
    c.drawCentredString(slip_width / 2, y_position, "www.dollieshop.com")
    y_position -= line_height * 1.5
    
    # บาร์โค้ดจำลอง
    c.setFont('Courier', 10)
    c.drawCentredString(slip_width / 2, y_position, "| || ||| || | ||| | || ||| |")
    y_position -= line_height * 0.7
    c.setFont('Courier', 8)
    c.drawCentredString(slip_width / 2, y_position, f"*{order_id:08d}*")
    
    # บันทึก PDF
    c.save()
    
    print(f"✓ สร้าง PDF สำเร็จ: {pdf_path}")
    return pdf_path


def wrap_text(text, canvas_obj, max_width, font_size, font_name):
    """แบ่งข้อความยาวเป็นหลายบรรทัด"""
    words = text.split()
    lines = []
    current_line = ""
    
    for word in words:
        test_line = current_line + " " + word if current_line else word
        text_width = canvas_obj.stringWidth(test_line, font_name, font_size)
        
        if text_width <= max_width:
            current_line = test_line
        else:
            if current_line:
                lines.append(current_line)
            current_line = word
    
    if current_line:
        lines.append(current_line)
    
    return lines