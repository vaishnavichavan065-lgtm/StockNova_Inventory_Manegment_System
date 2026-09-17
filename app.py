from flask import Flask, render_template, request, jsonify, session, redirect
from database import db
import traceback
import random
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'mysecretkey123'

# ===== SESSION CONFIG =====
app.config['SESSION_PERMANENT'] = True
app.config['PERMANENT_SESSION_LIFETIME'] = 86400  # 24 hours

# ============================================
# FIXED ADMIN CREDENTIALS
# ============================================
ADMIN_USERNAME = 'vaishnavichavan'
ADMIN_PASSWORD = 'vaishu@1234'

# ============================================
# LOGIN REQUIRED DECORATOR
# ============================================

def login_required(f):
    def wrapper(*args, **kwargs):
        if 'user_id' not in session and 'is_admin' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    wrapper.__name__ = f.__name__
    return wrapper

# ============================================
# PAGE ROUTES
# ============================================

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login')
def login_page():
    return render_template('login.html')

@app.route('/signup')
def signup_page():
    return render_template('signup.html')

@app.route('/reset-password')
def reset_password_page():
    username = request.args.get('username')
    if not username:
        return redirect('/login')
    return render_template('reset_password.html', username=username)

# ============================================
# DASHBOARD
# ============================================
@app.route('/dashboard')
@login_required
def dashboard():
    # Debugging - console मध्ये print करा
    print("=" * 50)
    print("🔍 SESSION DATA:")
    print(f"   is_admin: {session.get('is_admin')}")
    print(f"   role: {session.get('role')}")
    print(f"   user_id: {session.get('user_id')}")
    print(f"   username: {session.get('username')}")
    print("=" * 50)
    
    # Admin check - फक्त is_admin True असेल तरच Admin dashboard
    if session.get('is_admin') == True:
        return render_template('dashboard.html')
    else:
        return render_template('dashboard_staff.html')

@app.route('/products')
@login_required
def products_page():
    if session.get('is_admin') == True:
        return render_template('products.html')
    else:
        return render_template('products_staff.html')

@app.route('/add-product')
@login_required
def add_product_page():
    if session.get('is_admin') != True:
        return redirect('/dashboard')
    return render_template('add_product.html')

@app.route('/edit-product/<int:product_id>')
@login_required
def edit_product_page(product_id):
    if session.get('is_admin') != True:
        return redirect('/dashboard')
    return render_template('edit_product.html', product_id=product_id)

@app.route('/suppliers')
@login_required
def suppliers_page():
    if session.get('is_admin') == True:
        return render_template('suppliers.html')
    else:
        return render_template('suppliers_staff.html')

@app.route('/sales-report')
@login_required
def sales_report_page():
    if session.get('is_admin') == True:
        return render_template('sales_report.html')
    else:
        return render_template('sales_report_staff.html')

@app.route('/profile')
@login_required
def profile_page():
    if session.get('is_admin') == True:
        return render_template('profile.html')
    else:
        return render_template('staff_profile.html')
    
@app.route('/settings')
@login_required
def settings_page():
    if session.get('is_admin') == True:
        return render_template('settings.html')
    else:
        return render_template('staff_settings.html')

@app.route('/reset-session')
def reset_session():
    session.clear()
    return redirect('/login')

# ============================================
# FORGOT PASSWORD - NEW
# ============================================

@app.route('/api/forgot-password', methods=['POST'])
def forgot_password():
    try:
        data = request.json
        username = data.get('username', '').strip()
        
        if not username:
            return jsonify({'success': False, 'message': 'Username is required'}), 400
        
        # Check if user exists
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database error'}), 500
        
        cursor.execute("SELECT id, username FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        db.close_connection(conn, cursor)
        
        if not user:
            return jsonify({'success': False, 'message': 'Username not found'}), 404
        
        # Store username in session for verification
        session['reset_username'] = username
        
        return jsonify({
            'success': True,
            'message': 'Username verified. Proceed to reset password.'
        })
        
    except Exception as e:
        print(f"❌ Forgot password error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500


# ============================================
# RESET PASSWORD API - NEW
# ============================================

@app.route('/api/reset-password', methods=['POST'])
def reset_password():
    try:
        data = request.json
        username = data.get('username', '').strip()
        new_password = data.get('new_password', '')
        
        if not username or not new_password:
            return jsonify({'success': False, 'message': 'Username and password required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        # Check if user exists
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database error'}), 500
        
        cursor.execute("SELECT id FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        if not user:
            db.close_connection(conn, cursor)
            return jsonify({'success': False, 'message': 'Username not found'}), 404
        
        # Update password
        hashed = db.hash_password(new_password)
        cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed, username))
        conn.commit()
        db.close_connection(conn, cursor)
        
        # Clear reset session
        session.pop('reset_username', None)
        
        return jsonify({'success': True, 'message': 'Password reset successfully!'})
        
    except Exception as e:
        print(f"❌ Reset password error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# AUTH API
# ============================================

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.json
        username = data.get('username', '').strip()
        password = data.get('password', '')
        login_type = data.get('login_type', 'staff')

        print(f"🔐 Login attempt: {username} (type: {login_type})")

        # ✅ जुनी session clear करा
        session.clear()

        if login_type == 'admin':
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                session.permanent = True
                session['is_admin'] = True
                session['username'] = username
                session['full_name'] = 'Administrator'
                session['role'] = 'admin'
                return jsonify({
                    'success': True,
                    'message': 'Admin login successful',
                    'user': {'username': username, 'full_name': 'Administrator', 'role': 'admin'}
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid admin credentials'}), 401

        elif login_type == 'staff':
            user = db.login_user(username, password)
            if user:
                session.permanent = True
                session['user_id'] = user['id']
                session['username'] = user['username']
                session['full_name'] = user['full_name']
                session['role'] = 'staff'
                # ✅ 'is_admin' सेट करू नका - हे महत्वाचे आहे!
                return jsonify({
                    'success': True,
                    'message': 'Staff login successful',
                    'user': {
                        'id': user['id'],
                        'username': user['username'],
                        'full_name': user['full_name'],
                        'role': 'staff'
                    }
                })
            else:
                return jsonify({'success': False, 'message': 'Invalid staff credentials'}), 401

        return jsonify({'success': False, 'message': 'Invalid login type'}), 400

    except Exception as e:
        print(f"❌ Login error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/logout', methods=['POST'])
def logout():
    session.clear()
    return jsonify({'success': True, 'message': 'Logged out'})

@app.route('/api/current-user')
def current_user():
    if session.get('is_admin') == True:
        return jsonify({
            'success': True,
            'user': {
                'username': session.get('username'),
                'full_name': session.get('full_name', 'Administrator'),
                'role': 'admin',
                'profile_photo': None
            }
        })
    elif 'user_id' in session:
        user = db.get_user_by_id(session['user_id'])
        if user:
            return jsonify({
                'success': True,
                'user': {
                    'id': user['id'],
                    'username': user['username'],
                    'full_name': user['full_name'],
                    'email': user.get('email'),
                    'role': 'staff',
                    'profile_photo': user.get('profile_photo'),
                    'employee_id': user.get('employee_id'),
                    'member_since': '2026'
                }
            })
    return jsonify({'success': False, 'message': 'Not logged in'}), 401

@app.route('/api/register', methods=['POST'])
def register():
    try:
        data = request.json
        print("=" * 40)
        print(f"📝 Register: {data.get('username')}, {data.get('email')}")
        print("=" * 40)
        
        username = data.get('username', '').strip()
        email = data.get('email', '').strip()
        password = data.get('password', '')
        full_name = data.get('full_name', '').strip()
        
        if not username or not email or not password or not full_name:
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        if len(password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        user_id = db.register_user(username, email, password, full_name)
        
        if user_id:
            print(f"✅ User registered! ID: {user_id}")
            return jsonify({'success': True, 'message': 'Staff account created!'})
        else:
            return jsonify({'success': False, 'message': 'Username or email already exists'}), 400
    except Exception as e:
        print(f"❌ Register error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# PRODUCTS API
# ============================================

@app.route('/api/products', methods=['GET'])
@login_required
def get_products():
    try:
        products = db.get_all_products()
        return jsonify(products)
    except Exception as e:
        print(f"❌ Get products error: {e}")
        return jsonify([]), 500

@app.route('/api/products', methods=['POST'])
@login_required
def add_product():
    if session.get('is_admin') != True:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.json
        print("=" * 50)
        print("📦 Add Product Request:")
        print(f"   Name: {data.get('name')}")
        print(f"   Category: {data.get('category')}")
        print(f"   Quantity: {data.get('quantity')}")
        print(f"   Price: {data.get('price')}")
        print("=" * 50)
        
        product_id = db.add_product(
            data.get('name'),
            data.get('category'),
            int(data.get('quantity', 0)),
            float(data.get('price', 0)),
            int(data.get('supplier_id', 0)),
            5,
            data.get('description', '')
        )
        
        if product_id:
            print(f"✅ Product added with ID: {product_id}")
            return jsonify({'success': True, 'message': 'Product added!', 'id': product_id})
        else:
            print("❌ Failed to add product")
            return jsonify({'success': False, 'message': 'Failed to add product'}), 500
    except Exception as e:
        print(f"❌ Add product error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['PUT'])
@login_required
def update_product(product_id):
    try:
        data = request.json
        
        if session.get('is_admin') == True:
            success = db.update_product(
                product_id,
                data.get('name'),
                data.get('category'),
                int(data.get('quantity', 0)),
                float(data.get('price', 0)),
                int(data.get('supplier_id', 0)),
                int(data.get('reorder_level', 5)),
                data.get('description', '')
            )
        else:
            success = db.update_stock(product_id, int(data.get('quantity', 0)))
        
        if success:
            return jsonify({'success': True, 'message': 'Updated successfully'})
        return jsonify({'success': False, 'message': 'Update failed'}), 500
    except Exception as e:
        print(f"❌ Update product error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/<int:product_id>', methods=['DELETE'])
@login_required
def delete_product(product_id):
    if session.get('is_admin') != True:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        if db.delete_product(product_id):
            return jsonify({'success': True, 'message': 'Product deleted!'})
        return jsonify({'success': False, 'message': 'Product not found'}), 404
    except Exception as e:
        print(f"❌ Delete product error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/products/search')
@login_required
def search_products():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
        products = db.search_products(query)
        return jsonify(products)
    except Exception as e:
        print(f"❌ Search products error: {e}")
        return jsonify([]), 500

@app.route('/api/products/<int:product_id>', methods=['GET'])
@login_required
def get_product_by_id(product_id):
    try:
        product = db.get_product_by_id(product_id)
        if product:
            return jsonify(product)
        else:
            return jsonify({'error': 'Product not found'}), 404
    except Exception as e:
        print(f"❌ Get product error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# SUPPLIERS API
# ============================================

@app.route('/api/suppliers', methods=['GET'])
@login_required
def get_suppliers():
    try:
        suppliers = db.get_all_suppliers()
        return jsonify(suppliers)
    except Exception as e:
        print(f"❌ Get suppliers error: {e}")
        return jsonify([]), 500

@app.route('/api/suppliers', methods=['POST'])
@login_required
def add_supplier():
    if session.get('is_admin') != True:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.json
        supplier_id = db.add_supplier(
            data.get('name'),
            data.get('contact_person', ''),
            data.get('email', ''),
            data.get('phone', ''),
            data.get('address', '')
        )
        if supplier_id:
            return jsonify({'success': True, 'message': 'Supplier added!', 'id': supplier_id})
        return jsonify({'success': False, 'message': 'Failed to add supplier'}), 500
    except Exception as e:
        print(f"❌ Add supplier error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['GET'])
@login_required
def get_supplier(supplier_id):
    try:
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor.execute("SELECT * FROM suppliers WHERE id = %s", (supplier_id,))
        supplier = cursor.fetchone()
        db.close_connection(conn, cursor)
        
        if supplier:
            return jsonify(supplier)
        else:
            return jsonify({'error': 'Supplier not found'}), 404
    except Exception as e:
        print(f"❌ get_supplier error: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['PUT'])
@login_required
def update_supplier(supplier_id):
    if session.get('is_admin') != True:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        data = request.get_json()
        name = data.get('name')
        contact_person = data.get('contact_person', '')
        email = data.get('email', '')
        phone = data.get('phone', '')
        address = data.get('address', '')
        
        if not name:
            return jsonify({'success': False, 'message': 'Supplier name required'}), 400
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor.execute("""
            UPDATE suppliers 
            SET name = %s, contact_person = %s, email = %s, phone = %s, address = %s
            WHERE id = %s
        """, (name, contact_person, email, phone, address, supplier_id))
        conn.commit()
        
        affected_rows = cursor.rowcount
        db.close_connection(conn, cursor)
        
        if affected_rows > 0:
            return jsonify({'success': True, 'message': 'Supplier updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404
    except Exception as e:
        print(f"❌ update_supplier error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/suppliers/<int:supplier_id>', methods=['DELETE'])
@login_required
def delete_supplier_route(supplier_id):
    if session.get('is_admin') != True:
        return jsonify({'success': False, 'message': 'Admin access required'}), 403
    
    try:
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor.execute("SELECT id FROM suppliers WHERE id = %s", (supplier_id,))
        exists = cursor.fetchone()
        
        if not exists:
            db.close_connection(conn, cursor)
            return jsonify({'success': False, 'message': 'Supplier not found'}), 404
        
        cursor.execute("DELETE FROM suppliers WHERE id = %s", (supplier_id,))
        conn.commit()
        
        db.close_connection(conn, cursor)
        return jsonify({'success': True, 'message': 'Supplier deleted successfully'})
    except Exception as e:
        print(f"❌ delete_supplier error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/suppliers/search')
@login_required
def search_suppliers():
    try:
        query = request.args.get('q', '').strip()
        if not query:
            return jsonify([])
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify([])
        
        search = f"%{query}%"
        cursor.execute("""
            SELECT * FROM suppliers 
            WHERE name LIKE %s OR contact_person LIKE %s OR email LIKE %s OR phone LIKE %s
            ORDER BY name
        """, (search, search, search, search))
        suppliers = cursor.fetchall()
        db.close_connection(conn, cursor)
        return jsonify(suppliers)
    except Exception as e:
        print(f"❌ Search suppliers error: {e}")
        return jsonify([]), 500

# ============================================
# SALES API
# ============================================

@app.route('/api/sales', methods=['POST'])
@login_required
def add_sale():
    try:
        data = request.json
        print("=" * 50)
        print("📦 Add Sale Request:")
        print(f"   Product ID: {data.get('product_id')}")
        print(f"   Quantity: {data.get('quantity')}")
        print(f"   Total Price: {data.get('total_price')}")
        print(f"   Customer: {data.get('customer_name')}")
        print("=" * 50)
        
        sale_id = db.add_sale(
            int(data.get('product_id', 0)),
            int(data.get('quantity', 0)),
            float(data.get('total_price', 0)),
            data.get('customer_name', ''),
            data.get('customer_phone', '')
        )
        
        if sale_id:
            print(f"✅ Sale recorded! ID: {sale_id}")
            return jsonify({'success': True, 'message': 'Sale recorded!', 'id': sale_id})
        else:
            print("❌ Failed to record sale")
            return jsonify({'success': False, 'message': 'Failed to record sale'}), 500
    except Exception as e:
        print(f"❌ Add sale error: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sales/<int:sale_id>', methods=['GET'])
@login_required
def get_sale(sale_id):
    try:
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'error': 'Database connection failed'}), 500
        
        cursor.execute("""
            SELECT s.*, p.name as product_name 
            FROM sales s 
            JOIN products p ON s.product_id = p.id 
            WHERE s.id = %s
        """, (sale_id,))
        
        sale = cursor.fetchone()
        db.close_connection(conn, cursor)
        
        if sale:
            if isinstance(sale, dict):
                return jsonify(sale)
            else:
                sale_dict = {
                    'id': sale[0],
                    'product_id': sale[1],
                    'quantity': sale[2],
                    'total_price': float(sale[3]) if sale[3] else 0,
                    'customer_name': sale[4] or '',
                    'customer_phone': sale[5] or '',
                    'sale_date': sale[6].strftime('%Y-%m-%d') if sale[6] else None,
                    'product_name': sale[7] or ''
                }
                return jsonify(sale_dict)
        else:
            return jsonify({'error': 'Sale not found'}), 404
            
    except Exception as e:
        print(f"❌ Error in get_sale: {e}")
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500

@app.route('/api/sales/<int:sale_id>', methods=['PUT'])
@login_required
def update_sale(sale_id):
    try:
        data = request.get_json()
        quantity = data.get('quantity')
        total_price = data.get('total_price')
        
        if not quantity or not total_price:
            return jsonify({'success': False, 'message': 'Quantity and price required'}), 400
        
        try:
            quantity = int(quantity)
            total_price = float(total_price)
        except (ValueError, TypeError):
            return jsonify({'success': False, 'message': 'Invalid quantity or price format'}), 400
        
        if quantity <= 0:
            return jsonify({'success': False, 'message': 'Quantity must be greater than 0'}), 400
        
        if total_price <= 0:
            return jsonify({'success': False, 'message': 'Price must be greater than 0'}), 400
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor.execute("""
            UPDATE sales 
            SET quantity = %s, total_price = %s 
            WHERE id = %s
        """, (quantity, total_price, sale_id))
        conn.commit()
        
        affected_rows = cursor.rowcount
        db.close_connection(conn, cursor)
        
        if affected_rows > 0:
            return jsonify({'success': True, 'message': 'Sale updated successfully'})
        else:
            return jsonify({'success': False, 'message': 'Sale not found'}), 404
            
    except Exception as e:
        print(f"❌ Error in update_sale: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/api/sales/<int:sale_id>', methods=['DELETE'])
@login_required
def delete_sale(sale_id):
    try:
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'success': False, 'message': 'Database connection failed'}), 500
        
        cursor.execute("SELECT id FROM sales WHERE id = %s", (sale_id,))
        exists = cursor.fetchone()
        
        if not exists:
            db.close_connection(conn, cursor)
            return jsonify({'success': False, 'message': 'Sale not found'}), 404
        
        cursor.execute("DELETE FROM sales WHERE id = %s", (sale_id,))
        conn.commit()
        
        db.close_connection(conn, cursor)
        return jsonify({'success': True, 'message': 'Sale deleted successfully'})
            
    except Exception as e:
        print(f"❌ Error in delete_sale: {e}")
        traceback.print_exc()
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# SALES REPORT API
# ============================================

@app.route('/api/sales-report')
@login_required
def get_sales_report():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        print(f"📊 get_sales_report called - start: {start_date}, end: {end_date}")
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify([])
        
        query = """
            SELECT s.*, p.name as product_name 
            FROM sales s 
            JOIN products p ON s.product_id = p.id 
            WHERE 1=1
        """
        params = []
        
        if start_date and end_date:
            query += " AND DATE(s.sale_date) BETWEEN %s AND %s"
            params.extend([start_date, end_date])
            print(f"📊 Filtering: {start_date} to {end_date}")
        
        query += " ORDER BY s.sale_date DESC"
        
        print(f"📊 Query: {query}")
        print(f"📊 Params: {params}")
        
        cursor.execute(query, params)
        sales = cursor.fetchall()
        
        result = []
        for sale in sales:
            if isinstance(sale, dict):
                result.append(sale)
            else:
                result.append({
                    'id': sale[0],
                    'product_id': sale[1],
                    'quantity': sale[2],
                    'total_price': float(sale[3]) if sale[3] else 0,
                    'customer_name': sale[4] or '',
                    'customer_phone': sale[5] or '',
                    'sale_date': sale[6].strftime('%Y-%m-%d') if sale[6] else None,
                    'product_name': sale[7] or ''
                })
        
        db.close_connection(conn, cursor)
        print(f"📊 Found {len(result)} sales")
        return jsonify(result)
    except Exception as e:
        print(f"❌ Sales report error: {e}")
        traceback.print_exc()
        return jsonify([]), 500

# ============================================
# DASHBOARD API
# ============================================

@app.route('/api/stats')
@login_required
def get_stats():
    try:
        stats = db.get_dashboard_stats()
        stats['total_stock'] = stats.get('total_stock', 0)
        stats['total_orders'] = random.randint(100, 500)
        stats['total_users'] = random.randint(5, 20)
        stats['total_stock_value'] = stats.get('total_stock', 0) * random.randint(100, 500)
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Stats error: {e}")
        return jsonify({'total_products': 0, 'total_suppliers': 0, 'today_sales': 0, 'total_stock': 0, 'low_stock': 0})

@app.route('/api/low-stock')
@login_required
def get_low_stock():
    try:
        products = db.get_low_stock_products()
        return jsonify(products)
    except Exception as e:
        print(f"❌ Low stock error: {e}")
        return jsonify([])

# ============================================
# SALES CHART API
# ============================================

@app.route('/api/sales-chart')
@login_required
def get_sales_chart():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify([])
        
        query = """
            SELECT 
                DATE_FORMAT(sale_date, '%%b') as month,
                COALESCE(SUM(total_price), 0) as total
            FROM sales
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(sale_date) >= %s"
            params.append(start_date)
        if end_date:
            query += " AND DATE(sale_date) <= %s"
            params.append(end_date)
        
        query += """
            GROUP BY DATE_FORMAT(sale_date, '%%b'), MONTH(sale_date)
            ORDER BY MIN(sale_date) ASC
            LIMIT 6
        """
        
        cursor.execute(query, params)
        data = cursor.fetchall()
        
        result = []
        for row in data:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    'month': row[0],
                    'total': float(row[1]) if row[1] else 0
                })
        
        db.close_connection(conn, cursor)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Sales chart error: {e}")
        traceback.print_exc()
        return jsonify([])

# ============================================
# TOP SELLING API
# ============================================

@app.route('/api/top-selling')
@login_required
def get_top_selling():
    try:
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify([])
        
        query = """
            SELECT 
                p.name, 
                COALESCE(SUM(s.quantity), 0) as total_sold, 
                COALESCE(SUM(s.total_price), 0) as total_revenue
            FROM sales s
            JOIN products p ON s.product_id = p.id
            WHERE 1=1
        """
        params = []
        
        if start_date:
            query += " AND DATE(s.sale_date) >= %s"
            params.append(start_date)
        if end_date:
            query += " AND DATE(s.sale_date) <= %s"
            params.append(end_date)
        
        query += """
            GROUP BY p.id, p.name
            ORDER BY total_sold DESC
            LIMIT 5
        """
        
        cursor.execute(query, params)
        products = cursor.fetchall()
        
        result = []
        for row in products:
            if isinstance(row, dict):
                result.append(row)
            else:
                result.append({
                    'name': row[0],
                    'total_sold': int(row[1]) if row[1] else 0,
                    'total_revenue': float(row[2]) if row[2] else 0
                })
        
        db.close_connection(conn, cursor)
        return jsonify(result)
    except Exception as e:
        print(f"❌ Top selling error: {e}")
        traceback.print_exc()
        return jsonify([])

# ============================================
# SALES STATS API
# ============================================

@app.route('/api/sales-stats')
@login_required
def get_sales_stats():
    try:
        conn, cursor = db.get_connection()
        if not conn:
            return jsonify({'today': 0, 'weekly': 0, 'monthly': 0, 'total': 0})
        
        stats = {}
        
        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE DATE(sale_date) = CURDATE()"
        )
        row = cursor.fetchone()
        stats['today'] = float(row['total']) if isinstance(row, dict) else float(row[0]) if row else 0
        
        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE WEEK(sale_date) = WEEK(CURDATE()) AND YEAR(sale_date) = YEAR(CURDATE())"
        )
        row = cursor.fetchone()
        stats['weekly'] = float(row['total']) if isinstance(row, dict) else float(row[0]) if row else 0
        
        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) as total FROM sales WHERE MONTH(sale_date) = MONTH(CURDATE()) AND YEAR(sale_date) = YEAR(CURDATE())"
        )
        row = cursor.fetchone()
        stats['monthly'] = float(row['total']) if isinstance(row, dict) else float(row[0]) if row else 0
        
        cursor.execute(
            "SELECT COALESCE(SUM(total_price), 0) as total FROM sales"
        )
        row = cursor.fetchone()
        stats['total'] = float(row['total']) if isinstance(row, dict) else float(row[0]) if row else 0
        
        db.close_connection(conn, cursor)
        return jsonify(stats)
    except Exception as e:
        print(f"❌ Sales stats error: {e}")
        traceback.print_exc()
        return jsonify({'today': 0, 'weekly': 0, 'monthly': 0, 'total': 0})

# ============================================
# PROFILE API
# ============================================

@app.route('/api/profile', methods=['PUT'])
@login_required
def update_profile():
    try:
        data = request.json
        full_name = data.get('full_name')
        email = data.get('email')
        employee_id = data.get('employee_id')
        
        if not full_name:
            return jsonify({'success': False, 'message': 'Full name required'}), 400
        
        if session.get('is_admin') == True:
            username = session.get('username')
            conn, cursor = db.get_connection()
            if not conn:
                return jsonify({'success': False, 'message': 'Database error'}), 500
            
            cursor.execute("""
                UPDATE users 
                SET full_name = %s, email = %s, employee_id = %s 
                WHERE username = %s
            """, (full_name, email, employee_id, username))
            conn.commit()
            db.close_connection(conn, cursor)
            
            session['full_name'] = full_name
            return jsonify({'success': True, 'message': 'Profile updated'})
        
        elif 'user_id' in session:
            user_id = session.get('user_id')
            success = db.update_profile(user_id, full_name, email, employee_id)
            
            if success:
                session['full_name'] = full_name
                return jsonify({'success': True, 'message': 'Profile updated'})
            else:
                return jsonify({'success': False, 'message': 'Update failed'}), 500
        
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    except Exception as e:
        print(f"❌ Update profile error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# CHANGE PASSWORD
# ============================================

@app.route('/api/change-password', methods=['POST'])
@login_required
def change_password():
    try:
        data = request.json
        current_password = data.get('current_password')
        new_password = data.get('new_password')
        
        if not current_password or not new_password:
            return jsonify({'success': False, 'message': 'All fields required'}), 400
        
        if len(new_password) < 6:
            return jsonify({'success': False, 'message': 'Password must be at least 6 characters'}), 400
        
        if session.get('is_admin') == True:
            username = session.get('username')
            conn, cursor = db.get_connection()
            if not conn:
                return jsonify({'success': False, 'message': 'Database error'}), 500
            
            hashed_current = db.hash_password(current_password)
            cursor.execute("SELECT * FROM users WHERE username = %s AND password = %s", (username, hashed_current))
            user = cursor.fetchone()
            
            if not user:
                db.close_connection(conn, cursor)
                return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
            
            hashed_new = db.hash_password(new_password)
            cursor.execute("UPDATE users SET password = %s WHERE username = %s", (hashed_new, username))
            conn.commit()
            db.close_connection(conn, cursor)
            return jsonify({'success': True, 'message': 'Password changed'})
        
        elif 'user_id' in session:
            user_id = session.get('user_id')
            success = db.change_password(user_id, current_password, new_password)
            
            if success:
                return jsonify({'success': True, 'message': 'Password changed'})
            else:
                return jsonify({'success': False, 'message': 'Current password is incorrect'}), 400
        
        return jsonify({'success': False, 'message': 'Not logged in'}), 401
    except Exception as e:
        print(f"❌ Change password error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# UPDATE PROFILE PHOTO
# ============================================

@app.route('/api/profile/photo', methods=['POST'])
@login_required
def update_profile_photo():
    try:
        if 'photo' not in request.files:
            return jsonify({'success': False, 'message': 'No photo provided'}), 400
        
        file = request.files['photo']
        if file.filename == '':
            return jsonify({'success': False, 'message': 'No photo selected'}), 400
        
        import os
        import uuid
        
        upload_dir = 'static/uploads/profiles'
        if not os.path.exists(upload_dir):
            os.makedirs(upload_dir)
        
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else 'jpg'
        
        if session.get('is_admin') == True:
            user_identifier = session.get('username', 'admin')
        else:
            user_identifier = str(session.get('user_id', 'user'))
        
        filename = f"{user_identifier}_{uuid.uuid4().hex[:8]}.{ext}"
        filepath = os.path.join(upload_dir, filename)
        file.save(filepath)
        
        photo_url = f"/{upload_dir}/{filename}"
        
        if session.get('is_admin') == True:
            username = session.get('username')
            conn, cursor = db.get_connection()
            if not conn:
                return jsonify({'success': False, 'message': 'Database error'}), 500
            
            cursor.execute("UPDATE users SET profile_photo = %s WHERE username = %s", (photo_url, username))
            conn.commit()
            db.close_connection(conn, cursor)
        else:
            user_id = session.get('user_id')
            success = db.update_profile_photo(user_id, photo_url)
            if not success:
                return jsonify({'success': False, 'message': 'Update failed'}), 500
        
        return jsonify({'success': True, 'message': 'Photo updated', 'photo_url': photo_url})
    except Exception as e:
        print(f"❌ Upload photo error: {e}")
        return jsonify({'success': False, 'message': str(e)}), 500

# ============================================
# BARCODE GENERATOR API
# ============================================

@app.route('/api/barcode/<int:product_id>')
@login_required
def generate_barcode(product_id):
    try:
        import barcode
        from barcode.writer import ImageWriter
        from io import BytesIO
        import base64
        
        product = db.get_product_by_id(product_id)
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        code128 = barcode.get_barcode_class('code128')
        barcode_value = f"STOCKNOVA-{product_id:06d}"
        barcode_img = code128(barcode_value, writer=ImageWriter())
        
        buffer = BytesIO()
        barcode_img.write(buffer)
        barcode_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'barcode': barcode_base64,
            'product_name': product['name'],
            'product_id': product['id']
        })
    except ImportError:
        return jsonify({
            'success': False,
            'message': 'Barcode library not installed. Run: pip install python-barcode Pillow'
        }), 500
    except Exception as e:
        print(f"❌ Barcode error: {e}")
        return jsonify({'error': str(e)}), 500

# ============================================
# EXPORT EXCEL REPORT API
# ============================================

@app.route('/api/export/excel/<report_type>')
@login_required
def export_excel(report_type):
    try:
        from openpyxl import Workbook
        from io import BytesIO
        import base64
        
        wb = Workbook()
        ws = wb.active
        ws.title = "Report"
        
        if report_type == 'products':
            products = db.get_all_products()
            headers = ['ID', 'Product Name', 'Category', 'Quantity', 'Price', 'Supplier']
            ws.append(headers)
            for p in products:
                ws.append([
                    p.get('id', ''),
                    p.get('name', ''),
                    p.get('category', ''),
                    p.get('quantity', 0),
                    p.get('price', 0),
                    p.get('supplier_name', '')
                ])
            filename = 'products_report.xlsx'
            
        elif report_type == 'sales':
            sales = db.get_sales_report()
            headers = ['ID', 'Product', 'Quantity', 'Total Price', 'Customer', 'Date']
            ws.append(headers)
            for s in sales:
                ws.append([
                    s.get('id', ''),
                    s.get('product_name', ''),
                    s.get('quantity', 0),
                    s.get('total_price', 0),
                    s.get('customer_name', ''),
                    s.get('sale_date', '')
                ])
            filename = 'sales_report.xlsx'
            
        else:
            return jsonify({'error': 'Invalid report type'}), 400
        
        for col in ws.columns:
            max_length = 0
            column = col[0].column_letter
            for cell in col:
                try:
                    if len(str(cell.value)) > max_length:
                        max_length = len(str(cell.value))
                except:
                    pass
            adjusted_width = min(max_length + 2, 30)
            ws.column_dimensions[column].width = adjusted_width
        
        output = BytesIO()
        wb.save(output)
        output.seek(0)
        excel_data = base64.b64encode(output.getvalue()).decode('utf-8')
        
        return jsonify({
            'success': True,
            'filename': filename,
            'data': excel_data
        })
        
    except ImportError:
        return jsonify({'success': False, 'message': 'openpyxl not installed. Run: pip install openpyxl'}), 500
    except Exception as e:
        print(f"❌ Export error: {e}")
        return jsonify({'error': str(e)}), 500


    # ============================================
# EDIT SALE PAGE
# ============================================
@app.route('/edit-sale')
@login_required
def edit_sale_page():
    if session.get('is_admin') != True:
        return redirect('/dashboard')
    return render_template('edit_sale.html')
# ============================================
# START SERVER
# ============================================

if __name__ == '__main__':
    print("=" * 50)
    print("🚀 StockNova Inventory Management System")
    print("=" * 50)
    print("🔑 Admin: Full Access")
    print("👤 Staff: Limited Access (View + Update Stock Only)")
    print("🌐 Server: http://localhost:5000")
    print("=" * 50)
    app.run(debug=True, host='0.0.0.0', port=5000)