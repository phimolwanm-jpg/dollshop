from reportlab.lib.units import mm
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from datetime import datetime
import os

# ==================== ตั้งค่าฟอนต์ ====================
def setup_thai_font():
    """ตั้งค่าฟอนต์ภาษาไทย"""
    try:
        # หาตำแหน่งไฟล์โปรแกรม
        program_folder = os.path.dirname(os.path.abspath(__file__))
        
        # สร้าง path ไปหาไฟล์ฟอนต์
        font_regular = os.path.join(program_folder, 'fonts', 'Sarabun-Regular.ttf')
        font_bold = os.path.join(program_folder, 'fonts', 'Sarabun-Bold.ttf')
        
        # ลงทะเบียนฟอนต์
        pdfmetrics.registerFont(TTFont('ThaiFont', font_regular))
        pdfmetrics.registerFont(TTFont('ThaiFontBold', font_bold))
        
        print("✓ ตั้งค่าฟอนต์ไทยสำเร็จ!")
        return 'ThaiFont', 'ThaiFontBold'
        
    except Exception as e:
        print(f"❌ ไม่พบไฟล์ฟอนต์: {e}")
        print("⚠️  จะใช้ฟอนต์ Helvetica แทน (ภาษาไทยจะแสดงไม่ได้)")
        return 'Helvetica', 'Helvetica-Bold'


# ตั้งค่าฟอนต์ตอนเริ่มโปรแกรม
FONT_NORMAL, FONT_BOLD = setup_thai_font()


# ==================== คำนวณราคา ====================
def calculate_prices(total_with_vat):
    """
    คำนวณราคาแยกส่วน
    
    พารามิเตอร์:
        total_with_vat: ราคารวม VAT แล้ว
    
    คืนค่า:
        (ราคาก่อน VAT, ค่า VAT)
    """
    price_before_vat = total_with_vat / 1.07  # ลบ VAT 7% ออก
    vat_amount = total_with_vat - price_before_vat
    
    return price_before_vat, vat_amount


# ==================== แบ่งข้อความยาว ====================
def split_long_text(text, canvas_obj, max_width, font_size):
    """
    แบ่งข้อความยาวๆ ให้พอดีกับความกว้างกระดาษ
    
    พารามิเตอร์:
        text: ข้อความที่จะแบ่g
        canvas_obj: ออบเจ็กต์ canvas ของ PDF
        max_width: ความกว้างสูงสุดที่อนุญาต
        font_size: ขนาดตัวอักษร
    
    คืนค่า:
        list ของข้อความที่แบ่งแล้ว
    """
    if not text:
        return []
        
    words = text.split()  # แยกคำ
    lines = []
    current_line = ""
    
    for word in words:
        # ลองเพิ่มคำใหม่เข้าไป
        if current_line:
            test_line = current_line + " " + word
        else:
            test_line = word
        
        # วัดความกว้างของข้อความ
        width = canvas_obj.stringWidth(test_line, FONT_NORMAL, font_size)
        
        # ถ้าพอดี ก็เก็บไว้
        if width <= max_width:
            current_line = test_line
        else:
            # ถ้ายาวเกิน ให้ขึ้นบรรทัดใหม่
            if current_line:
                lines.append(current_line)
            current_line = word
    
    # เก็บบรรทัดสุดท้าย
    if current_line:
        lines.append(current_line)
    
    return lines


# ==================== สร้าง PDF ====================
def generate_receipt_pdf(order_id, db):
    """
    ฟังก์ชันหลักในการสร้างใบเสร็จ PDF
    
    พารามิเตอร์:
        order_id: เลขที่คำสั่งซื้อ
        db: ออบเจ็กต์ database
    
    คืนค่า:
        path ของไฟล์ PDF หรือ None ถ้าสร้างไม่สำเร็จ
    """
    
    # ===== 1. ดึงข้อมูลจาก Database =====
    order_data = db.get_order_details(order_id)
    if not order_data:
        print(f"❌ ไม่พบคำสั่งซื้อเลขที่: {order_id}")
        return None
    
    # ===== 2. สร้างโฟลเดอร์เก็บไฟล์ =====
    pdf_folder = "receipts_pdf"
    if not os.path.exists(pdf_folder):
        os.makedirs(pdf_folder)
    
    # สร้างชื่อไฟล์
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    pdf_filename = f"receipt_{order_id}_{timestamp}.pdf"
    pdf_path = os.path.join(pdf_folder, pdf_filename)
    
    # ===== 3. กำหนดขนาดกระดาษ =====
    paper_width = 80 * mm   # กว้าง 80mm (กระดาษสลิป)
    paper_height = 297 * mm # สูง 297mm
    
    # สร้าง Canvas สำหรับวาด PDF
    c = canvas.Canvas(pdf_path, pagesize=(paper_width, paper_height))
    
    # ===== 4. กำหนดตำแหน่งเริ่มต้น =====
    y = paper_height - 10 * mm  # เริ่มจากบน ห่างขอบ 10mm
    margin_left = 5 * mm         # ขอบซ้าย
    line_space = 4 * mm          # ระยะห่างระหว่างบรรทัด
    
    
    # ========================================
    # ส่วนที่ 1: หัวร้าน
    # ========================================
    
    # ชื่อร้าน (ตัวใหญ่ตัวหนา)
    c.setFont(FONT_BOLD, 20)
    c.drawCentredString(paper_width / 2, y, "DOLLIE SHOP")
    y -= line_space * 1.2
    
    # คำโปรย
    c.setFont(FONT_NORMAL, 10)
    c.drawCentredString(paper_width / 2, y, "ร้านขายตุ๊กตาน่ารัก")
    y -= line_space
    
    # ข้อมูลร้าน
    c.setFont(FONT_NORMAL, 8)
    store_lines = [
        "123 ถนนสุขุมวิท แขวงคลองเตย",
        "เขตคลองเตย กรุงเทพฯ 10110",
        "โทร: 02-xxx-xxxx",
        "TAX ID: x-xxxx-xxxxx-xx-x"
    ]
    
    for line in store_lines:
        c.drawCentredString(paper_width / 2, y, line)
        y -= line_space * 0.8
    
    # เส้นคั่น
    y -= line_space * 0.5
    c.line(margin_left, y, paper_width - margin_left, y)
    y -= line_space
    
    
    # ========================================
    # ส่วนที่ 2: ข้อมูลใบเสร็จ
    # ========================================
    
    # หัวข้อ
    c.setFont(FONT_BOLD, 10)
    c.drawCentredString(paper_width / 2, y, "ใบเสร็จรับเงิน / RECEIPT")
    y -= line_space * 1.2
    
    # เลขที่ใบเสร็จ
    c.setFont(FONT_NORMAL, 9)
    c.drawString(margin_left, y, f"เลขที่: #{order_data['order_id']}")
    y -= line_space
    
    # วันที่
    order_date_str = order_data.get('created_at', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
    
    # ### <<< แก้ไขเล็กน้อย >>> ###
    # (แปลงเป็น object เพื่อจัดรูปแบบ, ถ้าทำได้)
    try:
        order_date_obj = datetime.fromisoformat(order_date_str)
        order_date = order_date_obj.strftime("%Y-%m-%d %H:%M")
    except Exception:
        if len(order_date_str) > 19:
             order_date = order_date_str[:19]  # ตัดให้เหลือ 19 ตัวอักษร
        else:
             order_date = order_date_str
             
    c.drawString(margin_left, y, f"วันที่: {order_date}")
    y -= line_space
    
    # ชื่อลูกค้า
    customer = order_data.get('full_name', 'ลูกค้าทั่วไป')
    c.drawString(margin_left, y, f"ลูกค้า: {customer}")
    y -= line_space
    
    # ### <<< เพิ่มใหม่ >>> ###
    # เบอร์โทรลูกค้า
    phone = order_data.get('buyer_phone', '-')
    if not phone or phone == 'None':
        phone = order_data.get('phone', '-') # ใช้ค่าสำรอง
        
    c.drawString(margin_left, y, f"เบอร์โทร: {phone}")
    y -= line_space
    # ### <<< จบส่วนที่เพิ่ม >>> ###
    
    # วิธีชำระเงิน
    payment = order_data.get('payment_method', '-')
    c.drawString(margin_left, y, f"ชำระโดย: {payment}")
    y -= line_space * 1.5
    
    # เส้นคั่น
    c.line(margin_left, y, paper_width - margin_left, y)
    y -= line_space
    
    
    # ========================================
    # ส่วนที่ 3: รายการสินค้า
    # ========================================
    
    c.setFont(FONT_BOLD, 9)
    c.drawString(margin_left, y, "รายการสินค้า")
    y -= line_space * 1.2
    
    # ดึงข้อมูลรายการสินค้า
    items_text = order_data.get('items', '')
    items = []
    
    if items_text:
        # แยกรายการสินค้า (คั่นด้วย ", ")
        item_list = items_text.split(', ')
        
        for item_text in item_list:
            try:
                # แยกชื่อสินค้าและจำนวน (คั่นด้วย " x")
                parts = item_text.rsplit(' x', 1)
                if len(parts) == 2:
                    name = parts[0]
                    quantity = int(parts[1])
                else:
                    name = item_text
                    quantity = 1
                
                items.append({'name': name, 'qty': quantity})
            except Exception:
                items.append({'name': item_text, 'qty': 1})
    
    # คำนวณราคา
    total = float(order_data.get('total_amount', 0))
    price_before_vat, vat = calculate_prices(total)
    
    # ถ้ามีหลายรายการ แบ่งราคาเฉลี่ย
    c.setFont(FONT_NORMAL, 8)
    if items:
        # ### <<< แก้ไขเล็กน้อย >>> ### (วิธีคำนวณราคาต่อชิ้น)
        total_quantity = sum(item['qty'] for item in items)
        if total_quantity == 0:
            total_quantity = 1 # ป้องกันหารด้วย 0
            
        # ราคาต่อหน่วย (เฉลี่ยจากราคาก่อน VAT / จำนวนชิ้นทั้งหมด)
        price_per_unit = price_before_vat / total_quantity
        
        for item in items:
            # ราคารวมของรายการนี้ = ราคาต่อหน่วย * จำนวนชิ้น
            item_total = price_per_unit * item['qty']
            
            # บรรทัดที่ 1: ชื่อสินค้า
            c.drawString(margin_left, y, item['name'])
            y -= line_space * 0.9
            
            # บรรทัดที่ 2: จำนวน x ราคา = ราคารวม
            qty_text = f"  {item['qty']} x {price_per_unit:,.2f}"
            c.drawString(margin_left + 3*mm, y, qty_text)
            c.drawRightString(paper_width - margin_left, y, f"{item_total:,.2f}")
            y -= line_space * 1.2
    
    # เส้นคั่น
    y -= line_space * 0.5
    c.line(margin_left, y, paper_width - margin_left, y)
    y -= line_space
    
    
    # ========================================
    # ส่วนที่ 4: สรุปยอดเงิน
    # ========================================
    
    c.setFont(FONT_NORMAL, 9)
    
    # ยอดรวม (ก่อน VAT)
    c.drawString(margin_left, y, "ยอดรวม (Subtotal)")
    c.drawRightString(paper_width - margin_left, y, f"{price_before_vat:,.2f}")
    y -= line_space
    
    # VAT 7%
    c.drawString(margin_left, y, "VAT 7%")
    c.drawRightString(paper_width - margin_left, y, f"{vat:,.2f}")
    y -= line_space * 1.2
    
    # เส้นคั่นหนา
    c.setLineWidth(2)
    c.line(margin_left, y, paper_width - margin_left, y)
    c.setLineWidth(1)
    y -= line_space
    
    # ยอดรวมทั้งสิ้น (ตัวใหญ่ตัวหนา)
    c.setFont(FONT_BOLD, 12)
    c.drawString(margin_left, y, "ยอดรวมทั้งสิ้น")
    c.drawRightString(paper_width - margin_left, y, f"{total:,.2f}")
    y -= line_space * 1.5
    
    # เส้นคั่น
    c.setLineWidth(1)
    c.line(margin_left, y, paper_width - margin_left, y)
    y -= line_space
    
    
    # ========================================
    # ส่วนที่ 5: ข้อมูลเพิ่มเติม
    # ========================================
    
    c.setFont(FONT_NORMAL, 8)
    
    # สถานะคำสั่งซื้อ
    status_thai = {
        'pending': 'รอดำเนินการ',
        'confirmed': 'ยืนยันแล้ว',
        'shipped': 'กำลังจัดส่ง',
        'delivered': 'จัดส่งสำเร็จ',
        'cancelled': 'ยกเลิก'
    }
    status = order_data.get('status', 'pending')
    status_text = status_thai.get(status, 'รอดำเนินการ')
    c.drawString(margin_left, y, f"สถานะ: {status_text}")
    y -= line_space * 1.2
    
    # ที่อยู่จัดส่ง
    # ### <<< แก้ไขเล็กน้อย >>> ### (ใช้ buyer_address)
    address = order_data.get('buyer_address')
    if not address:
        address = order_data.get('shipping_address') # ใช้ค่าสำรอง
        
    if address:
        c.setFont(FONT_BOLD, 8)
        c.drawString(margin_left, y, "ที่อยู่จัดส่ง:")
        y -= line_space * 0.9
        
        # แบ่งที่อยู่ยาวๆ เป็นหลายบรรทัด
        c.setFont(FONT_NORMAL, 7)
        max_width = paper_width - (2 * margin_left)
        address_lines = split_long_text(address, c, max_width, 7)
        
        for addr_line in address_lines:
            c.drawString(margin_left, y, addr_line)
            y -= line_space * 0.8
    
    y -= line_space
    
    
    # ========================================
    # ส่วนที่ 6: ท้ายใบเสร็จ
    # ========================================
    
    c.setFont(FONT_NORMAL, 8)
    c.drawCentredString(paper_width / 2, y, "*** ขอบคุณที่ใช้บริการ ***")
    y -= line_space
    
    c.drawCentredString(paper_width / 2, y, "www.dollieshop.com")
    y -= line_space * 1.5
    
    # บาร์โค้ดจำลอง
    c.setFont(FONT_NORMAL, 6)
    c.drawCentredString(paper_width / 2, y, "| || ||| || | ||| | || ||| |")
    y -= line_space * 0.7
    c.drawCentredString(paper_width / 2, y, f"*{order_id:08d}*")
    
    
    # ===== 5. บันทึกไฟล์ =====
    c.save()
    
    print(f"✓ สร้างใบเสร็จสำเร็จ: {pdf_path}")
    return pdf_path