#!/usr/bin/python3
"""
Flask app to submit and retrieve student billing data from MySQL using PyMySQL
"""
from flask import Flask, render_template, request, redirect, jsonify, render_template_string, make_response, session, url_for, flash
from io import BytesIO
from xhtml2pdf import pisa
import pymysql
from pymysql.cursors import DictCursor
from functools import wraps

app = Flask(__name__)

app.secret_key = "supersecretkey123"

# MySQL connection setup using PyMySQL
conn = pymysql.connect(
    host="localhost",
    user="root",
    password="1412",
    database="school_db",
    cursorclass=DictCursor,  # This makes all rows dictionary-based
    charset='utf8mb4'
)

# File upload folder
UPLOAD_FOLDER = "static/uploads"
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'doc','docx','xml', 'xlsx', 'pptx', 'pdf', 'txt'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# --- Login Required ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page", "error")
            return redirect(url_for("signin"))
        return f(*args, **kwargs)
    return decorated_function


# --- Role Required ---
def role_required(*roles):
    def wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if "role" not in session or session["role"] not in roles:
                flash("You do not have permission to access this page", "error")
                return redirect(url_for("dashboard"))
            return f(*args, **kwargs)
        return decorated_function
    return wrapper

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        row = cursor.fetchone()
        cursor.close()

        # Check if user exists and verify password hash
        if row is None or not check_password_hash(row["password"], password):
            flash("Invalid username or password!", "error")
            return redirect(url_for("signin"))

    
        # Store session with role
        session["user_id"] = row["id"]
        session["username"] = username
        session["role"] = row["role"]

        # ✅ Login successful
        flash("Login successful!", "success")
        return redirect(url_for("home"))
    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        username = request.form.get("username")
        phone=request.form.get("no")
        password = request.form.get("password")
        

        # Check for  the phone no 
        if  phone :
            cursor = conn.cursor()
            cursor.execute(
                    "INSERT INTO users (username, phone, password) VALUES (%s, %s, %s)",
                    (username, phone, hashed_password)
                    )
            conn.commit()
            cursor.close()
            flash("Account created successfully!", "success")
            return redirect(url_for("signin"))
        
        # Or skip the   if 
        cursor=conn.cursor()
        cursor.excute(
                "INSERT INTO users(Username, password)VALUES(%s, %s)",
                (username, password)
                )
        flash("Account created successfully!", "success")
        return redirect(url_for("signup"))

        # Check if username already exists
        if username in users:
            flash("Username already exists!", "error")
            return redirect(url_for("signup"))

        # Save hashed password
        users[username] = generate_password_hash(password)
        flash("Sign-up successful! You can now log in.", "success")
        return redirect(url_for("signin"))

    return render_template("signup.html")




@app.route('/manage')
@login_required
@role_required("admin")
def form():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM billing")
            records = cursor.fetchall()

            project_records = []
            printed_records = []

            for row in records:
                if row['status'] == 'printed' and row['binding'] != 0:
                    printed_records.append(row)
                elif row['binding'] !=0:
                    project_records.append(row)

        return render_template('form.html', records=records, prints=printed_records, projects=project_records)

    except Exception as e:
        return f"Error loading records: {e}"



@app.route('/search', methods=['GET'])
@login_required
@role_required("admin")
def search():
    student_id = request.args.get('student_id', '').strip()
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM billing WHERE student_id = %s", (student_id,))
            records = cursor.fetchall()
        return render_template('form.html', records=records)
    except Exception as e:
        return f"Search Error: {e}"

@app.route('/upload', methods=['POST', 'GET'])
@login_required
def upload_page():

    if request.method == 'POST':
        student_id = session['user_id']
        file = request.files["file"]

        try:
            if file and allowed_file(file.filename):
                # Create upload folder if not exists
                os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

                # Save file
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filepath)
                
                #save to database  
                with conn.cursor() as cursor:
                    cursor.execute(
                            "INSERT INTO work (student_id, filepath) VALUES (%s, %s)",
                            (student_id, filepath)
               @login_required
             )
                    conn.commit()
                    flash("File uploaded successfully!", "success")
                    return redirect(url_for('upload_page'))
            else :
                flash("You have the wrong file extension")
                return  redirect(url_for('upload_page'))
        except Exception as e:
            flash("Database Error: {e}")
            return redirect(url_for('upload_page'))

    return render_template('print.html')


@app.route('/update', methods=['POST'])
@login_required
@role_required("admin")
def update():
    student_id = request.form.get('student_id', '').strip()
    name = request.form.get('name', '').strip()
    amount = request.form.get('amount', '').strip()
    binding = request.form.get('binding', '').strip()
    status = request.form.get('status', '').strip()

    fields = []
    values = []

    if name:
        fields.append("name = %s")
        values.append(name)
    if amount:
        fields.append("amount = %s")
        values.append(amount)
    if binding:
        fields.append("binding = %s")
        values.append(binding)
    if status:
        fields.append("status = %s")
        values.append(status)

    if not fields:
        return "No fields to update."

    values.append(student_id)

    try:
        with conn.cursor() as cursor:
            query = f"UPDATE billing SET {', '.join(fields)} WHERE student_id = %s"
            cursor.execute(query, values)
        conn.commit()
        return redirect('/')
    except Exception as e:
        return f"Update Error: {e}"


@app.route('/download')
@login_required
@role_required("admin")
def download_pdf():
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT id, student_id, name, status FROM billing WHERE status='printed' ORDER BY id ASC")
            data = cursor.fetchall()
    except Exception as e:
        return f"PDF Generation Error: {e}"

    html = render_template_string("""
        <html>
        <head><meta charset="UTF-8"></head>
        <body>
        <h2>Billing Report</h2>
        <table border="1" cellspacing="0" cellpadding="4">
            <tr><th>ID</th><th>Student ID</th><th>Name</th><th>Status</th></tr>
            {% for row in data %}
            <tr>
                <td>{{ loop.index }}</td>
                <td>{{ row.student_id }}</td>
                <td>{{ row.name }}</td>
                <td>{{ row.status }}</td>
            </tr>
            {% endfor %}
        </table>
        </body>
        </html>
    """, data=data)

    pdf_buffer = BytesIO()
    pisa_status = pisa.CreatePDF(html, dest=pdf_buffer)
    if pisa_status.err:
        return "Error generating PDF"

    response = make_response(pdf_buffer.getvalue())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = 'attachment; filename=report.pdf'
    return response

@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "success")
    return redirect(url_for("signin"))


if __name__ == '__main__':
    app.run(debug=True)

