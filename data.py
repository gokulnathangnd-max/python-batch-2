from flask import Flask, request, jsonify
import sqlite3

app = Flask(__name__)
DB_FILE = "number.db"

def get_conn():
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    return conn

def initializedb():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE,
            password TEXT
        )
    """)
    conn.commit()
    conn.close()
  
initializedb()

@app.route("/", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user")
        rows = cursor.fetchall()
        conn.close()
        
        user_dict = [dict(row) for row in rows]
        
        return jsonify({
            "msg": "enter the userdetails",
            "user details": user_dict
        })
        
    frontend = request.get_json(force=True)

    if not frontend:
        return jsonify({"msg": "the data is not send"}), 400

    username = frontend.get("username")
    password = frontend.get("password")

    if not username or not password:
        return jsonify({"msg": "username or password is missing"}), 400
        
    try:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO user (username, password) VALUES (?, ?)", 
            (username, password)
        )
        conn.commit()
        return jsonify({"msg": "the user is saved succesfully"}), 201
        
    except sqlite3.IntegrityError:
        return jsonify({"msg": "This username is already taken"}), 400
    except Exception as e:
        return jsonify({"msg": "Database error", "error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(debug=True)
