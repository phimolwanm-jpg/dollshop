import sqlite3
import bcrypt
from datetime import datetime

class Database:
    
    def __init__(self, db_name='dollshop.db'):
        self.db_name = db_name
        self.conn = None
        self.create_tables()
        self.insert_sample_data()
    
    def connect(self):
        self.conn = sqlite3.connect(self.db_name)
        # ตั้งค่านี้สำคัญ ทำให้ผลลัพธ์เป็นเหมือน dictionary
        self.conn.row_factory = sqlite3.Row 
        return self.conn.cursor()
    
    def close(self):
        if self.conn:
            self.conn.commit() # บันทึกการเปลี่ยนแปลง
            self.conn.close()  # ปิดการเชื่อมต่อ
    
    # --- ส่วนสร้างตาราง (create_tables) และ เพิ่มข้อมูลตัวอย่าง (insert_sample_data) ---
    # --- โค้ดส่วนนี้เหมือนเดิม เพราะเป็นการตั้งค่าพื้นฐาน ---
    def create_tables(self):
        cursor = self.connect()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT, username TEXT UNIQUE NOT NULL, password BLOB NOT NULL, 
                email TEXT UNIQUE NOT NULL, full_name TEXT NOT NULL, phone TEXT, address TEXT,
                role TEXT DEFAULT 'customer', created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT,
                price REAL NOT NULL, stock INTEGER DEFAULT 0, category TEXT, image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER, total_amount REAL NOT NULL,
                status TEXT DEFAULT 'pending', payment_method TEXT, shipping_address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP, FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS order_items (
                order_item_id INTEGER PRIMARY KEY AUTOINCREMENT, order_id INTEGER, product_id INTEGER,
                quantity INTEGER, price REAL, FOREIGN KEY (order_id) REFERENCES orders (order_id),
                FOREIGN KEY (product_id) REFERENCES products (product_id)
            )
        ''')
        self.close()

    def insert_sample_data(self):
        cursor = self.connect()
        # เช็คว่าตาราง users ว่างหรือไม่
        cursor.execute("SELECT COUNT(*) FROM users")
        count_result = cursor.fetchone()
        if count_result[0] == 0:
            # เข้ารหัสรหัสผ่านตัวอย่าง
            hashed_admin_pw = bcrypt.hashpw('admin'.encode('utf-8'), bcrypt.gensalt())
            hashed_customer_pw = bcrypt.hashpw('123456'.encode('utf-8'), bcrypt.gensalt())
            users = [
                ('admin', hashed_admin_pw, 'admin@shop.com', 'Admin User', '0800000000', '123 Shop St. 10110', 'admin'),
                ('customer', hashed_customer_pw, 'customer@email.com', 'Customer Name', '0811111111', '456 User Ave. 10220', 'customer')
            ]
            # เพิ่มข้อมูลหลายแถวพร้อมกัน
            cursor.executemany('INSERT INTO users (username, password, email, full_name, phone, address, role) VALUES (?, ?, ?, ?, ?, ?, ?)', users)
        self.close()

    # --- ส่วนจัดการผู้ใช้ (User Management) ---
    # --- โค้ดส่วนนี้เหมือนเดิม เพราะค่อนข้างตรงไปตรงมา ---
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        # เช็คว่าเจอ user และรหัสผ่านตรงกันหรือไม่ (ใช้ bcrypt)
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password']):
            return user
        return None

    def create_user(self, username, password, email, full_name, phone="", address=""):
        try:
            # เข้ารหัสรหัสผ่านก่อนเก็บ
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            cursor = self.connect()
            cursor.execute('INSERT INTO users (username, password, email, full_name, phone, address) VALUES (?, ?, ?, ?, ?, ?)', 
                           (username, hashed_password, email, full_name, phone, address))
            user_id = cursor.lastrowid # เอา ID ของ user ที่เพิ่งสร้าง
            self.close()
            return user_id
        except sqlite3.IntegrityError: # ดักจับ error ถ้า username หรือ email ซ้ำ
            self.close()
            return None # คืนค่า None ถ้าสมัครไม่สำเร็จ
            
    def register_user(self, username, password, email, full_name, phone='', address=''):
        """สมัครสมาชิกใหม่ (เรียกใช้ create_user อีกที)"""
        return self.create_user(username, password, email, full_name, phone, address)

    def get_user(self, username):
        cursor = self.connect()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone() # เอาแค่แถวแรกที่เจอ
        self.close()
        # แปลงผลลัพธ์เป็น dictionary ถ้าเจอข้อมูล
        if user:
            return dict(user) 
        else:
            return None
            
    def get_user_by_id(self, user_id):
        cursor = self.connect()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        self.close()
        if user:
            return dict(user)
        else:
            return None
            
    def update_user_profile(self, user_id, full_name, phone, address):
        try:
            cursor = self.connect()
            cursor.execute("UPDATE users SET full_name = ?, phone = ?, address = ? WHERE user_id = ?",
                           (full_name, phone, address, user_id))
            self.close()
            return True # คืนค่า True ถ้าสำเร็จ
        except Exception as e:
            print(f"Database error updating profile: {e}")
            self.close() # อย่าลืม close แม้จะเกิด error
            return False # คืนค่า False ถ้าไม่สำเร็จ

    def update_user_password(self, user_id, new_password):
        try:
            # เข้ารหัสรหัสผ่านใหม่
            hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt())
            cursor = self.connect()
            cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (hashed_password, user_id))
            self.close()
            return True
        except Exception as e:
            print(f"Database error updating password: {e}")
            self.close()
            return False

    # --- ส่วนจัดการสินค้า (Product Management) ---
    # --- โค้ดส่วนนี้เหมือนเดิม เพราะค่อนข้างตรงไปตรงมา ---
    def get_product_by_id(self, product_id):
        cursor = self.connect()
        cursor.execute("SELECT * FROM products WHERE product_id = ?", (product_id,))
        product = cursor.fetchone()
        self.close()
        if product:
            return dict(product)
        else:
            return None

    def create_product(self, name, description, price, stock, category, image_url=''):
        try:
            cursor = self.connect()
            cursor.execute('''
                INSERT INTO products (name, description, price, stock, category, image_url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, price, stock, category, image_url))
            product_id = cursor.lastrowid
            self.close()
            return product_id
        except Exception as e:
            print(f"Database error creating product: {e}")
            self.close()
            return None

    def update_product(self, product_id, name, description, price, stock, category, image_url):
        try:
            cursor = self.connect()
            cursor.execute('''
                UPDATE products 
                SET name = ?, description = ?, price = ?, stock = ?, category = ?, image_url = ?
                WHERE product_id = ?
            ''', (name, description, price, stock, category, image_url, product_id))
            self.close()
            return True
        except Exception as e:
            print(f"Database error updating product: {e}")
            self.close()
            return False

    def delete_product(self, product_id):
        try:
            cursor = self.connect()
            cursor.execute("DELETE FROM products WHERE product_id = ?", (product_id,))
            self.close()
            return True
        except Exception as e:
            print(f"Database error deleting product: {e}")
            self.close()
            return False
            
    # --- ส่วนดึงข้อมูลสินค้า/หมวดหมู่ (ปรับสไตล์) ---
    def get_all_products(self, category=None, search_term=None, limit=None):
        cursor = self.connect()
        query = "SELECT * FROM products WHERE 1=1"
        params = []

        if category:
           query += " AND category = ?"
           params.append(category)
    
        if search_term:
           # ใช้ LIKE เพื่อค้นหาบางส่วนของชื่อ
           query += " AND name LIKE ?" 
           params.append(f"%{search_term}%") # ใส่ % หน้าหลังคำค้น

        query += " ORDER BY created_at DESC" # เรียงจากใหม่ไปเก่า

        if limit:
           query += " LIMIT ?"
           params.append(limit)

        cursor.execute(query, params)
        products_results = cursor.fetchall() # ดึงข้อมูลทั้งหมดที่เจอ
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        product_list = []
        for p in products_results:
            product_list.append(dict(p)) # แปลงแต่ละแถวเป็น dict แล้วเพิ่ม
        return product_list

    def get_categories(self):
        cursor = self.connect()
        # ใช้ DISTINCT เพื่อเอาหมวดหมู่ที่ไม่ซ้ำ
        cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL") 
        categories_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        category_list = []
        for row in categories_results:
            category_list.append(row[0]) # ดึงค่าจากคอลัมน์แรก
        return category_list

    # --- ส่วนจัดการคำสั่งซื้อ (Order Management) ---
    def create_order(self, user_id, total_amount, items, payment_method, shipping_address):
        # ใช้ try...except เพื่อจัดการ Transaction
        try:
            cursor = self.connect()
            # 1. สร้าง order หลัก
            cursor.execute('INSERT INTO orders (user_id, total_amount, payment_method, shipping_address) VALUES (?, ?, ?, ?)', 
                           (user_id, total_amount, payment_method, shipping_address))
            order_id = cursor.lastrowid # เอา ID ของ order ที่เพิ่งสร้าง

            # 2. เพิ่มรายการสินค้า (order_items) และตัดสต็อก
            for item in items: # วนลูปสินค้าในตะกร้า
                cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)', 
                               (order_id, item.product.product_id, item.quantity, item.product.price))
                # ตัดสต็อกสินค้า
                cursor.execute('UPDATE products SET stock = stock - ? WHERE product_id = ?', 
                               (item.quantity, item.product.product_id))
                               
            self.close() # commit การเปลี่ยนแปลงทั้งหมด
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            if self.conn: 
                self.conn.rollback() # ถ้ามี error ให้ยกเลิกทั้งหมด
            self.close() # ปิด connection แม้จะ error
            return None # คืนค่า None ถ้าสร้าง order ไม่สำเร็จ

    def get_user_orders(self, user_id):
        cursor = self.connect()
        # ใช้ JOIN และ GROUP_CONCAT เพื่อรวมข้อมูล
        cursor.execute('''
            SELECT o.*, GROUP_CONCAT(p.name || ' x' || oi.quantity) as items
            FROM orders o
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.user_id = ?
            GROUP BY o.order_id ORDER BY o.created_at DESC
        ''', (user_id,))
        orders_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list

    def get_all_orders(self):
        cursor = self.connect()
        cursor.execute('''
            SELECT o.*, u.username, u.full_name,
                   GROUP_CONCAT(p.name || ' x' || oi.quantity) as items
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            GROUP BY o.order_id
            ORDER BY o.created_at DESC
        ''')
        orders_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list
        
    def get_order_details(self, order_id):
        cursor = self.connect()
        cursor.execute('''
            SELECT o.*, u.username, u.full_name,
                   GROUP_CONCAT(p.name || ' x' || oi.quantity) as items
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            LEFT JOIN order_items oi ON o.order_id = oi.order_id
            LEFT JOIN products p ON oi.product_id = p.product_id
            WHERE o.order_id = ?
            GROUP BY o.order_id
        ''', (order_id,))
        order = cursor.fetchone()
        self.close()
        if order:
            return dict(order)
        else:
            return None

    def update_order_status(self, order_id, new_status):
        try:
            cursor = self.connect()
            cursor.execute("UPDATE orders SET status = ? WHERE order_id = ?", (new_status, order_id))
            self.close()
            return True
        except Exception as e:
            print(f"Database error updating status: {e}")
            self.close()
            return False

    # --- ส่วน Dashboard Stats (โค้ดเหมือนเดิม เพราะตรงไปตรงมา) ---
    def get_dashboard_stats(self):
        cursor = self.connect()
        
        cursor.execute("SELECT COUNT(*) FROM orders")
        total_orders = cursor.fetchone()[0]
        
        cursor.execute("SELECT COALESCE(SUM(total_amount), 0) FROM orders WHERE status != 'cancelled'")
        total_revenue = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products")
        total_products = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM products WHERE stock < 10")
        low_stock_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'customer'")
        total_customers = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM orders WHERE status = 'pending'")
        pending_orders = cursor.fetchone()[0]
        
        self.close()
        
        return {
            'total_orders': total_orders,
            'total_revenue': total_revenue,
            'total_products': total_products,
            'low_stock_count': low_stock_count, # แก้ชื่อ key ให้สื่อความหมาย
            'total_customers': total_customers,
            'pending_orders': pending_orders
        }
    
    # --- ส่วนดึงข้อมูลอื่นๆ (ปรับสไตล์) ---
    def get_top_selling_products(self, limit=5):
        cursor = self.connect()
        cursor.execute('''
            SELECT p.product_id, p.name, p.category, p.price, p.image_url,
                   SUM(oi.quantity) as total_sold,
                   SUM(oi.quantity * oi.price) as total_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id
            ORDER BY total_sold DESC
            LIMIT ?
        ''', (limit,))
        products_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        product_list = []
        for p in products_results:
            product_list.append(dict(p))
        return product_list
    
    def get_low_stock_products(self, threshold=10):
        cursor = self.connect()
        cursor.execute('''
            SELECT * FROM products 
            WHERE stock < ? 
            ORDER BY stock ASC
        ''', (threshold,))
        products_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        product_list = []
        for p in products_results:
            product_list.append(dict(p))
        return product_list
    
    def get_recent_orders(self, limit=10):
        cursor = self.connect()
        cursor.execute('''
            SELECT o.*, u.username, u.full_name
            FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC
            LIMIT ?
        ''', (limit,))
        orders_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list
    
    def get_sales_by_category(self):
        cursor = self.connect()
        cursor.execute('''
            SELECT p.category, 
                   SUM(oi.quantity) as total_quantity,
                   SUM(oi.quantity * oi.price) as total_revenue
            FROM products p
            JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.category
            ORDER BY total_revenue DESC
        ''')
        categories_results = cursor.fetchall()
        self.close()
        
        # --- เปลี่ยนเป็น For Loop ---
        category_list = []
        for c in categories_results:
            category_list.append(dict(c))
        return category_list