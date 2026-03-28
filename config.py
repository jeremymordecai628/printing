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
    cursorclass=pymysql.cursors.DictCursor,    
    charset='utf8mb4'
)

# File upload folder
DESTINATION = os.getenv("REPO_BASE_PATH")
UPLOAD_FOLDER = os.getenv('mdir')
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed extensions
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'doc','docx','xml', 'xlsx', 'pptx', 'pdf', 'txt'}

