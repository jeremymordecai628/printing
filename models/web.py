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
            return redirect(url_for("signin", next=request.path))
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
    MAIL_SERVER = os.getenv("MAIL_SERVER")
    MAIL_PORT = int(os.getenv("MAIL_PORT"))
    MAIL_USE_TLS = os.getenv("MAIL_USE_TLS") == "True"
    MAIL_USE_SSL = os.getenv("MAIL_USE_SSL") == "True"
    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")
    MAIL_DEFAULT_SENDER = os.getenv("MAIL_DEFAULT_SENDER")

    msg = MIMEText(body, "html")
    msg["Subject"] = subject
    msg["From"] = MAIL_USERNAME
    msg["To"] = recipient_email

    print(MAIL_SERVER, MAIL_PORT, MAIL_USERNAME)

    try:
        if MAIL_USE_SSL:
            server = smtplib.SMTP_SSL(MAIL_SERVER, MAIL_PORT)
        else:
            server = smtplib.SMTP(MAIL_SERVER, MAIL_PORT)
            if MAIL_USE_TLS:
                server.starttls()

        server.login(MAIL_USERNAME, MAIL_PASSWORD)
        server.sendmail(MAIL_USERNAME, [recipient_email], msg.as_string())
        server.quit()

        print("✅ Email sent to", recipient_email)
        return "Email sent successfully"

    except Exception as e:
        print("❌ Email failed:", e)
        return f"Failed to send email: {str(e)}"

def generate_unique_code(length=8):
    """
    Generate a secure random alphanumeric code.

    Args:
        length (int): Length of the code (default 8).

    Returns:
        str: Generated unique code.
    """
    alphabet = string.ascii_uppercase + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def user_exists_with_media_role(conn, user_id):
    """
    Check whether a user exists and has role 'media'.

    Args:
        conn: Database connection object.
        user_id (int): User ID.

    Returns:
        bool: True if user exists with role media, False otherwise.
    """
    sql = "SELECT 1 FROM `user` WHERE id = %s AND role = %s LIMIT 1"

    with conn.cursor() as cursor:
        cursor.execute(sql, (user_id, "media"))
        return cursor.fetchone() is not None

def detect_os():
    ua = request.user_agent.platform
    if ua == "windows":
        return "windows"
    if ua == "linux":
        return "linux"
    if ua == "macos":
        return "macos"
    if ua == "android":
        return "android"
    return None

def detect_arch():
    machine = platform.machine().lower()
    if "arm" in machine:
        return "arm64"
    return "x64"

