import sqlite3

# 1. (สำคัญ!) แก้ไข Path ให้ถูกต้อง ชี้ไปที่ไฟล์เดียวกับ database.py
db_path = r'M:\doll_shop\dollshop\dollieshop.db'
conn = sqlite3.connect(db_path)
c = conn.cursor()

print(f"เชื่อมต่อกับ {db_path} เพื่อเพิ่มข้อมูลสินค้า...")

try:
    # 2. (สำคัญ!) นี่คือส่วนที่ "หายไป"
    # คุณต้องใส่ข้อมูลสินค้าของคุณที่นี่
    # นี่คือตัวอย่าง: (กรุณาแก้ไขเป็นข้อมูลของคุณเอง)
    products_to_add = [
        ('ตุ๊กตาหมีน้อย', 'นุ่มนิ่มน่ากอด', 590.0, 50, 'ตุ๊กตา', 'images/bear.jpg'),
        ('รถแข่งบังคับ', 'เร็วแรงทะลุนรก', 1200.0, 30, 'ของเล่น', 'images/rc_car.jpg'),
        ('โมเดลกันดั้ม', 'ของแท้จากญี่ปุ่น', 2500.0, 15, 'โมเดล', 'images/gundam.jpg')
    ]
    
    c.executemany('''
        INSERT INTO products (name, description, price, stock, category, image_url)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', products_to_add)
    
    print(f"เพิ่มสินค้า {len(products_to_add)} รายการสำเร็จ!")
    conn.commit()
    
except sqlite3.Error as e:
    print(f"เกิดข้อผิดพลาดตอนเพิ่มข้อมูล: {e}")
finally:
    conn.close()
    print("ปิดการเชื่อมต่อ")