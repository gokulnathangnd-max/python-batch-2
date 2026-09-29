import sqlite3
from flask import Flask, jsonify, request, render_template, session, redirect, url_for

app = Flask(__name__)

app.secret_key = "change_this_to_a_secure_random_string_later" 

DB_FILE = "users.db"


ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "password123"

def get_db_connection():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT,
            age INTEGER,
            rollno TEXT UNIQUE
        )
    """)
    conn.commit()
    conn.close()

init_db()



@app.route('/')
def home():
    """Renders the main registration form page."""
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login_page():
    """Handles admin authentication rendering and submission form parsing."""
    if request.method == 'POST':
       
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        else:
            return render_template('login.html', error="Invalid username or password")
            
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    """Protects the administrative database monitoring screen."""
    if not session.get('logged_in'):
        return redirect(url_for('login_page'))
    return render_template('dashboard.html')

@app.route('/logout')
def logout():
    """Destroys active administration cookies."""
    session.pop('logged_in', None)
    return redirect(url_for('login_page'))


# --- API Endpoints ---

@app.route("/user", methods=["POST"])
def register():
    """API endpoint to insert new profiles."""
    frontend = request.get_json(force=True)
    if not frontend:
        return jsonify({"error": "Invalid or missing JSON data"}), 400

    name = frontend.get("name")
    age = frontend.get("age")
    rollno = frontend.get("rollno")

    if not name or not age or not rollno:
        return jsonify({"error": "User details are required"}), 400

    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "INSERT INTO users (name, age, rollno) VALUES (?, ?, ?)",
            (name, int(age), str(rollno))
        )
        conn.commit()
        return jsonify({"message": "User details saved successfully to database"}), 201
    except sqlite3.IntegrityError:
        return jsonify({"error": "Roll number already exists"}), 400
    except Exception as e:
        return jsonify({"error": "Failed to save data", "details": str(e)}), 500
    finally:
        conn.close()

@app.route("/api/admin/users", methods=["GET"])
def get_all_users():
    """Protected API endpoint fetching user data rows for dashboard display."""
    if not session.get('logged_in'):
        return jsonify({"error": "Unauthorized access window"}), 401
        
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT name, age, rollno FROM users")
    rows = cursor.fetchall()
    conn.close()
    
    users_list = [dict(row) for row in rows]
    return jsonify({"users": users_list})

if __name__ == "__main__":
    app.run(debug=True)
