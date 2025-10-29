# database.py (ปรับปรุง - เรียบง่าย)

import sqlite3
import os
from datetime import datetime

class Database:
    def __init__(self, db_name='dollieshop.db'):
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
        """สร้างตารางทั้งหมดในฐานข้อมูล"""
        cursor = self.connect()
        if not cursor:
            return
        
        try:
            # ตารางผู้ใช้
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
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางสินค้า
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS products (
                    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    description TEXT,
                    price REAL NOT NULL,
                    stock INTEGER DEFAULT 0,
                    category TEXT,
                    image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # ตารางคำสั่งซื้อ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS orders (
                    order_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    buyer_name TEXT,
                    buyer_phone TEXT,
                    buyer_address TEXT,
                    total_amount REAL NOT NULL,
                    status TEXT DEFAULT 'pending',
                    payment_method TEXT,
                    shipping_address TEXT,
                    slip_image_url TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id) ON DELETE SET NULL
                )
            ''')
            
            # ตารางรายการสินค้าในคำสั่งซื้อ
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS order_items (
                    order_item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    order_id INTEGER,
                    product_id INTEGER,
                    quantity INTEGER,
                    price REAL,
                    FOREIGN KEY (order_id) REFERENCES orders (order_id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (product_id) ON DELETE SET NULL
                )
            ''')
            
            print("สร้างตารางทั้งหมดสำเร็จ")
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาดในการสร้างตาราง: {e}")
        finally:
            self.close()

    def insert_sample_data(self):
        """เพิ่มข้อมูลตัวอย่าง (admin และ customer)"""
        cursor = self.connect()
        if not cursor:
            return
        
        try:
            # ตรวจสอบว่ามีข้อมูลแล้วหรือยัง
            cursor.execute("SELECT COUNT(*) FROM users")
            if cursor.fetchone()[0] == 0:
                users = [
                    ('admin', 'admin', 'admin@shop.com', 'Admin User', '0800000000', '123 Shop St.', None, 'admin'),
                    ('customer', '123456', 'customer@email.com', 'Customer Name', '0811111111', '456 User Ave.', None, 'customer')
                ]
                cursor.executemany(
                    'INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url, role) VALUES (?, ?, ?, ?, ?, ?, ?, ?)',
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
        """สร้างผู้ใช้ใหม่"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute('''
                INSERT INTO users (username, password, email, full_name, phone, address, profile_image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (username, password, email, full_name, phone, address, profile_image_url))
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
        """สร้างสินค้าใหม่"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
            cursor.execute('''
                INSERT INTO products (name, description, price, stock, category, image_url) 
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, description, price, stock, category, image_url))
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

    def create_order(self, user_id, total_amount, items, payment_method, 
                     shipping_address, slip_image_filename=None,
                     buyer_name=None, buyer_phone=None, buyer_address=None):
        """สร้างคำสั่งซื้อใหม่"""
        conn = None
        try:
            conn = sqlite3.connect(self.db_name)
            conn.row_factory = sqlite3.Row
            conn.execute("PRAGMA foreign_keys = ON;")
            cursor = conn.cursor()
            
            # สร้างคำสั่งซื้อ
            cursor.execute('''
                INSERT INTO orders (user_id, buyer_name, buyer_phone, buyer_address, 
                                    total_amount, payment_method, shipping_address, slip_image_url)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (user_id, buyer_name, buyer_phone, buyer_address, 
                  total_amount, payment_method, shipping_address, slip_image_filename))
            
            order_id = cursor.lastrowid
            
            # เพิ่มรายการสินค้า
            for item in items:
                # ตรวจสอบสต็อก
                cursor.execute("SELECT stock FROM products WHERE product_id = ?", 
                             (item.product.product_id,))
                result = cursor.fetchone()
                
                if not result or result['stock'] < item.quantity:
                    conn.rollback()
                    print(f"สินค้า ID {item.product.product_id} สต็อกไม่พอ")
                    return None
                
                # เพิ่มรายการสินค้าในคำสั่งซื้อ
                cursor.execute('''
                    INSERT INTO order_items (order_id, product_id, quantity, price) 
                    VALUES (?, ?, ?, ?)
                ''', (order_id, item.product.product_id, item.quantity, item.product.price))
                
                # ลดสต็อก
                cursor.execute('''
                    UPDATE products SET stock = stock - ? WHERE product_id = ?
                ''', (item.quantity, item.product.product_id))
            
            conn.commit()
            return order_id
            
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            if conn:
                conn.rollback()
            return None
        finally:
            if conn:
                conn.close()

    def get_user_orders(self, user_id):
        """ดึงคำสั่งซื้อของผู้ใช้"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, GROUP_CONCAT(p.name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE o.user_id = ? 
                GROUP BY o.order_id 
                ORDER BY o.created_at DESC
            ''', (user_id,))
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_all_orders(self):
        """ดึงคำสั่งซื้อทั้งหมด (สำหรับ Admin)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
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
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
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

    def get_order_details(self, order_id):
        """ดึงรายละเอียดคำสั่งซื้อ"""
        cursor = self.connect()
        if not cursor:
            return None
        
        try:
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
            return dict(order) if order else None
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return None
        finally:
            self.close()

    def get_order_items(self, order_id):
        """ดึงรายการสินค้าในคำสั่งซื้อ (สำหรับพิมพ์ใบเสร็จ)"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT oi.*, p.name, p.image_url
                FROM order_items oi
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE oi.order_id = ?
            ''', (order_id,))
            items = cursor.fetchall()
            return [dict(item) for item in items]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    # ========== ฟังก์ชันสำหรับ Dashboard และรายงาน ==========
    
    def get_daily_sales_summary(self, date_str):
        """ดึงยอดขายรายวัน"""
        cursor = self.connect()
        if not cursor:
            return (0, 0.0)
        
        try:
            cursor.execute("""
                SELECT COUNT(*), COALESCE(SUM(total_amount), 0)
                FROM orders 
                WHERE DATE(created_at) = DATE(?) AND status != 'cancelled'
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

    def get_orders_for_date(self, date_str):
        """ดึงรายการคำสั่งซื้อในวันที่กำหนด"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, u.username, u.full_name, 
                       GROUP_CONCAT(p.name || ' x' || oi.quantity) as items
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id
                LEFT JOIN order_items oi ON o.order_id = oi.order_id 
                LEFT JOIN products p ON oi.product_id = p.product_id
                WHERE DATE(o.created_at) = DATE(?) 
                GROUP BY o.order_id 
                ORDER BY o.created_at DESC
            ''', (date_str,))
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
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
            return [dict(u) for u in users]
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
            return [dict(p) for p in products]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_recent_orders(self, limit=10):
        """ดึงคำสั่งซื้อล่าสุด"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT o.*, u.username, u.full_name 
                FROM orders o 
                LEFT JOIN users u ON o.user_id = u.user_id
                ORDER BY o.created_at DESC 
                LIMIT ?
            ''', (limit,))
            orders = cursor.fetchall()
            return [dict(o) for o in orders]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_top_selling_products(self, limit=5):
        """ดึงสินค้าขายดี"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT p.product_id, p.name, p.category, p.price, p.image_url,
                       SUM(oi.quantity) as total_sold, 
                       SUM(oi.quantity * oi.price) as total_revenue
                FROM products p 
                JOIN order_items oi ON p.product_id = oi.product_id
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE o.status != 'cancelled'
                GROUP BY p.product_id 
                ORDER BY total_sold DESC 
                LIMIT ?
            ''', (limit,))
            products = cursor.fetchall()
            return [dict(p) for p in products]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()

    def get_sales_by_category(self):
        """ดึงยอดขายแยกตามหมวดหมู่"""
        cursor = self.connect()
        if not cursor:
            return []
        
        try:
            cursor.execute('''
                SELECT p.category, 
                       SUM(oi.quantity) as total_quantity, 
                       SUM(oi.quantity * oi.price) as total_revenue
                FROM products p 
                JOIN order_items oi ON p.product_id = oi.product_id
                JOIN orders o ON oi.order_id = o.order_id 
                WHERE o.status != 'cancelled'
                GROUP BY p.category 
                ORDER BY total_revenue DESC
            ''')
            categories = cursor.fetchall()
            return [dict(c) for c in categories if c['category'] is not None]
        except sqlite3.Error as e:
            print(f"เกิดข้อผิดพลาด: {e}")
            return []
        finally:
            self.close()