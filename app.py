#!/usr/bin/python3
"""
Flask app to submit and retrieve student billing data from MySQL using PyMySQL
"""
from flask import Flask, render_template, request, redirect, jsonify, render_template_string, make_response, session, url_for, flash
from io import BytesIO
from xhtml2pdf import pisa
from urllib.parse import urlparse, urljoin
import pymysql
from pymysql.cursors import DictCursor
from functools import wraps
import traceback
import hashlib
import os 
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

app.secret_key = "supersecretkey123"

# MySQL connection setup using PyMySQL
conn = pymysql.connect(
    host=os.getenv('dbhost'),
    user=os.getenv('dbuser'),
    password=os.getenv('pss'),
    database=os.getenv('db'),
    cursorclass=DictCursor,  # This makes all rows dictionary-based
    charset='utf8mb4'
)

# File upload folder
UPLOAD_FOLDER = os.getenv('mdir')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'doc','docx','xml', 'xlsx', 'pptx', 'pdf', 'txt'}

# Function to check allowed file types
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def hash_value(value: str) -> str:
    """
    Hash a string value using SHA-256.

    :param value: Input string to hash
    :return: SHA-256 hexadecimal digest
    """
    return hashlib.sha256(value.encode('utf-8')).hexdigest()


# --- Login Required ---
def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "user_id" not in session:
            flash("You must be logged in to access this page", "error")
            return redirect(url_for("signin", next=request.url))
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

def is_safe_url(target):
    ref = urlparse(request.host_url)
    test = urlparse(urljoin(request.host_url, target))
    return test.scheme in ("http", "https") and ref.netloc == test.netloc

def get_images(folder):
    """Return list of image filenames from a static subfolder."""
    path = os.path.join(app.static_folder, "images", folder)
    if not os.path.exists(path):
        return []

    return [
        f for f in os.listdir(path)
        if f.lower().endswith((".png", ".jpg", ".jpeg", ".gif", ".webp"))
    ]


def send_email(recipient_email, subject, body):
    MAIL_SERVER=os.getenv("MAIL_SERVER"),
    MAIL_PORT=int(os.getenv("MAIL_PORT")),
    MAIL_USE_TLS=os.getenv("MAIL_USE_TLS") == "True",
    MAIL_USE_SSL=os.getenv("MAIL_USE_SSL") == "True",
    MAIL_USERNAME=os.getenv("MAIL_USERNAME"),
    MAIL_PASSWORD=os.getenv("MAIL_PASSWORD"),
    MAIL_DEFAULT_SENDER=os.getenv("MAIL_DEFAULT_SENDER")
    msg = MIMEText(body, "html")

    msg["Subject"] = subject
    msg["From"] = sender_email
    msg["To"] = recipient_email

    try:
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            if smtp_tls:
                server.starttls()
            server.login(smtp_user, smtp_password)
            server.sendmail(sender_email, [recipient_email], msg.as_string())
        print("✅ Email sent to", recipient_email)
        return "Email sent successfully"  # ✅ Added
    except Exception as e:
        print("❌ Email failed:", e)
        return f"Failed to send email: {str(e)}"  # ✅ Added

@app.route("/")
def home():
    maintenance_imgs = get_images("maintainance")
    printing_imgs = get_images("cyber")
    game_imgs = get_images("games")
    library_imgs = get_images("store")
    support_imgs = get_images("customer_care")
    return render_template(
        "index.html",
        maintenance_imgs=maintenance_imgs,
        printing_imgs=printing_imgs,
        game_imgs=game_imgs,
        library_imgs=library_imgs,
        support_imgs=support_imgs
    )

@app.route("/maintenance")
def maintenance():
    return render_template("maintenance.html")


@app.route("/printing")
@login_required
def printing():
    return render_template("print.html")


@app.route("/networking")
def networking():
    return render_template("networking.html")


@app.route("/development")
def development():
    return render_template("development.html")


@app.route("/support")
def support():
    return render_template("support.html")


@app.route("/cloud")
def cloud():
    return render_template("cloud.html")

@app.route("/signin", methods=["GET", "POST"])
def signin():
    if request.method == 'POST':
        try :
            username = request.form.get("username")
            password = request.form.get("password")
            next_page = request.form.get("next")
            hashed_password = hash_value("password")
            cursor = conn.cursor(dictionary=True)
            cursor.execute("SELECT password FROM users WHERE email = %s", (username,))
            row = cursor.fetchone()
            cursor.close()

            #check for a  secure  connection
            if not is_safe_url(next_page):
                flash("Kindly make sure your connection is secure")
                return redirect(url_for("home"))

            # Check if user exists and verify password hash
            if row.password==hashed_password:
                # Store session with role
                session["user_id"] = row["id"]
                session["username"] = username
                session["role"] = row["role"]

                # ✅ Login successful
                flash("Login successful!", "success")
                return redirect(next_page)
            else:
                flash("invalid credetials")
                return redirect(url_for("home"))

        except Exception as e:
            flash(f"Database error: {str(e)}", "error")
            return redirect(url_for("home"))
    
    # ✅ THIS FIXES THE TypeError
    return render_template("signin.html")

@app.route("/signup", methods=["GET", "POST"])
def signup():
    if request.method == "POST":
        try:
            recipient = request.form.get("email")
            password = request.form.get("password")

            subject = "Welcome to Ressen Technologies"
            body = """<div style="
            max-width:600px; margin:0 auto; background-color:#ffffff; border-radius:8px;
            box-shadow:0 4px 12px rgba(0,0,0,0.1);
            font-family:Arial, Helvetica, sans-serif;">
            <div style="background-color:#0f766e;padding:20px;text-align:center;color:#ffffff;
            border-radius:8px 8px 0 0;">
            <h2>Welcome to Ressen Technologies</h2>
            </div>
            <div style="padding:25px;color:#333333;">
            <p>Dear <strong>Valued User</strong>,</p>
            <p>Your account has been successfully created.</p>
            <p>You may now sign in and begin using our services.</p>
            <p>Kind regards,<br><strong>Ressen Technologies Team</strong></p>
            </div>
            </div>"""

            hashed_password = hash_value(password)

            send_email(recipient, subject, body)

            cursor = conn.cursor()
            cursor.execute(
                "INSERT INTO users (email, password) VALUES (%s, %s)",
                (recipient, hashed_password)
            )
            conn.commit()
            cursor.close()

            flash("Account created successfully! Kindly sign in.", "success")
            return redirect(url_for("signin"))

        except Exception as e:
            traceback.print_exc()
            flash(f"Database error: {str(e)}", "error")
            return render_template("signup.html")

    # ✅ REQUIRED: handles GET requests
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
    """
    Retrieve the file path for a student's work from DB, calculate price, 
    update DB, and send the file.
    """

    work = request.form.get('work_id', '').strip()
    bind = request.form.get('binding', '').strip()

    # Convert to boolean
    is_bind = True if bind == 'true' else False

    # Retrieve the file path
    with conn.cursor() as cursor:
        cursor.execute("SELECT filepath FROM work WHERE work_id = %s LIMIT 1", (work,))
        result = cursor.fetchone()

    if not result:
        abort(404, description="No file found for this student")

    filepath = result[0]

    if not os.path.isfile(filepath):
        abort(404, description="File not found on server")

    # Count the number of pages in the PDF
    with open(filepath, "rb") as pdf_file:
        reader = PdfReader(pdf_file)
        page_count = len(reader.pages)

    # Calculate price
    price = (page_count * 20) + (50 if is_bind else 0)

    # Update the DB
    with conn.cursor() as cursor:
        cursor.execute(
            "UPDATE work SET binding = %s, price = %s WHERE work_id = %s",
            (is_bind, price, work)
        )
        conn.commit()

    # Return both file and price
    response = send_file(filepath, as_attachment=True)
    response.headers['X-Price'] = str(price)  # Optional custom header
    return response

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

