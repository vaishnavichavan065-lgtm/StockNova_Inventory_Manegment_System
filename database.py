import mysql.connector
from mysql.connector import Error, pooling
import hashlib
import time

class Database:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(Database, cls).__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
        self._initialized = True

        self.db_config = {
        "host": "tramway.proxy.rlwy.net",
        "port": 35363,
        "user": "root",
        "password": "PQbzdIHHrAwoEtKeMJfVycWqdgQktlhe",
        "database": "railway"
}
        self.pool = None
        self.connection = None
        self.cursor = None

        
        try:
            self.pool = mysql.connector.pooling.MySQLConnectionPool(
            pool_name="mypool",
            pool_size=5,
            **self.db_config
)
        except Error as e:
            print(f"❌ Pool creation error: {e}")
            self.pool = None
    
    def get_connection(self):
        try:
            if self.pool:
                conn = self.pool.get_connection()
                cursor = conn.cursor(dictionary=True)
                return conn, cursor
            return None, None
        except Error as e:
            print(f"❌ Connection error: {e}")
            return None, None
    
    def close_connection(self, conn, cursor):
        try:
            if cursor:
                cursor.close()
            if conn and conn.is_connected():
                conn.close()
        except:
            pass
    
    def connect(self):
        try:
            if self.pool:
                self.connection = self.pool.get_connection()
                self.cursor = self.connection.cursor(dictionary=True)
                return True
            return False
        except Exception as e:
            print(f"❌ Connect error: {e}")
            return False
    
    def close(self):
        try:
            if self.cursor:
                self.cursor.close()
            if self.connection and self.connection.is_connected():
                self.connection.close()
        except:
            pass
    
    def hash_password(self, password):
        return hashlib.sha256(password.encode()).hexdigest()
    
    # ============================================
    # USER AUTHENTICATION
    # ============================================
    
    def register_user(self, username, email, password, full_name):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
            if cursor.fetchone():
                self.close_connection(conn, cursor)
                return None
            
            cursor.execute("SELECT id FROM users WHERE email = %s", (email,))
            if cursor.fetchone():
                self.close_connection(conn, cursor)
                return None
            
            hashed = self.hash_password(password)
            cursor.execute(
                "INSERT INTO users (username, email, password, full_name) VALUES (%s, %s, %s, %s)",
                (username, email, hashed, full_name)
            )
            conn.commit()
            user_id = cursor.lastrowid
            self.close_connection(conn, cursor)
            return user_id
        except Exception as e:
            print(f"❌ register_user error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def login_user(self, username, password):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            hashed = self.hash_password(password)
            cursor.execute(
                "SELECT * FROM users WHERE username = %s AND password = %s",
                (username, hashed)
            )
            user = cursor.fetchone()
            self.close_connection(conn, cursor)
            return user
        except Exception as e:
            print(f"❌ login_user error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def get_user_by_id(self, user_id):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute(
                "SELECT id, username, email, full_name, profile_photo, employee_id FROM users WHERE id = %s",
                (user_id,)
            )
            user = cursor.fetchone()
            self.close_connection(conn, cursor)
            return user
        except Exception as e:
            print(f"❌ get_user_by_id error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    # ============================================
    # PROFILE
    # ============================================
    
    def update_profile(self, user_id, full_name, email, employee_id):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, email = %s, employee_id = %s 
                WHERE id = %s
            """, (full_name, email, employee_id, user_id))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_profile error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def change_password(self, user_id, current_password, new_password):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            hashed_current = self.hash_password(current_password)
            cursor.execute("SELECT id FROM users WHERE id = %s AND password = %s", (user_id, hashed_current))
            user = cursor.fetchone()
            
            if not user:
                self.close_connection(conn, cursor)
                return False
            
            hashed_new = self.hash_password(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE id = %s", (hashed_new, user_id))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ change_password error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def update_profile_photo(self, user_id, photo_url):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute("UPDATE users SET profile_photo = %s WHERE id = %s", (photo_url, user_id))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_profile_photo error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    # ============================================
    # PRODUCTS
    # ============================================
    
    def get_all_products(self):
        conn, cursor = self.get_connection()
        if not conn:
            return []
        try:
            cursor.execute("SELECT * FROM products ORDER BY id DESC")
            products = cursor.fetchall()
            self.close_connection(conn, cursor)
            return products
        except Exception as e:
            print(f"❌ get_all_products error: {e}")
            self.close_connection(conn, cursor)
            return []
    
    def get_product_by_id(self, product_id):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute("SELECT * FROM products WHERE id = %s", (product_id,))
            product = cursor.fetchone()
            self.close_connection(conn, cursor)
            return product
        except Exception as e:
            print(f"❌ get_product_by_id error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def add_product(self, name, category, quantity, price, supplier_id=0, reorder_level=5, description=''):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute(
                """INSERT INTO products (name, category, quantity, price, supplier_id, reorder_level, description)
                   VALUES (%s, %s, %s, %s, %s, %s, %s)""",
                (name, category, quantity, price, supplier_id, reorder_level, description)
            )
            conn.commit()
            product_id = cursor.lastrowid
            self.close_connection(conn, cursor)
            return product_id
        except Exception as e:
            print(f"❌ add_product error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def update_product(self, product_id, name, category, quantity, price, supplier_id, reorder_level, description):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute(
                """UPDATE products 
                   SET name=%s, category=%s, quantity=%s, price=%s, 
                       supplier_id=%s, reorder_level=%s, description=%s
                   WHERE id=%s""",
                (name, category, quantity, price, supplier_id, reorder_level, description, product_id)
            )
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_product error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def update_stock(self, product_id, quantity):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute(
                "UPDATE products SET quantity = %s WHERE id = %s",
                (quantity, product_id)
            )
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_stock error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def delete_product(self, product_id):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute("DELETE FROM products WHERE id = %s", (product_id,))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ delete_product error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def search_products(self, query):
        conn, cursor = self.get_connection()
        if not conn:
            return []
        try:
            search = f"%{query}%"
            cursor.execute(
                "SELECT * FROM products WHERE name LIKE %s OR category LIKE %s",
                (search, search)
            )
            products = cursor.fetchall()
            self.close_connection(conn, cursor)
            return products
        except Exception as e:
            print(f"❌ search_products error: {e}")
            self.close_connection(conn, cursor)
            return []
    
    # ============================================
    # SUPPLIERS
    # ============================================
    
    def get_all_suppliers(self):
        conn, cursor = self.get_connection()
        if not conn:
            return []
        try:
            cursor.execute("SELECT * FROM suppliers ORDER BY name")
            suppliers = cursor.fetchall()
            self.close_connection(conn, cursor)
            return suppliers
        except Exception as e:
            print(f"❌ get_all_suppliers error: {e}")
            self.close_connection(conn, cursor)
            return []
    
    def get_supplier_by_id(self, supplier_id):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
            supplier = cursor.fetchone()
            self.close_connection(conn, cursor)
            return supplier
        except Exception as e:
            print(f"❌ get_supplier_by_id error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def add_supplier(self, name, contact_person='', email='', phone='', address=''):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute(
                "INSERT INTO suppliers (name, contact_person, email, phone, address) VALUES (%s, %s, %s, %s, %s)",
                (name, contact_person, email, phone, address)
            )
            conn.commit()
            supplier_id = cursor.lastrowid
            self.close_connection(conn, cursor)
            return supplier_id
        except Exception as e:
            print(f"❌ add_supplier error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def update_supplier(self, supplier_id, name, contact_person, email, phone, address=''):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute("""
                UPDATE suppliers 
                SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s
                WHERE id = %s
            """, (name, contact_person, email, phone, address, supplier_id))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_supplier error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def delete_supplier(self, supplier_id):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            # Check if supplier exists
            cursor.execute("SELECT id FROM suppliers WHERE id = %s", (supplier_id,))
            exists = cursor.fetchone()
            if not exists:
                self.close_connection(conn, cursor)
                return False
            
            cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ delete_supplier error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    # ============================================
    # SALES
    # ============================================
    
    def add_sale(self, product_id, quantity, total_price, customer_name='', customer_phone=''):
        print(f"🛒 Adding sale: product_id={product_id}, quantity={quantity}")
        conn, cursor = self.get_connection()
        if not conn:
            print("❌ Connection failed")
            return None
        try:
            cursor.execute(
                "INSERT INTO sales (product_id, quantity, total_price, customer_name, customer_phone) VALUES (%s, %s, %s, %s, %s)",
                (product_id, quantity, total_price, customer_name, customer_phone)
            )
            conn.commit()
            
            cursor.execute("SELECT LAST_INSERT_ID() as id")
            result = cursor.fetchone()
            sale_id = result['id'] if result else None
            
            print(f"✅ Sale recorded! ID: {sale_id}")
            self.close_connection(conn, cursor)
            return sale_id
        except Exception as e:
            print(f"❌ Sale Error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def get_sales_report(self, start_date=None, end_date=None):
        print(f"📊 get_sales_report called - start: {start_date}, end: {end_date}")
        conn, cursor = self.get_connection()
        if not conn:
            print("❌ Connection failed")
            return []
        try:
            query = """
                SELECT s.*, p.name as product_name 
                FROM sales s 
                JOIN products p ON s.product_id = p.id
            """
            params = []
            
            if start_date and end_date:
                query += " WHERE DATE(s.sale_date) BETWEEN %s AND %s"
                params = [start_date, end_date]
                print(f"📊 Filtering: {start_date} to {end_date}")
            
            query += " ORDER BY s.sale_date DESC"
            
            print(f"📊 Query: {query}")
            print(f"📊 Params: {params}")
            
            cursor.execute(query, params)
            sales = cursor.fetchall()
            print(f"📊 Found {len(sales)} sales")
            
            self.close_connection(conn, cursor)
            return sales
        except Exception as e:
            print(f"❌ get_sales_report error: {e}")
            self.close_connection(conn, cursor)
            return []
    
    def get_sale_by_id(self, sale_id):
        conn, cursor = self.get_connection()
        if not conn:
            return None
        try:
            cursor.execute("""
                SELECT s.*, p.name as product_name 
                FROM sales s 
                JOIN products p ON s.product_id = p.id 
                WHERE s.id = %s
            """, (sale_id,))
            sale = cursor.fetchone()
            self.close_connection(conn, cursor)
            return sale
        except Exception as e:
            print(f"❌ get_sale_by_id error: {e}")
            self.close_connection(conn, cursor)
            return None
    
    def update_sale(self, sale_id, quantity, total_price):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            cursor.execute("""
                UPDATE sales 
                SET quantity = %s, total_price = %s 
                WHERE id = %s
            """, (quantity, total_price, sale_id))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ update_sale error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    def delete_sale(self, sale_id):
        conn, cursor = self.get_connection()
        if not conn:
            return False
        try:
            # Check if sale exists
            cursor.execute("SELECT id FROM sales WHERE id = %s", (sale_id,))
            exists = cursor.fetchone()
            if not exists:
                self.close_connection(conn, cursor)
                return False
            
            cursor.execute("DELETE FROM sales WHERE id = %s", (sale_id,))
            conn.commit()
            self.close_connection(conn, cursor)
            return True
        except Exception as e:
            print(f"❌ delete_sale error: {e}")
            self.close_connection(conn, cursor)
            return False
    
    # ============================================
    # DASHBOARD STATS
    # ============================================
    
    def get_dashboard_stats(self):
        conn, cursor = self.get_connection()
        if not conn:
            return {'total_products': 0, 'total_suppliers': 0, 'today_sales': 0, 'total_stock': 0, 'low_stock': 0}
        try:
            stats = {}
            cursor.execute("SELECT COUNT(*) as total FROM products")
            result = cursor.fetchone()
            stats['total_products'] = result['total'] if result else 0
            
            cursor.execute("SELECT COUNT(*) as total FROM suppliers")
            result = cursor.fetchone()
            stats['total_suppliers'] = result['total'] if result else 0
            
            cursor.execute("SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE DATE(sale_date) = CURDATE()")
            result = cursor.fetchone()
            stats['today_sales'] = result['total'] if result else 0
            
            cursor.execute("SELECT COALESCE(SUM(quantity), 0) as total FROM products")
            result = cursor.fetchone()
            stats['total_stock'] = result['total'] if result else 0
            
            cursor.execute("SELECT COUNT(*) as total FROM products WHERE quantity <= 10")
            result = cursor.fetchone()
            stats['low_stock'] = result['total'] if result else 0
            
            self.close_connection(conn, cursor)
            return stats
        except Exception as e:
            print(f"❌ get_dashboard_stats error: {e}")
            self.close_connection(conn, cursor)
            return {'total_products': 0, 'total_suppliers': 0, 'today_sales': 0, 'total_stock': 0, 'low_stock': 0}
    
    def get_low_stock_products(self, threshold=10):
        conn, cursor = self.get_connection()
        if not conn:
            return []
        try:
            cursor.execute("SELECT * FROM products WHERE quantity <= %s ORDER BY quantity ASC", (threshold,))
            products = cursor.fetchall()
            self.close_connection(conn, cursor)
            return products
        except Exception as e:
            print(f"❌ get_low_stock_products error: {e}")
            self.close_connection(conn, cursor)
            return []

# ============================================
# SINGLETON INSTANCE
# ============================================
db = Database()
print("=" * 40)
print("📦 Database ready")
print("=" * 40)