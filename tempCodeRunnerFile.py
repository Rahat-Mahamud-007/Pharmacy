import mysql.connector
import random
import functools
from flask import Flask, render_template, request, redirect, url_for, session, flash
from config import db_config, SECRET_KEY

app = Flask(__name__)
app.secret_key = SECRET_KEY

# --- Database Connection ---
def get_db_connection():
    try:
        conn = mysql.connector.connect(**db_config)
        return conn
    except mysql.connector.Error as err:
        print(f"Database Connection Error: {err}")
        return None

# --- Decorator for Access Control ---
def login_required(role):
    def decorator(f):
        @functools.wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session or session.get('role') != role:
                flash(f'You must be logged in as a {role} to view this page.', 'danger')
                if role == 'customer':
                    return redirect(url_for('customer_login'))
                elif role == 'employee':
                    return redirect(url_for('employee_login'))
                elif role == 'admin':
                    return redirect(url_for('admin_login'))
                else:
                    return redirect(url_for('index'))
            return f(*args, **kwargs)
        return decorated_function
    return decorator

# --- Main & Static Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/contact-us')
def contact_us():
    conn = get_db_connection()
    if conn is None:
        flash('Could not connect to the database.', 'danger')
        return render_template('contact_us.html', branches=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BRANCHNAME, LOCATION, BRANCHMANAGERNUBMBER FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('contact_us.html', branches=branches)

@app.route('/login-signup')
def login_signup():
    return render_template('login_signup.html')

@app.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        user_id = request.form.get('user_id')
        email = request.form.get('email')
        contact = request.form.get('contact')
        new_password = request.form.get('new_password')
        confirm_password = request.form.get('confirm_password')
        
        errors = {}
        
        if new_password != confirm_password:
            errors['password'] = 'Passwords do not match.'

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('forgot_password.html', errors=errors, form_data=request.form)

        cursor = conn.cursor(dictionary=True)
        
        user_found = False
        user_type = None
        
        # Check CUSTOMERS table first
        cursor.execute("SELECT * FROM CUSTOMERS WHERE CUSTOMERID = %s", (user_id,))
        record = cursor.fetchone()
        
        if record:
            user_found = True
            user_type = 'customer'
            if record.get('EMAIL') != email:
                errors['email'] = 'Incorrect Email.'
            if record.get('CONTACT') != contact:
                errors['contact'] = 'Incorrect Contact Number.'
        else:
            # If not found in customers, check EMPLOYEES table
            cursor.execute("SELECT * FROM EMPLOYEES WHERE EMPLOYEEID = %s", (user_id,))
            record = cursor.fetchone()
            if record:
                user_found = True
                user_type = 'employee'
                if record.get('Email') != email:
                    errors['email'] = 'Incorrect Email.'
                if record.get('CONTACT') != contact:
                    errors['contact'] = 'Incorrect Contact Number.'

        if not user_found:
            errors['user_id'] = 'ID not found in any account.'

        if errors:
            cursor.close()
            conn.close()
            return render_template('forgot_password.html', errors=errors, form_data=request.form)
        
        # If no errors, proceed to update the password/PIN
        try:
            if user_type == 'customer':
                cursor.execute("UPDATE CUSTOMERS SET PASSWORD = %s WHERE CUSTOMERID = %s", (new_password, user_id))
            elif user_type == 'employee':
                cursor.execute("UPDATE EMPLOYEES SET EMPLOYEEPIN = %s WHERE EMPLOYEEID = %s", (new_password, user_id))
            
            conn.commit()
            flash('Your password/PIN has been reset successfully. Please log in.', 'success')
            return redirect(url_for('login_signup'))
        except mysql.connector.Error as err:
            flash(f'An error occurred: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

        return redirect(url_for('forgot_password'))

    # For GET request, just show the form with no errors
    return render_template('forgot_password.html', errors={}, form_data={})

# --- Search Routes ---
@app.route('/search', methods=['GET', 'POST'])
def search_medicine():
    if request.method == 'POST':
        search_query = request.form.get('search_query', '')
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return render_template('search/search_form.html')
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT m.MEDICINEID, m.MEDICINENAME, m.PRICE, m.MANUFACTURER, mc.CATEGORYNAME
            FROM MEDICINES m
            LEFT JOIN MEDICINECATEGORY mc ON m.CATEGORYID = mc.CATEGORYID
            WHERE m.MEDICINENAME LIKE %s
        """
        cursor.execute(query, (f'%{search_query}%',))
        medicines = cursor.fetchall()
        cursor.close()
        conn.close()
        return render_template('search/search_results.html', medicines=medicines, query=search_query)
    return render_template('search/search_form.html')

@app.route('/medicine-details/<int:medicine_id>')
def medicine_details(medicine_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('search_medicine'))
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT m.MEDICINEID, m.MEDICINENAME, m.PRICE, m.MANUFACTURER, mc.CATEGORYNAME, mc.CATAGORYDETAILS
        FROM MEDICINES m
        LEFT JOIN MEDICINECATEGORY mc ON m.CATEGORYID = mc.CATEGORYID
        WHERE m.MEDICINEID = %s
    """
    cursor.execute(query, (medicine_id,))
    medicine = cursor.fetchone()
    cursor.close()
    conn.close()
    if not medicine:
        return render_template('404.html'), 404
    return render_template('search/medicine_details.html', medicine=medicine)

@app.route('/onlineorders')
def view_online_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    query = """
    SELECT 
        o.ORDERID,
        o.ORDERDATE,
        c.CUSTOMERNAME,
        o.DELIVERYADDRESS,
        sd.TOTALAMOUNT,
        COALESCE(m.MEDICINENAME, 'N/A') AS MEDICINENAME,
        COALESCE(sd.QUANTITY, 'N/A') AS QUANTITY
    FROM 
        ONLINEORDERS o
    JOIN CUSTOMERS c ON o.CUSTOMERID = c.CUSTOMERID
    JOIN SALESDETAILS sd ON o.SALEDETAILID = sd.SALEDETAILID
    LEFT JOIN MEDICINES m ON sd.MEDICINEID = m.MEDICINEID;
    """

    cursor.execute(query)
    orders = cursor.fetchall()

    cursor.close()
    conn.close()

    return render_template('onlineorders.html', orders=orders)

# --- Customer Routes ---
@app.route('/customer/login', methods=['GET', 'POST'])
def customer_login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('customer/login.html')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM CUSTOMERS WHERE EMAIL = %s AND PASSWORD = %s", (email, password))
        customer = cursor.fetchone()
        cursor.close()
        conn.close()
        if customer:
            session['user_id'] = customer['CUSTOMERID']
            session['user_name'] = customer['CUSTOMERNAME']
            session['role'] = 'customer'
            flash('Login successful!', 'success')
            return redirect(url_for('customer_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('customer/login.html')

@app.route('/customer/signup', methods=['GET', 'POST'])
def customer_signup():
    if request.method == 'POST':
        name = request.form['name']
        contact = request.form['contact']
        email = request.form['email']
        password = request.form['password']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('customer/signup.html')
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO CUSTOMERS (CUSTOMERNAME, CONTACT, EMAIL, PASSWORD) VALUES (%s, %s, %s, %s)",
                           (name, contact, email, password))
            conn.commit()
            flash('Account created successfully! Please log in.', 'success')
            return redirect(url_for('customer_login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('customer/signup.html')

@app.route('/customer/dashboard')
@login_required('customer')
def customer_dashboard():
    return render_template('customer/dashboard.html')

@app.route('/add-to-cart/<int:medicine_id>', methods=['POST'])
def add_to_cart(medicine_id):
    if 'user_id' not in session or session.get('role') != 'customer':
        flash('You must be logged in as a customer to add items to the cart.', 'warning')
        return redirect(url_for('customer_login'))

    cart = session.get('cart', {})
    medicine_id_str = str(medicine_id)
    try:
        quantity = int(request.form.get('quantity', 1))
        if quantity < 1:
            quantity = 1
    except (ValueError, TypeError):
        quantity = 1
    
    if medicine_id_str in cart:
        cart[medicine_id_str] += quantity
    else:
        cart[medicine_id_str] = quantity
        
    session['cart'] = cart
    flash('Item added to cart!', 'success')
    return redirect(url_for('cart_details'))

@app.route('/customer/cart', methods=['GET', 'POST'])
@login_required('customer')
def cart_details():
    cart_items_ids = session.get('cart', {})
    medicines_in_cart = []
    total_price = 0

    if cart_items_ids:
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return render_template('customer/cart_details.html', cart_items=[], total_price=0)
        cursor = conn.cursor(dictionary=True)
        
        medicine_ids = list(cart_items_ids.keys())
        if medicine_ids:
            query_placeholders = ','.join(['%s'] * len(medicine_ids))
            query = f"SELECT MEDICINEID, MEDICINENAME, PRICE FROM MEDICINES WHERE MEDICINEID IN ({query_placeholders})"
            cursor.execute(query, tuple(medicine_ids))
            medicines_data = {str(med['MEDICINEID']): med for med in cursor.fetchall()}

            for med_id, quantity in cart_items_ids.items():
                med_data = medicines_data.get(med_id)
                if med_data:
                    subtotal = med_data['PRICE'] * quantity
                    total_price += subtotal
                    medicines_in_cart.append({**med_data, 'quantity': quantity, 'subtotal': subtotal})
        
        cursor.close()
        conn.close()
    
    if request.method == 'POST':
        delivery_address = request.form.get('address')
        payment_method = request.form.get('payment')
        
        if not medicines_in_cart:
            flash('Your cart is empty. Please add items before placing an order.', 'warning')
            return redirect(url_for('cart_details'))

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Could not place order.', 'danger')
            return redirect(url_for('cart_details'))
        cursor = conn.cursor()
        try:
            customer_id = session['user_id']
            branch_id = 1 
            employee_id = 153398

            for item in medicines_in_cart:
                cursor.execute("""
                    INSERT INTO SALESDETAILS (SALEID, SALEDATE, BRANCHID, CUSTOMERID, EMPLOYEEID, PRICEPERUNIT, TOTALAMOUNT, PAYMENTMETHOD, MEDICINEID, QUANTITY)
                    VALUES (NULL, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s)
                """, (branch_id, customer_id, employee_id, item['PRICE'], item['subtotal'], payment_method, item['MEDICINEID'], item['quantity']))
                sale_detail_id = cursor.lastrowid

                cursor.execute("""
                    INSERT INTO ONLINEORDERS (CUSTOMERID, SALEDETAILID, ORDERDATE, DELIVERYADDRESS)
                    VALUES (%s, %s, NOW(), %s)
                """, (customer_id, sale_detail_id, delivery_address))

            conn.commit()
            session.pop('cart', None)
            flash('Your order has been placed successfully!', 'success')
            return redirect(url_for('previous_orders'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f"An error occurred while placing the order: {err}", 'danger')
        finally:
            cursor.close()
            conn.close()

    return render_template('customer/cart_details.html', cart_items=medicines_in_cart, total_price=total_price)

@app.route('/customer/previous-orders')
@login_required('customer')
def previous_orders():
    customer_id = session['user_id']
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('customer/previous_orders.html', orders=[])
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sd.SALEDATE, m.MEDICINENAME, sd.QUANTITY, sd.PRICEPERUNIT, sd.TOTALAMOUNT, sd.PAYMENTMETHOD, b.BRANCHNAME, oo.DELIVERYADDRESS
        FROM SALESDETAILS sd
        JOIN MEDICINES m ON sd.MEDICINEID = m.MEDICINEID
        JOIN BRANCHES b ON sd.BRANCHID = b.BRANCHID
        LEFT JOIN ONLINEORDERS oo ON sd.SALEDETAILID = oo.SALEDETAILID
        WHERE sd.CUSTOMERID = %s
        ORDER BY sd.SALEDATE DESC, sd.SALEDETAILID DESC
    """
    cursor.execute(query, (customer_id,))
    orders = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('customer/previous_orders.html', orders=orders)

# --- Employee Routes ---
@app.route('/employee/login', methods=['GET', 'POST'])
def employee_login():
    if request.method == 'POST':
        employee_id = request.form.get('employee_id')
        pin = request.form.get('pin')
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('employee/login.html')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM EMPLOYEES WHERE EMPLOYEEID = %s AND EMPLOYEEPIN = %s", (employee_id, pin))
        employee = cursor.fetchone()
        cursor.close()
        conn.close()
        if employee:
            session['user_id'] = employee['EMPLOYEEID']
            session['user_name'] = employee['EMPLOYEENAME']
            session['role'] = 'employee'
            flash('Login successful!', 'success')
            return redirect(url_for('employee_dashboard'))
        else:
            flash('Invalid credentials. Please try again.', 'danger')
    return render_template('employee/login.html')

@app.route('/employee/signup', methods=['GET', 'POST'])
def employee_signup():
    new_employee_id = None

    if request.method == 'POST':
        name = request.form.get('employee_name')
        contact = request.form.get('contact')
        pin = request.form.get('pin')
        designation = request.form.get('designation', 'Staff')
        branch_id = request.form.get('branch_id')

        if not contact or len(contact) < 7 or not contact.isdigit():
            flash('Contact number must be at least 7 digits and numeric.', 'danger')
            return redirect(url_for('employee_signup'))

        employee_id = int(contact[:7])
        email = f"{employee_id}@curepoint.com"

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('employee_signup'))

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO EMPLOYEES (EMPLOYEEID, EMPLOYEENAME, Email, EMPLOYEEPIN, DESIGNATION, CONTACT, BRANCHID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (employee_id, name, email, pin, designation, contact, branch_id))
            conn.commit()
            new_employee_id = employee_id
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/signup.html', branches=[], new_employee_id=new_employee_id)

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('employee/signup.html', branches=branches, new_employee_id=new_employee_id)

@app.route('/employee/dashboard')
@login_required('employee')
def employee_dashboard():
    return render_template('employee/dashboard.html')

@app.route('/employee/medicine-category')
@login_required('employee')
def employee_medicine_category():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/medicine_category.html', categories=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM MEDICINECATEGORY")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/medicine_category.html', categories=categories)

@app.route('/employee/medicine-category/add', methods=['GET', 'POST'])
@login_required('employee')
def employee_add_medicine_category():
    if request.method == 'POST':
        name = request.form['categoryname']
        details = request.form['categorydetails']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('employee_add_medicine_category'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO MEDICINECATEGORY (CATEGORYNAME, CATAGORYDETAILS) VALUES (%s, %s)", (name, details))
            conn.commit()
            flash('Medicine category added successfully!', 'success')
            return redirect(url_for('employee_medicine_category'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('employee/add_edit_medicine_category.html', action='Add', category=None)

@app.route('/employee/medicine-category/edit/<int:category_id>', methods=['GET', 'POST'])
@login_required('employee')
def employee_edit_medicine_category(category_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicine_category'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['categoryname']
        details = request.form['categorydetails']
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("UPDATE MEDICINECATEGORY SET CATEGORYNAME = %s, CATAGORYDETAILS = %s WHERE CATEGORYID = %s", (name, details, category_id))
            conn.commit()
            flash('Medicine category updated successfully!', 'success')
            return redirect(url_for('employee_medicine_category'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor.execute("SELECT * FROM MEDICINECATEGORY WHERE CATEGORYID = %s", (category_id,))
    category = cursor.fetchone()
    cursor.close()
    conn.close()
    if not category:
        return render_template('404.html'), 404
    return render_template('employee/add_edit_medicine_category.html', action='Edit', category=category)

@app.route('/employee/medicine-category/delete/<int:category_id>', methods=['POST'])
@login_required('employee')
def employee_delete_medicine_category(category_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicine_category'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM MEDICINECATEGORY WHERE CATEGORYID = %s", (category_id,))
        conn.commit()
        flash('Medicine category deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting category. It might be in use by medicines. Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('employee_medicine_category'))

@app.route('/employee/medicines')
@login_required('employee')
def employee_medicines():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/medicines.html', medicines=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT m.*, mc.CATEGORYNAME FROM MEDICINES m LEFT JOIN MEDICINECATEGORY mc ON m.CATEGORYID = mc.CATEGORYID")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/medicines.html', medicines=medicines)

@app.route('/employee/medicine/add', methods=['GET', 'POST'])
@login_required('employee')
def employee_add_medicine():
    if request.method == 'POST':
        name = request.form['medicinename']
        categoryid = request.form.get('categoryid')
        manufacturer = request.form['manufacturer']
        price = request.form['price']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('employee_add_medicine'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO MEDICINES (MEDICINENAME, CATEGORYID, MANUFACTURER, PRICE) VALUES (%s, %s, %s, %s)",
                           (name, categoryid if categoryid else None, manufacturer, price))
            conn.commit()
            flash('Medicine added successfully!', 'success')
            return redirect(url_for('employee_medicines'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/add_edit_medicine.html', action='Add', medicine=None, categories=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT CATEGORYID, CATEGORYNAME FROM MEDICINECATEGORY")
    categories = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/add_edit_medicine.html', action='Add', medicine=None, categories=categories)

@app.route('/employee/medicine/edit/<int:medicine_id>', methods=['GET', 'POST'])
@login_required('employee')
def employee_edit_medicine(medicine_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicines'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['medicinename']
        categoryid = request.form.get('categoryid')
        manufacturer = request.form['manufacturer']
        price = request.form['price']
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("UPDATE MEDICINES SET MEDICINENAME=%s, CATEGORYID=%s, MANUFACTURER=%s, PRICE=%s WHERE MEDICINEID=%s",
                                  (name, categoryid if categoryid else None, manufacturer, price, medicine_id))
            conn.commit()
            flash('Medicine updated successfully!', 'success')
            return redirect(url_for('employee_medicines'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor.execute("SELECT * FROM MEDICINES WHERE MEDICINEID = %s", (medicine_id,))
    medicine = cursor.fetchone()
    
    cursor.execute("SELECT CATEGORYID, CATEGORYNAME FROM MEDICINECATEGORY")
    categories = cursor.fetchall()
    
    cursor.close()
    conn.close()
    if not medicine:
        return render_template('404.html'), 404
    return render_template('employee/add_edit_medicine.html', action='Edit', medicine=medicine, categories=categories)

@app.route('/employee/medicine/delete/<int:medicine_id>', methods=['POST'])
@login_required('employee')
def employee_delete_medicine(medicine_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicines'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM MEDICINES WHERE MEDICINEID = %s", (medicine_id,))
        conn.commit()
        flash('Medicine deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting medicine. Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('employee_medicines'))

@app.route('/employee/medicine-stock')
@login_required('employee')
def employee_medicine_stock():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/medicine_stock.html', stocks=[])
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT ms.*, b.BRANCHNAME, m.MEDICINENAME 
        FROM MEDICINESTOCK ms 
        JOIN BRANCHES b ON ms.BRANCHID = b.BRANCHID 
        JOIN MEDICINES m ON ms.MEDICINEID = m.MEDICINEID
    """
    cursor.execute(query)
    stocks = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/medicine_stock.html', stocks=stocks)

@app.route('/employee/medicine-stock/add', methods=['GET', 'POST'])
@login_required('employee')
def employee_add_medicine_stock():
    if request.method == 'POST':
        stockid = request.form['stockid']
        branchid = request.form['branchid']
        medicineid = request.form['medicineid']
        quantity = request.form['quantity']
        expirydate = request.form['expirydate']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('employee_add_medicine_stock'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO MEDICINESTOCK (STOCKID, BRANCHID, MEDICINEID, QUANTITY, EXPIRYDATE) VALUES (%s, %s, %s, %s, %s)",
                           (stockid, branchid, medicineid, quantity, expirydate))
            conn.commit()
            flash('Stock record added successfully!', 'success')
            return redirect(url_for('employee_medicine_stock'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/add_edit_medicine_stock.html', action='Add', stock=None, branches=[], medicines=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.execute("SELECT MEDICINEID, MEDICINENAME FROM MEDICINES")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/add_edit_medicine_stock.html', action='Add', stock=None, branches=branches, medicines=medicines)

@app.route('/employee/medicine-stock/edit/<int:stock_id>', methods=['GET', 'POST'])
@login_required('employee')
def employee_edit_medicine_stock(stock_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicine_stock'))
    if request.method == 'POST':
        branchid = request.form['branchid']
        medicineid = request.form['medicineid']
        quantity = request.form['quantity']
        expirydate = request.form['expirydate']
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("UPDATE MEDICINESTOCK SET BRANCHID=%s, MEDICINEID=%s, QUANTITY=%s, EXPIRYDATE=%s WHERE STOCKID=%s",
                                  (branchid, medicineid, quantity, expirydate, stock_id))
            conn.commit()
            flash('Stock record updated successfully!', 'success')
            return redirect(url_for('employee_medicine_stock'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM MEDICINESTOCK WHERE STOCKID = %s", (stock_id,))
    stock = cursor.fetchone()
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.execute("SELECT MEDICINEID, MEDICINENAME FROM MEDICINES")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    if not stock:
        return render_template('404.html'), 404
    return render_template('employee/add_edit_medicine_stock.html', action='Edit', stock=stock, branches=branches, medicines=medicines)

@app.route('/employee/medicine-stock/delete/<int:stock_id>', methods=['POST'])
@login_required('employee')
def employee_delete_medicine_stock(stock_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_medicine_stock'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM MEDICINESTOCK WHERE STOCKID = %s", (stock_id,))
        conn.commit()
        flash('Stock record deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('employee_medicine_stock'))

@app.route('/employee/sales')
@login_required('employee')
def employee_sales():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('employee/sales.html', sales=[])
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT SALEID, SALEDATE, CUSTOMERID, SUM(TOTALAMOUNT) as GrandTotal, PAYMENTMETHOD
        FROM SALESDETAILS 
        GROUP BY SALEID, SALEDATE, CUSTOMERID, PAYMENTMETHOD
        ORDER BY SALEDATE DESC, SALEID DESC
    """
    cursor.execute(query)
    sales = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/sales.html', sales=sales)

@app.route('/employee/add-sale', methods=['GET', 'POST'])
@login_required('employee')
def employee_add_sale():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_dashboard'))
    cursor = conn.cursor(dictionary=True)

    if request.method == 'POST':
        customerid = request.form.get('customerid')
        payment_method = request.form.get('payment')
        employee_id = session['user_id']
        
        cursor.execute("SELECT BRANCHID FROM EMPLOYEES WHERE EMPLOYEEID = %s", (employee_id,))
        branch_id = cursor.fetchone()['BRANCHID']
        
        cursor.execute("SELECT MAX(SALEID) as max_id FROM SALESDETAILS")
        max_id = cursor.fetchone()['max_id']
        new_sale_id = (max_id or 0) + 1

        items_to_add = []
        for i in range(5):
            med_id = request.form.get(f'medicineid_{i}')
            quantity = request.form.get(f'quantity_{i}')
            if med_id and quantity and int(quantity) > 0:
                items_to_add.append({'med_id': med_id, 'quantity': int(quantity)})
        
        if not items_to_add:
            flash('Please add at least one medicine to the sale.', 'warning')
            return redirect(url_for('employee_add_sale'))

        try:
            for item in items_to_add:
                cursor.execute("SELECT PRICE FROM MEDICINES WHERE MEDICINEID = %s", (item['med_id'],))
                price_per_unit = cursor.fetchone()['PRICE']
                total_amount = price_per_unit * item['quantity']
                
                cursor.execute("""
                    INSERT INTO SALESDETAILS (SALEID, SALEDATE, BRANCHID, CUSTOMERID, EMPLOYEEID, PRICEPERUNIT, TOTALAMOUNT, PAYMENTMETHOD, MEDICINEID, QUANTITY)
                    VALUES (%s, CURDATE(), %s, %s, %s, %s, %s, %s, %s, %s)
                """, (new_sale_id, branch_id, customerid, employee_id, price_per_unit, total_amount, payment_method, item['med_id'], item['quantity']))
            
            conn.commit()
            flash(f'Sale (ID: {new_sale_id}) created successfully!', 'success')
            return redirect(url_for('employee_sales'))
        except mysql.connector.Error as err:
            conn.rollback()
            flash(f'Error creating sale: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    cursor.execute("SELECT CUSTOMERID, CUSTOMERNAME FROM CUSTOMERS")
    customers = cursor.fetchall()
    cursor.execute("SELECT MEDICINEID, MEDICINENAME, PRICE FROM MEDICINES")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/add_sale.html', customers=customers, medicines=medicines)

@app.route('/employee/sales-item/<int:sale_id>')
@login_required('employee')
def employee_sales_item(sale_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('employee_sales'))
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT sd.*, m.MEDICINENAME, c.CUSTOMERNAME, e.EMPLOYEENAME
        FROM SALESDETAILS sd
        LEFT JOIN MEDICINES m ON sd.MEDICINEID = m.MEDICINEID
        LEFT JOIN CUSTOMERS c ON sd.CUSTOMERID = c.CUSTOMERID
        LEFT JOIN EMPLOYEES e ON sd.EMPLOYEEID = e.EMPLOYEEID
        WHERE sd.SALEID = %s
    """
    cursor.execute(query, (sale_id,))
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('employee/sales_item.html', items=items, sale_id=sale_id)

@app.route('/employee/online-orders')
@login_required('employee')
def employee_online_orders():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("""
        SELECT 
            o.ORDERID,
            o.ORDERDATE,
            c.CUSTOMERNAME,
            o.DELIVERYADDRESS,
            sd.TOTALAMOUNT,
            m.MEDICINENAME,
            sd.QUANTITY
        FROM 
            ONLINEORDERS o
        JOIN CUSTOMERS c ON o.CUSTOMERID = c.CUSTOMERID
        JOIN SALESDETAILS sd ON o.SALEDETAILID = sd.SALEDETAILID
        LEFT JOIN MEDICINES m ON sd.MEDICINEID = m.MEDICINEID
        ORDER BY o.ORDERDATE DESC;
    """)

    rows = cursor.fetchall()
    conn.close()

    for row in rows:
        row['MEDICINENAME'] = row['MEDICINENAME'] or 'N/A'
        row['QUANTITY'] = row['QUANTITY'] or 'N/A'

    return render_template('employee/online_orders.html', orders=rows)






# --- Admin Routes ---
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        employee_id = request.form['admin_id']
        pin = request.form['pin']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return render_template('admin/login.html')
        cursor = conn.cursor(dictionary=True)
        cursor.execute("""
            SELECT * FROM EMPLOYEES 
            WHERE EMPLOYEEID = %s AND EMPLOYEEPIN = %s AND DESIGNATION IN ('Admin', 'Branch Manager')
        """, (employee_id, pin))
        admin = cursor.fetchone()
        cursor.close()
        conn.close()
        if admin:
            session['user_id'] = admin['EMPLOYEEID']
            session['user_name'] = admin['EMPLOYEENAME']
            session['role'] = 'admin'
            flash('Admin login successful!', 'success')
            return redirect(url_for('admin_dashboard'))
        else:
            flash('Invalid credentials or not an admin.', 'danger')
    return render_template('admin/login.html')

@app.route('/admin/signup', methods=['GET', 'POST'])
def admin_signup():
    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        contact = request.form['contact']
        pin = request.form['pin']
        designation = request.form['designation']
        branch_id = request.form['branch_id']

        if not contact or len(contact) < 7 or not contact.isdigit():
            flash('Phone number must be at least 7 digits and contain only numbers.', 'danger')
            return redirect(url_for('admin_signup'))

        employee_id = int(contact[:7])

        conn = get_db_connection()
        if conn is None:
            flash('Database connection error. Please try again later.', 'danger')
            return redirect(url_for('admin_signup'))

        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO EMPLOYEES (EMPLOYEEID, EMPLOYEENAME, Email, EMPLOYEEPIN, DESIGNATION, CONTACT, BRANCHID)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (employee_id, name, email, pin, designation, contact, branch_id))
            conn.commit()
            flash(f'Admin account created successfully! Your Admin ID is: {employee_id}', 'success')
            return redirect(url_for('admin_login'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/signup.html', branches=[])

    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()

    return render_template('admin/signup.html', branches=branches)

@app.route('/admin/dashboard')
@login_required('admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/branches')
@login_required('admin')
def admin_branches():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/branches.html', branches=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT * FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/branches.html', branches=branches)

@app.route('/admin/branch/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_branch():
    if request.method == 'POST':
        name = request.form['branchname']
        location = request.form['location']
        manager_num = request.form['managernumber']
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('admin_add_branch'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO BRANCHES (BRANCHNAME, LOCATION, BRANCHMANAGERNUBMBER) VALUES (%s, %s, %s)",
                           (name, location, manager_num))
            conn.commit()
            flash('Branch added successfully!', 'success')
            return redirect(url_for('admin_branches'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    return render_template('admin/add_edit_branch.html', action='Add', branch=None)

@app.route('/admin/branch/edit/<int:branch_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_branch(branch_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_branches'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['branchname']
        location = request.form['location']
        manager_num = request.form['managernumber']
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("""
                UPDATE BRANCHES SET BRANCHNAME = %s, LOCATION = %s, BRANCHMANAGERNUBMBER = %s
                WHERE BRANCHID = %s
            """, (name, location, manager_num, branch_id))
            conn.commit()
            flash('Branch updated successfully!', 'success')
            return redirect(url_for('admin_branches'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()
    
    cursor.execute("SELECT * FROM BRANCHES WHERE BRANCHID = %s", (branch_id,))
    branch = cursor.fetchone()
    cursor.close()
    conn.close()
    if not branch:
        return render_template('404.html'), 404
    return render_template('admin/add_edit_branch.html', action='Edit', branch=branch)

@app.route('/admin/branch/delete/<int:branch_id>', methods=['POST'])
@login_required('admin')
def admin_delete_branch(branch_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_branches'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM BRANCHES WHERE BRANCHID = %s", (branch_id,))
        conn.commit()
        flash('Branch deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error deleting branch. It might be in use by employees. Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_branches'))

@app.route('/admin/suppliers')
@login_required('admin')
def admin_suppliers():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/suppliers.html', suppliers=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, m.MEDICINENAME FROM SUPPLIERS s LEFT JOIN MEDICINES m ON s.MEDICINEID = m.MEDICINEID")
    suppliers = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/suppliers.html', suppliers=suppliers)

@app.route('/admin/supplier/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_supplier():
    if request.method == 'POST':
        name = request.form['suppliername']
        contact = request.form['contact']
        medicine_id = request.form.get('medicineid')
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('admin_add_supplier'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO SUPPLIERS (SUPPLIERNAME, CONTACT, MEDICINEID) VALUES (%s, %s, %s)",
                           (name, contact, medicine_id if medicine_id else None))
            conn.commit()
            flash('Supplier added successfully!', 'success')
            return redirect(url_for('admin_suppliers'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()
    
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/add_edit_supplier.html', action='Add', supplier=None, medicines=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT MEDICINEID, MEDICINENAME FROM MEDICINES")
    medicines = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/add_edit_supplier.html', action='Add', supplier=None, medicines=medicines)

@app.route('/admin/supplier/edit/<int:supplier_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_supplier(supplier_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_suppliers'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        name = request.form['suppliername']
        contact = request.form['contact']
        medicine_id = request.form.get('medicineid')
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("UPDATE SUPPLIERS SET SUPPLIERNAME = %s, CONTACT = %s, MEDICINEID = %s WHERE SUPPLIERID = %s",
                                  (name, contact, medicine_id if medicine_id else None, supplier_id))
            conn.commit()
            flash('Supplier updated successfully!', 'success')
            return redirect(url_for('admin_suppliers'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor.execute("SELECT * FROM SUPPLIERS WHERE SUPPLIERID = %s", (supplier_id,))
    supplier = cursor.fetchone()
    
    cursor.execute("SELECT MEDICINEID, MEDICINENAME FROM MEDICINES")
    medicines = cursor.fetchall()
    
    cursor.close()
    conn.close()
    if not supplier:
        return render_template('404.html'), 404
    return render_template('admin/add_edit_supplier.html', action='Edit', supplier=supplier, medicines=medicines)

@app.route('/admin/supplier/delete/<int:supplier_id>', methods=['POST'])
@login_required('admin')
def admin_delete_supplier(supplier_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_suppliers'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SUPPLIERS WHERE SUPPLIERID = %s", (supplier_id,))
        conn.commit()
        flash('Supplier deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_suppliers'))

@app.route('/admin/shifts')
@login_required('admin')
def admin_shifts():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/shifts.html', shifts=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT s.*, e.EMPLOYEENAME FROM SHIFTS s LEFT JOIN EMPLOYEES e ON s.EMPLOYEEID = e.EMPLOYEEID")
    shifts = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/shifts.html', shifts=shifts)

@app.route('/admin/shift/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_shift():
    if request.method == 'POST':
        shiftid = request.form['shiftid']
        shiftname = request.form['shiftname']
        starttime = request.form['starttime']
        endtime = request.form['endtime']
        employeeid = request.form.get('employeeid')
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('admin_add_shift'))
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO SHIFTS (SHIFTID, SHIFTNAME, STARTTIME, ENDTIME, EMPLOYEEID) VALUES (%s, %s, %s, %s, %s)",
                           (shiftid, shiftname, starttime, endtime, employeeid if employeeid else None))
            conn.commit()
            flash('Shift added successfully!', 'success')
            return redirect(url_for('admin_shifts'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/add_edit_shift.html', action='Add', shift=None, employees=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT EMPLOYEEID, EMPLOYEENAME FROM EMPLOYEES")
    employees = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/add_edit_shift.html', action='Add', shift=None, employees=employees)

@app.route('/admin/shift/edit/<int:shift_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_shift(shift_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_shifts'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        shiftname = request.form['shiftname']
        starttime = request.form['starttime']
        endtime = request.form['endtime']
        employeeid = request.form.get('employeeid')
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("UPDATE SHIFTS SET SHIFTNAME = %s, STARTTIME = %s, ENDTIME = %s, EMPLOYEEID = %s WHERE SHIFTID = %s",
                                  (shiftname, starttime, endtime, employeeid if employeeid else None, shift_id))
            conn.commit()
            flash('Shift updated successfully!', 'success')
            return redirect(url_for('admin_shifts'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor.execute("SELECT * FROM SHIFTS WHERE SHIFTID = %s", (shift_id,))
    shift = cursor.fetchone()
    
    cursor.execute("SELECT EMPLOYEEID, EMPLOYEENAME FROM EMPLOYEES")
    employees = cursor.fetchall()
    
    cursor.close()
    conn.close()
    if not shift:
        return render_template('404.html'), 404
    return render_template('admin/add_edit_shift.html', action='Edit', shift=shift, employees=employees)

@app.route('/admin/shift/delete/<int:shift_id>', methods=['POST'])
@login_required('admin')
def admin_delete_shift(shift_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_shifts'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM SHIFTS WHERE SHIFTID = %s", (shift_id,))
        conn.commit()
        flash('Shift deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_shifts'))

@app.route('/admin/attendance')
@login_required('admin')
def admin_attendance():
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/attendance.html', attendances=[])
    cursor = conn.cursor(dictionary=True)
    query = """
        SELECT a.*, e.EMPLOYEENAME, s.SHIFTNAME, b.BRANCHNAME 
        FROM ATTENDANCE a
        LEFT JOIN EMPLOYEES e ON a.EMPLOYEEID = e.EMPLOYEEID
        LEFT JOIN SHIFTS s ON a.SHIFTID = s.SHIFTID
        LEFT JOIN BRANCHES b ON a.BRANCHID = b.BRANCHID
    """
    cursor.execute(query)
    attendances = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/attendance.html', attendances=attendances)

@app.route('/admin/attendance/add', methods=['GET', 'POST'])
@login_required('admin')
def admin_add_attendance():
    if request.method == 'POST':
        employeeid = request.form.get('employeeid')
        shiftid = request.form.get('shiftid')
        branchid = request.form.get('branchid')
        attendancedate = request.form.get('attendancedate')
        timein = request.form.get('timein')
        timeout = request.form.get('timeout')
        conn = get_db_connection()
        if conn is None:
            flash('Database connection error.', 'danger')
            return redirect(url_for('admin_add_attendance'))
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO ATTENDANCE (EMPLOYEEID, SHIFTID, BRANCHID, ATTENDANCEDATE, TIMEIN, TIMEOUT) 
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (employeeid, shiftid, branchid, attendancedate, timein, timeout))
            conn.commit()
            flash('Attendance record added successfully!', 'success')
            return redirect(url_for('admin_attendance'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            cursor.close()
            conn.close()

    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return render_template('admin/add_edit_attendance.html', action='Add', attendance=None, employees=[], shifts=[], branches=[])
    cursor = conn.cursor(dictionary=True)
    cursor.execute("SELECT EMPLOYEEID, EMPLOYEENAME FROM EMPLOYEES")
    employees = cursor.fetchall()
    cursor.execute("SELECT SHIFTID, SHIFTNAME FROM SHIFTS")
    shifts = cursor.fetchall()
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    cursor.close()
    conn.close()
    return render_template('admin/add_edit_attendance.html', action='Add', attendance=None, employees=employees, shifts=shifts, branches=branches)

@app.route('/admin/attendance/edit/<int:attendance_id>', methods=['GET', 'POST'])
@login_required('admin')
def admin_edit_attendance(attendance_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_attendance'))
    cursor = conn.cursor(dictionary=True)
    if request.method == 'POST':
        employeeid = request.form.get('employeeid')
        shiftid = request.form.get('shiftid')
        branchid = request.form.get('branchid')
        attendancedate = request.form.get('attendancedate')
        timein = request.form.get('timein')
        timeout = request.form.get('timeout')
        update_cursor = conn.cursor()
        try:
            update_cursor.execute("""
                UPDATE ATTENDANCE SET EMPLOYEEID=%s, SHIFTID=%s, BRANCHID=%s, ATTENDANCEDATE=%s, TIMEIN=%s, TIMEOUT=%s 
                WHERE ATTENDANCEID=%s
            """, (employeeid, shiftid, branchid, attendancedate, timein, timeout, attendance_id))
            conn.commit()
            flash('Attendance record updated successfully!', 'success')
            return redirect(url_for('admin_attendance'))
        except mysql.connector.Error as err:
            flash(f'Error: {err}', 'danger')
        finally:
            update_cursor.close()

    cursor.execute("SELECT * FROM ATTENDANCE WHERE ATTENDANCEID = %s", (attendance_id,))
    attendance = cursor.fetchone()
    
    cursor.execute("SELECT EMPLOYEEID, EMPLOYEENAME FROM EMPLOYEES")
    employees = cursor.fetchall()
    cursor.execute("SELECT SHIFTID, SHIFTNAME FROM SHIFTS")
    shifts = cursor.fetchall()
    cursor.execute("SELECT BRANCHID, BRANCHNAME FROM BRANCHES")
    branches = cursor.fetchall()
    
    cursor.close()
    conn.close()
    if not attendance:
        return render_template('404.html'), 404
    return render_template('admin/add_edit_attendance.html', action='Edit', attendance=attendance, employees=employees, shifts=shifts, branches=branches)

@app.route('/admin/attendance/delete/<int:attendance_id>', methods=['POST'])
@login_required('admin')
def admin_delete_attendance(attendance_id):
    conn = get_db_connection()
    if conn is None:
        flash('Database connection error.', 'danger')
        return redirect(url_for('admin_attendance'))
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM ATTENDANCE WHERE ATTENDANCEID = %s", (attendance_id,))
        conn.commit()
        flash('Attendance record deleted successfully.', 'success')
    except mysql.connector.Error as err:
        flash(f'Error: {err}', 'danger')
    finally:
        cursor.close()
        conn.close()
    return redirect(url_for('admin_attendance'))

# --- Logout ---
@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))

# --- Error Handler ---
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == '__main__':
    app.run(debug=True)



