import sqlite3
import os
from datetime import datetime, timedelta # 👈 1. Import timedelta

class Database:
    def __init__(self, db_name=r'M:\doll_shop\dollshop\dollieshop.db'):
        """เชื่อมต่อกับฐานข้อมูล SQLite"""
        self.db_name = db_name
        self.conn = None
        
        # ตรวจสอบและสร้าง database ถ้ายังไม่มี
        if not os.path.exists(self.db_name):
            print(f"สร้างฐานข้อมูลใหม่: {self.db_name}")
            self.create_tables()
            self.insert_sample_data()
        else:
            print(f"ใช้ฐานข้อมูลที่มีอยู่: {self.db_name}")
            # (สำคัญ) เรียก create_tables() เสมอ เพื่อให้มันตรวจสอบ
            # และอัปเดตโครงสร้างตาราง (เช่น เพิ่มคอลัมน์) ให้อัตโนมัติ
            self.create_tables()

    def connect(self):
        """เปิดการเชื่อมต่อกับฐานข้อมูล"""
        try:
            self.conn = sqlite3.connect(self.db_name)
            self.conn.row_factory = sqlite3.Row
            self.conn.execute("PRAGMA foreign_keys = ON;")
            return self.conn.cursor()
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาดในการเชื่อมต่อ: {e}")
            return None

    def close(self):
        """ปิดการเชื่อมต่อกับฐานข้อมูล"""
        if self.conn:
            self.conn.commit()
            self.conn.close()
            self.conn = None

    def create_tables(self):
        """สร้างตารางทั้งหมดในฐานข้อมูล (และอัปเดตถ้าจำเป็น)"""
        cursor = self.connect()
        if not cursor:
            return
        
        try:
            # --- ตารางผู้ใช้ ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT UNIQUE NOT NULL,
                    password TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    full_name TEXT NOT NULL,
                    phone TEXT,
                    address TEXT,
                    profile_image_url TEXT,
                    role TEXT DEFAULT 'customer',
                    created_at TIMESTAMP 
                )
            ''')
            
            # --- ตารางสินค้า ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0,
                    category TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP
                )
            ''')
            
            # --- ตารางคำสั่งซื้อ (Snapshot ผู้ซื้อ) ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    buyer_name TEXT,        -- Snapshot
                    buyer_phone TEXT,       -- Snapshot
                    buyer_address TEXT,     -- Snapshot
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    shipping_address TEXT,  -- Legacy (เก็บไว้เผื่อ)
                    slip_image_url TEXT,
                    created_at TIMESTAMP,   -- (เวลาไทย)
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
                )
            ''')
            
            # --- ตารางรายการสินค้า (Snapshot สินค้า) ---
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    
                    product_name TEXT,    -- Snapshot: ชื่อสินค้า
                    price_per_unit REAL,  -- Snapshot: ราคา
                    
                    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE SET NULL
                )
            ''')
            
            print("สร้างตารางทั้งหมดสำเร็จ (หรือมีอยู่แล้ว)")
            
            # --- (สำคัญ!) อัปเดตโครงสร้างตารางเก่าอัตโนมัติ ---
            print("กำลังตรวจสอบและอัปเดตคอลัมน์ (ALTER TABLE)...")
            
            # 1. เพิ่มคอลัมน์ 'product_name' (ถ้ายังไม่มี)
            self.add_column_if_not_exists(cursor, 'order_items', 'product_name', 'TEXT')
            
            # 2. เพิ่มคอลัมน์ 'price_per_unit' (ถ้ายังไม่มี)
            self.add_column_if_not_exists(cursor, 'order_items', 'price_per_unit', 'REAL')
            
            # 3. (สำคัญ) เปลี่ยนชื่อ 'price' (เก่า) -> 'price_per_unit' (ใหม่)
            self.rename_column_if_exists(cursor, 'order_items', 'price', 'price_per_unit')
            
            print("ตรวจสอบคอลัมน์เสร็จสิ้น")

        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
        finally:
            self.close()

    def add_column_if_not_exists(self, cursor, table_name, column_name, column_type):
        """Helper: ช่วยเพิ่มคอลัมน์ถ้ายังไม่มี (กัน Error)"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            if column_name not in columns:
                cursor.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}")
                print(f"  -> (สำเร็จ) เพิ่มคอลัมน์ {column_name} ในตาราง {table_name}")
        except sqlite3.Error as e:
            print(f"  -> (ไม่สำเร็จ) ไม่สามารถเพิ่มคอลัมน์ {column_name}: {e}")

    # --- 🛠️ (เพิ่มใหม่) ฟังก์ชันเปลี่ยนชื่อคอลัมน์ ---
    def rename_column_if_exists(self, cursor, table_name, old_name, new_name):
        """Helper: ช่วยเปลี่ยนชื่อคอลัมน์ price -> price_per_unit (กัน Error)"""
        try:
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = [info[1] for info in cursor.fetchall()]
            if old_name in columns and new_name not in columns:
                cursor.execute(f"ALTER TABLE {table_name} RENAME COLUMN {old_name} TO {new_name}")
                print(f"  -> (สำเร็จ) เปลี่ยนชื่อคอลัมน์ {old_name} เป็น {new_name}")
        except sqlite3.Error as e:
            # (อาจจะ Error ถ้าคอลัมน์ new_name มีอยู่แล้ว แต่ไม่เป็นไร)
            print(f"  -> (ข้อสังเกต) ไม่สามารถเปลี่ยนชื่อคอลัมน์ {old_name}: {e}")

    def insert_sample_data(self):
        """เพิ่มข้อมูลตัวอย่าง (admin และ customer)"""
        cursor = self.connect()
        if not cursor:
            return
        
        try:
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                # --- 🛠️ (แก้ไข) จัดรูปแบบเวลา ---
                thai_time_str = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
                users = [
                    ('admin', 'admin', 'admin@shop.com', 'Admin User', '0800000000', '123 Shop St.', None, 'admin', thai_time_str),
                    ('customer', '123456', 'customer@email.com', 'Customer Name', '0811111111', '456 User Ave.', None, 'customer', thai_time_str)
                ]
                cursor.executemany(
                    'INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url, role, created_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                    users
                )
                print("เพิ่มข้อมูลผู้ใช้ตัวอย่างสำเร็จ")
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาดในการเพิ่มข้อมูล: {e}")
        finally:
            self.close()

    # ========== ฟังก์ชันจัดการผู้ใช้ ==========
    
    def authenticate_user(self, username, password):
        """ตรวจสอบการเข้าสู่ระบบ"""
        user = self.get_user(username)
        if user and user.get('password') == password:
            return user
        return None

    def create_user(self, username, password, email, full_name, phone="", address="", profile_image_url=None):
        """สร้างผู้ใช้ใหม่ (ใช้เวลาไทย)"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            # --- 🛠️ (แก้ไข) จัดรูปแบบเวลา ---
            thai_time_str = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, email, full_name, phone, address, profile_image_url, thai_time_str))
            user_id = cursor.lastrowid
            return user_id
        except sqlite3.IntegrityError:
            print(f"ชื่อผู้ใช้หรืออีเมลซ้ำ: {username}")
            return None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def get_user(self, username):
        """ดึงข้อมูลผู้ใช้จากชื่อผู้ใช้"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def get_user_by_id(self, user_id):
        """ดึงข้อมูลผู้ใช้จาก ID"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
            user = cursor.fetchone()
            return dict(user) if user else None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def update_user_profile(self, user_id, full_name, phone, address, profile_image_url):
        """อัปเดตข้อมูลโปรไฟล์"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute('''
                UPDATE users 
                SET full_name = ?, phone = ?, address = ?, profile_image_url = ? 
                WHERE user_id = ?
            ''', (full_name, phone, address, profile_image_url, user_id))
            return True
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    def update_user_password(self, user_id, new_password):
        """เปลี่ยนรหัสผ่าน"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (new_password, user_id))
            return True
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    # ========== ฟังก์ชันจัดการสินค้า ==========
    
    def get_all_products(self, category=None, search_term=None, limit=None):
        """ดึงข้อมูลสินค้าทั้งหมด"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = "SELECT * FROM products WHERE 1=1"
            params = []
            
            if category:
                query += " AND category = ?"
                params.append(category)
            
            if search_term:
                query += " AND name LIKE ?"
                params.append(f"%{search_term}%")
            
            query += " ORDER BY created_at DESC"
            
            if limit:
                query += " LIMIT ?"
                params.append(limit)
            
            cursor.execute(query, params)
            products = cursor.fetchall()
            return [dict(p) for p in products]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_product_by_id(self, product_id):
        """ดึงข้อมูลสินค้าจาก ID"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
            product = cursor.fetchone()
            return dict(product) if product else None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def create_product(self, name, description, price, stock, category, image_url=''):
        """สร้างสินค้าใหม่ (ใช้เวลาไทย)"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            # --- 🛠️ (แก้ไข) จัดรูปแบบเวลา ---
            thai_time_str = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            cursor.execute('''
                INSERT INTO products (name, description, price, stock, category, image_url, created_at) 
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (name, description, price, stock, category, image_url, thai_time_str))
            product_id = cursor.lastrowid
            return product_id
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def update_product(self, product_id, name, description, price, stock, category, image_url):
        """อัปเดตข้อมูลสินค้า"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute('''
                UPDATE products 
                SET name = ?, description = ?, price = ?, stock = ?, category = ?, image_url = ? 
                WHERE product_id = ?
            ''', (name, description, price, stock, category, image_url, product_id))
            return True
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    def delete_product(self, product_id):
        """ลบสินค้า"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            return True
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    # ========== ฟังก์ชันอื่นๆ ==========
    
    def get_categories(self):
        """ดึงหมวดหมู่สินค้าทั้งหมด"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL AND category != ''")
            categories = cursor.fetchall()
            return [row[0] for row in categories]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    # --- 🛠️ (ฟังก์ชัน create_order ฉบับ Snapshot + เวลาไทย) ---
    def create_order(self, user_id, total_amount, items, payment_method, 
                     shipping_address, slip_image_filename=None,
                     buyer_name=None, buyer_phone=None, buyer_address=None):
        """สร้างคำสั่งซื้อใหม่ (พร้อม Snapshot)"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            
            # 1. (แก้ไข) เพิ่มเวลาไทย (UTC+7) และจัดรูปแบบ
            thai_time_str = (datetime.utcnow() + timedelta(hours=7)).strftime('%Y-%m-%d %H:%M:%S')
            
            # 2. (แก้ไข) สร้างคำสั่งซื้อ - เพิ่ม created_at
            cursor.execute('''
                INSERT INTO orders (user_id, buyer_name, buyer_phone, buyer_address, 
                                    total_amount, payment_method, shipping_address, slip_image_url,
                                    created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, buyer_name, buyer_phone, buyer_address, 
                  total_amount, payment_method, shipping_address, slip_image_filename,
                  thai_time_str))
            
            order_id = cursor.lastrowid
            
            # 3. เพิ่มรายการสินค้า (พร้อม Snapshot)
            for item in items:
                cursor.execute("SELECT stock, name, price FROM products WHERE product_id = ?", 
                             (item.product.product_id,))
                product_data = cursor.fetchone()
                
                if not product_data or product_data['stock'] < item.quantity:
                    conn.rollback()
                    print(f"สินค้า ID {item.product.product_id} สต็อกไม่พอ")
                    return None
                
                snapshot_name = product_data['name']
                snapshot_price = product_data['price']
                
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price_per_unit, product_name) 
                    VALUES (?, ?, ?, ?, ?)
                ''', (order_id, item.product.product_id, item.quantity, snapshot_price, snapshot_name))
                
                cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE product_id = ?
                ''', (item.quantity, item.product.product_id))
            
            conn.commit()
            return order_id
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (create_order): {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    # --- 🛠️ (แก้ไข) ฟังก์ชัน get_user_orders (เรียงตาม ID) ---
    def get_user_orders(self, user_id):
        """ดึงคำสั่งซื้อของผู้ใช้ (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, 
                       GROUP_CONCAT(oi.product_name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                WHERE o.user_id = ? 
                GROUP BY o.order_id 
                ORDER BY o.order_id DESC 
            ''', (user_id,))
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_user_orders): {e}")
            return []
        finally:
            self.close()

    # --- 🛠️ (แก้ไข) ฟังก์ชัน get_all_orders (เรียงตาม ID) ---
    def get_all_orders(self):
        """ดึงคำสั่งซื้อทั้งหมด (สำหรับ Admin) (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, 
                       o.buyer_name as full_name, -- (ส่ง 'buyer_name' ในชื่อ 'full_name')
                       GROUP_CONCAT(oi.product_name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                GROUP BY o.order_id 
                ORDER BY o.order_id DESC
            ''')
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_all_orders): {e}")
            return []
        finally:
            self.close()

    def update_order_status(self, order_id, new_status):
        """อัปเดตสถานะคำสั่งซื้อ"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", 
                         (new_status, order_id))
            return True
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    # --- 🛠️ (ฟังก์ชัน get_order_details ฉบับ Snapshot) ---
    def get_order_details(self, order_id):
        """ดึงรายละเอียดคำสั่งซื้อ (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute('''
                SELECT o.*, 
                       o.buyer_name as full_name, -- (ส่ง 'buyer_name' ในชื่อ 'full_name')
                       o.buyer_phone as phone,    -- (ส่ง 'buyer_phone' ในชื่อ 'phone')
                       GROUP_CONCAT(oi.product_name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                WHERE o.order_id = ? 
                GROUP BY o.order_id
            ''', (order_id,))
            order = cursor.fetchone()
            return dict(order) if order else None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_order_details): {e}")
            return None
        finally:
            self.close()

    # --- 🛠️ (ฟังก์ชัน get_order_items ฉบับ Snapshot) ---
    def get_order_items(self, order_id):
        """ดึงรายการสินค้าในคำสั่งซื้อ (สำหรับพิมพ์ใบเสร็จ) (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT 
                    oi.order_item_id,
                    oi.order_id,
                    oi.product_id,
                    oi.quantity,
                    oi.product_name as name,        -- (Snapshot)
                    oi.price_per_unit as price,     -- (Snapshot)
                    p.image_url
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
            ''', (order_id,))
            items = cursor.fetchall()
            return [dict(item) for item in items]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_order_items): {e}")
            return []
        finally:
            self.close()

    # ========== ฟังก์ชันสำหรับ Dashboard และรายงาน ==========
    
    # --- 🛠️ (แก้ไข) เปลี่ยน DATE() เป็น STRFTIME ---
    def get_daily_sales_summary(self, date_str):
        """ดึงยอดขายรายวัน"""
        cursor = self.connect()
        if not cursor:
            return (0, 0.0)
        
        try:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM orders 
                WHERE STRFTIME('%Y-%m-%d', created_at) = ? AND status != 'cancelled'
            """, (date_str,))
            result = cursor.fetchone()
            total_orders = result[0] if result else 0
            total_revenue = result[1] if result else 0.0
            return total_orders, total_revenue
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return (0, 0.0)
        finally:
            self.close()

    # --- 🛠️ (แก้ไข) เปลี่ยน DATE() เป็น STRFTIME และเรียงตาม ID ---
    def get_orders_for_date(self, date_str):
        """ดึงรายการคำสั่งซื้อในวันที่กำหนด (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, 
                       o.buyer_name as full_name,
                       GROUP_CONCAT(oi.product_name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                WHERE STRFTIME('%Y-%m-%d', o.created_at) = ? 
                GROUP BY o.order_id 
                ORDER BY o.order_id DESC
            ''', (date_str,))
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()
            
    def get_sales_by_period(self, period):
        """
        ดึงข้อมูลยอดขายรวมตามช่วงเวลา
        period สามารถเป็น: 'day', 'month', 'year'
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            if period == 'day':
                date_format = '%Y-%m-%d'
            elif period == 'month':
                date_format = '%Y-%m'
            elif period == 'year':
                date_format = '%Y'
            else:
                print("period ต้องเป็น 'day', 'month' หรือ 'year' เท่านั้น")
                return []
                
            query = f'''
                SELECT 
                    STRFTIME('{date_format}', created_at) AS sales_period,
                    COUNT(order_id) AS total_orders,
                    COALESCE(SUM(total_amount), 0) AS total_revenue
                FROM orders
                WHERE status != 'cancelled'
                GROUP BY sales_period
                ORDER BY sales_period DESC
            '''
            
            cursor.execute(query)
            sales_data = cursor.fetchall()
            result = []
            for row in sales_data:
                result.append(dict(row))
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    # ========== ฟังก์ชันสำหรับดูยอดขายตามวันที่เลือก (ใหม่) ==========
    
    # --- 🛠️ (แก้ไข) เปลี่ยน DATE() เป็น STRFTIME ---
    def get_sales_by_date(self, date_str):
        """
        ดึงยอดขายตามวันที่ที่ระบุ
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y-%m-%d', created_at) as sale_date,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_revenue
                FROM orders
                WHERE STRFTIME('%Y-%m-%d', created_at) = ? 
                  AND status != 'cancelled'
                GROUP BY STRFTIME('%Y-%m-%d', created_at)
            """
            
            cursor.execute(query, (date_str,))
            result = cursor.fetchall()
            output = []
            for row in result:
                output.append(dict(row))
            return output
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()
    
    def get_sales_by_month(self, month_str):
        """
        ดึงยอดขายตามเดือน
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y-%m', created_at) as sale_month,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_revenue
                FROM orders
                WHERE STRFTIME('%Y-%m', created_at) = ? 
                  AND status != 'cancelled'
                GROUP BY STRFTIME('%Y-%m', created_at)
            """
            
            cursor.execute(query, (month_str,))
            result = cursor.fetchall()
            output = []
            for row in result:
                output.append(dict(row))
            return output
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()
    
    def get_sales_by_year(self, year_str):
        """
        ดึงยอดขายตามปี
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y', created_at) as sale_year,
                    COUNT(*) as order_count,
                    COALESCE(SUM(total_amount), 0) as total_revenue
                FROM orders
                WHERE STRFTIME('%Y', created_at) = ? 
                  AND status != 'cancelled'
                GROUP BY STRFTIME('%Y', created_at)
            """
            
            cursor.execute(query, (year_str,))
            result = cursor.fetchall()
            output = []
            for row in result:
                output.append(dict(row))
            return output
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_dashboard_stats(self):
        """ดึงสถิติสำหรับ Dashboard"""
        cursor = self.connect()
        if not cursor:
            return {}
        
        stats = {}
        try:
            cursor.execute("SELECT COUNT(*) FROM orders")
            stats['total_orders'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status != 'cancelled'")
            stats['total_revenue'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 10")
            stats['low_stock_count'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
            stats['total_customers'] = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
            stats['pending_orders'] = cursor.fetchone()[0]
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
        finally:
            self.close()
        
        return stats

    def get_all_users(self, role=None):
        """ดึงข้อมูลผู้ใช้ทั้งหมด"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = "SELECT * FROM users"
            params = []
            
            if role:
                query += " WHERE role = ?"
                params.append(role)
            
            query += " ORDER BY user_id ASC"
            
            cursor.execute(query, params)
            users = cursor.fetchall()
            result = []
            for user in users:
                result.append(dict(user))
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def update_user_details_admin(self, user_id, email, full_name, phone, address, role):
        """อัปเดตข้อมูลผู้ใช้ (สำหรับ Admin)"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute('''
                UPDATE users 
                SET email = ?, full_name = ?, phone = ?, address = ?, role = ? 
                WHERE user_id = ?
            ''', (email, full_name, phone, address, role, user_id))
            return True
        except sqlite3.IntegrityError:
            print(f"อีเมลซ้ำ: {email}")
            return False
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    def delete_user(self, user_id):
        """ลบผู้ใช้"""
        cursor = self.connect()
        if not cursor:
            return False
        
        try:
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            return cursor.rowcount > 0
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return False
        finally:
            self.close()

    def get_low_stock_products(self, threshold=10):
        """ดึงสินค้าที่สต็อกต่ำ"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('SELECT * FROM products WHERE stock < ? ORDER BY stock ASC', (threshold,))
            products = cursor.fetchall()
            result = []
            for product in products:
                result.append(dict(product))
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    # --- 🛠️ (แก้ไข) ฟังก์ชัน get_recent_orders (เรียงตาม ID) ---
    def get_recent_orders(self, limit=10):
        """ดึงคำสั่งซื้อล่าสุด (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, 
                       o.buyer_name as full_name
                FROM orders o 
                ORDER BY o.order_id DESC 
                LIMIT ?
            ''', (limit,))
            orders = cursor.fetchall()
            result = []
            for order in orders:
                result.append(dict(order))
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    # --- 🛠️ (ฟังก์ชัน get_top_selling_products ฉบับแก้ไข) ---
    def get_top_selling_products(self, limit=5):
        """ดึงสินค้าขายดี (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT 
                    oi.product_id, 
                    oi.product_name as name, 
                    SUM(oi.quantity) as total_sold, 
                    SUM(oi.quantity * oi.price_per_unit) as total_revenue
                FROM order_items oi
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE o.status != 'cancelled' 
                      AND oi.product_name IS NOT NULL
                      AND oi.price_per_unit IS NOT NULL
                GROUP BY oi.product_id, oi.product_name
                ORDER BY total_sold DESC 
                LIMIT ?
            ''', (limit,))
            products = cursor.fetchall()
            
            result = []
            for product in products:
                result.append(dict(product))
            
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_top_selling_products): {e}")
            return []
        finally:
            self.close()

    # --- 🛠️ (ฟังก์ชัน get_sales_by_category ฉบับ Snapshot) ---
    def get_sales_by_category(self):
        """ดึงยอดขายแยกตามหมวดหมู่ (ใช้ Snapshot)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT 
                    p.category, 
                    SUM(oi.quantity) as total_quantity, 
                    SUM(oi.quantity * oi.price_per_unit) as total_revenue
                FROM products p 
                JOIN order_items oi ON p.product_id = oi.product_id
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE o.status != 'cancelled'
                GROUP BY p.category 
                ORDER BY total_revenue DESC
            ''')
            categories = cursor.fetchall()
            result = []
            for cat in categories:
                if cat['category'] is not None:
                    result.append(dict(cat))
            return result
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()
    
    # --- 🛠️ (แก้ไข) เปลี่ยน DATE() เป็น STRFTIME ---
    def get_items_sold_by_date(self, date_str):
        """
        ดึงจำนวนสินค้าที่ขายได้ตามวันที่
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y-%m-%d', o.created_at) as sale_date,
                    COALESCE(SUM(oi.quantity), 0) as total_items
                FROM orders o
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                WHERE STRFTIME('%Y-%m-%d', o.created_at) = ? 
                  AND o.status != 'cancelled'
                GROUP BY STRFTIME('%Y-%m-%d', o.created_at)
            """
            cursor.execute(query, (date_str,))
            result = cursor.fetchall()
            return [dict(row) for row in result]
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_items_sold_by_date): {e}")
            return []
        finally:
            self.close()

    def get_items_sold_by_month(self, month_str):
        """
        ดึงจำนวนสินค้าที่ขายได้ตามเดือน
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y-%m', o.created_at) as sale_month,
                    COALESCE(SUM(oi.quantity), 0) as total_items
                FROM orders o
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                WHERE STRFTIME('%Y-%m', o.created_at) = ? 
                  AND o.status != 'cancelled'
                GROUP BY STRFTIME('%Y-%m', o.created_at)
            """
            cursor.execute(query, (month_str,))
            result = cursor.fetchall()
            return [dict(row) for row in result]
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_items_sold_by_month): {e}")
            return []
        finally:
            self.close()

    def get_items_sold_by_year(self, year_str):
        """
        ดึงจำนวนสินค้าที่ขายได้ตามปี
        """
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            query = """
                SELECT 
                    STRFTIME('%Y', o.created_at) as sale_year,
                    COALESCE(SUM(oi.quantity), 0) as total_items
                FROM orders o
                LEFT JOIN order_items oi ON o.order_id = oi.order_id
                WHERE STRFTIME('%Y', o.created_at) = ? 
                  AND o.status != 'cancelled'
                GROUP BY STRFTIME('%Y', o.created_at)
            """
            cursor.execute(query, (year_str,))
            result = cursor.fetchall()
            return [dict(row) for row in result]
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด (get_items_sold_by_year): {e}")
            return []
        finally:
            self.close()
    # ### <<< จบส่วนที่เพิ่มใหม่ >>> ###


if __name__ == "__main__":
    print("กำลังเริ่มต้น... สร้างตารางและผู้ใช้ตัวอย่าง (ถ้ายังไม่มี)")
    db = Database()
    print("database.py ทำงานเสร็จสิ้น")