# M:/doll_shop/database.py (Updated for profile picture)

import sqlite3
# --- ลบ import bcrypt ถ้าใช้เวอร์ชัน plain text ---
# import bcrypt
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
    def create_tables(self):
        cursor = self.connect()
        # --- vvvv แก้ไขตาราง users เพิ่ม profile_image_url vvvv ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL, -- Assuming plain text
                email TEXT UNIQUE NOT NULL,
                full_name TEXT NOT NULL,
                phone TEXT,
                address TEXT,
                profile_image_url TEXT, -- <--- เพิ่มคอลัมน์นี้
                role TEXT DEFAULT 'customer',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        # --- ^^^^ สิ้นสุดการแก้ไข ^^^^ ---
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS products (
                product_id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, description TEXT,
                price REAL NOT NULL, stock INTEGER DEFAULT 0, category TEXT, image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders (
                order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                buyer_name TEXT, buyer_phone TEXT, buyer_address TEXT,
                total_amount REAL NOT NULL, status TEXT DEFAULT 'pending', payment_method TEXT,
                shipping_address TEXT, slip_image_url TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
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
        cursor.execute("SELECT COUNT(*) FROM users")
        count_result = cursor.fetchone()
        if count_result[0] == 0:
            plain_admin_pw = 'admin'
            plain_customer_pw = '123456'
            # --- vvvv เพิ่มค่า NULL สำหรับ profile_image_url vvvv ---
            users = [
                ('admin', plain_admin_pw, 'admin@shop.com', 'Admin User', '0800000000', '123 Shop St. 10110', None, 'admin'), # เพิ่ม None
                ('customer', plain_customer_pw, 'customer@email.com', 'Customer Name', '0811111111', '456 User Ave. 10220', None, 'customer') # เพิ่ม None
            ]
            # --- ^^^^ แก้ไข SQL INSERT ให้รองรับคอลัมน์ใหม่ ^^^^ ---
            cursor.executemany('INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)', users)
        self.close()

    # --- ส่วนจัดการผู้ใช้ (User Management) ---
    def authenticate_user(self, username, password):
        user = self.get_user(username)
        # Assuming plain text password check
        if user and user['password'] == password:
            return user
        return None

    # --- vvvv แก้ไข create_user เพิ่ม profile_image_url vvvv ---
    def create_user(self, username, password, email, full_name, phone="", address="", profile_image_url=None):
        try:
            plain_password = password
            cursor = self.connect()
            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, plain_password, email, full_name, phone, address, profile_image_url)) # เพิ่ม profile_image_url
            user_id = cursor.lastrowid
            self.close()
            return user_id
        except sqlite3.IntegrityError:
            self.close()
            return None
    # --- ^^^^ แก้ไข create_user ^^^^ ---

    def register_user(self, username, password, email, full_name, phone='', address=''):
        # ตอนสมัครครั้งแรก ยังไม่มีรูป
        return self.create_user(username, password, email, full_name, phone, address, profile_image_url=None)

    # --- vvvv แก้ไข get_user และ get_user_by_id ให้ SELECT * vvvv ---
    def get_user(self, username):
        cursor = self.connect()
        cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
        user = cursor.fetchone()
        self.close()
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
    # --- ^^^^ แก้ไข get_user และ get_user_by_id ^^^^ ---

    # --- vvvv แก้ไข update_user_profile เพิ่ม profile_image_url vvvv ---
    def update_user_profile(self, user_id, full_name, phone, address, profile_image_url):
        try:
            cursor = self.connect()
            cursor.execute('''
                UPDATE users
                SET full_name = ?, phone = ?, address = ?, profile_image_url = ?
                WHERE user_id = ?
            ''', (full_name, phone, address, profile_image_url, user_id)) # เพิ่ม profile_image_url
            self.close()
            return True
        except Exception as e:
            print(f"Database error updating profile: {e}")
            self.close()
            return False
    # --- ^^^^ แก้ไข update_user_profile ^^^^ ---

    def update_user_password(self, user_id, new_password):
        try:
            plain_new_password = new_password
            cursor = self.connect()
            cursor.execute("UPDATE users SET password = ? WHERE user_id = ?", (plain_new_password, user_id))
            self.close()
            return True
        except Exception as e:
            print(f"Database error updating password: {e}")
            self.close()
            return False

    # --- ฟังก์ชันใหม่ สำหรับ Admin จัดการ User ---
    def get_all_users(self, role=None):
        cursor = self.connect()
        # --- Select * to get all columns including profile_image_url ---
        query = "SELECT * FROM users"
        params = []
        if role:
            query += " WHERE role = ?"
            params.append(role)
        query += " ORDER BY user_id ASC"

        cursor.execute(query, params)
        users_results = cursor.fetchall()
        self.close()
        user_list = []
        for u in users_results:
            user_list.append(dict(u))
        return user_list

    def update_user_details_admin(self, user_id, email, full_name, phone, address, role):
        try:
            cursor = self.connect()
            cursor.execute('''
                UPDATE users
                SET email = ?, full_name = ?, phone = ?, address = ?, role = ?
                WHERE user_id = ?
            ''', (email, full_name, phone, address, role, user_id))
            self.close()
            return True
        except sqlite3.IntegrityError:
             print(f"Database error updating user {user_id}: Email may already exist.")
             self.close()
             return False
        except Exception as e:
            print(f"Database error updating user {user_id}: {e}")
            self.close()
            return False

    def delete_user(self, user_id):
        try:
            cursor = self.connect()
            cursor.execute("DELETE FROM users WHERE user_id = ?", (user_id,))
            deleted_rows = cursor.rowcount
            self.close()
            return deleted_rows > 0
        except sqlite3.IntegrityError as ie:
             print(f"Database integrity error deleting user {user_id}: {ie}")
             self.close()
             return False
        except Exception as e:
            print(f"Database error deleting user {user_id}: {e}")
            self.close()
            return False

    # --- ส่วนจัดการ Product, Order, Stats, Getters (get_all_products etc.) เหมือนเดิม ---
    # ... (โค้ดส่วนที่เหลือ ไม่มีการเปลี่ยนแปลง) ...
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

    def get_all_products(self, category=None, search_term=None, limit=None):
        cursor = self.connect()
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
        products_results = cursor.fetchall()
        self.close()
        product_list = []
        for p in products_results:
            product_list.append(dict(p))
        return product_list

    def get_categories(self):
        cursor = self.connect()
        cursor.execute("SELECT DISTINCT category FROM products WHERE category IS NOT NULL")
        categories_results = cursor.fetchall()
        self.close()
        category_list = []
        for row in categories_results:
            category_list.append(row[0])
        return category_list

    def create_order(self, user_id, total_amount, items, payment_method,
                     shipping_address, slip_image_filename=None,
                     buyer_name=None, buyer_phone=None, buyer_address=None):
        try:
            cursor = self.connect()
            cursor.execute('''
                INSERT INTO orders (
                    user_id, buyer_name, buyer_phone, buyer_address,
                    total_amount, payment_method, shipping_address, slip_image_url
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_id, buyer_name, buyer_phone, buyer_address,
                total_amount, payment_method, shipping_address, slip_image_filename
            ))
            order_id = cursor.lastrowid
            for item in items:
                cursor.execute('INSERT INTO order_items (order_id, product_id, quantity, price) VALUES (?, ?, ?, ?)',
                               (order_id, item.product.product_id, item.quantity, item.product.price))
                cursor.execute('UPDATE products SET stock = stock - ? WHERE product_id = ?',
                               (item.quantity, item.product.product_id))
            self.close()
            return order_id
        except Exception as e:
            print(f"Error creating order: {e}")
            if self.conn:
                self.conn.rollback()
            self.close()
            return None

    def get_user_orders(self, user_id):
        cursor = self.connect()
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
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list

    def get_all_orders(self):
        cursor = self.connect()
        # Fetch buyer info as well if needed in AdminOrdersWindow display
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
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list

    def get_order_details(self, order_id):
        cursor = self.connect()
        # Fetch buyer info for the receipt
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
            'total_orders': total_orders, 'total_revenue': total_revenue,
            'total_products': total_products, 'low_stock_count': low_stock_count,
            'total_customers': total_customers, 'pending_orders': pending_orders
        }

    def get_top_selling_products(self, limit=5):
        cursor = self.connect()
        cursor.execute('''
            SELECT p.product_id, p.name, p.category, p.price, p.image_url,
                   SUM(oi.quantity) as total_sold, SUM(oi.quantity * oi.price) as total_revenue
            FROM products p JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.product_id ORDER BY total_sold DESC LIMIT ?
        ''', (limit,))
        products_results = cursor.fetchall()
        self.close()
        product_list = []
        for p in products_results:
            product_list.append(dict(p))
        return product_list

    def get_low_stock_products(self, threshold=10):
        cursor = self.connect()
        cursor.execute('SELECT * FROM products WHERE stock < ? ORDER BY stock ASC', (threshold,))
        products_results = cursor.fetchall()
        self.close()
        product_list = []
        for p in products_results:
            product_list.append(dict(p))
        return product_list

    def get_recent_orders(self, limit=10):
        cursor = self.connect()
        cursor.execute('''
            SELECT o.*, u.username, u.full_name FROM orders o
            LEFT JOIN users u ON o.user_id = u.user_id
            ORDER BY o.created_at DESC LIMIT ?
        ''', (limit,))
        orders_results = cursor.fetchall()
        self.close()
        order_list = []
        for o in orders_results:
            order_list.append(dict(o))
        return order_list

    def get_sales_by_category(self):
        cursor = self.connect()
        cursor.execute('''
            SELECT p.category, SUM(oi.quantity) as total_quantity, SUM(oi.quantity * oi.price) as total_revenue
            FROM products p JOIN order_items oi ON p.product_id = oi.product_id
            GROUP BY p.category ORDER BY total_revenue DESC
        ''')
        categories_results = cursor.fetchall()
        self.close()
        category_list = []
        for c in categories_results:
            category_list.append(dict(c))
        return category_list