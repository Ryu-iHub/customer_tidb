import os
import base64
from flask import Flask, request, jsonify, render_template
import pymysql
from pymysql.cursors import DictCursor
from dotenv import load_dotenv

load_dotenv()

# การรับค่าจาก .env ด้วย os.getenv("ชื่อตัวแปร") จะได้ค่ากลับมาเป็น String เสมอ
DB_HOST = os.getenv("DB_HOST")
DB_PORT = int(os.getenv("DB_PORT", 4000)) # แปลงค่า String ที่ได้มาจาก os.getenv("DB_PORT") เป็นตัวเลข int
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_NAME = os.getenv("DB_NAME")

# DB_CA = os.getenv("DB_CA_CERT")  # path to isrgrootx1.pem

# Base64-encoded CA cert
DB_CA_CERT = os.getenv("DB_CA_CERT")  # path to isrgrootx1.pem
DB_CA_PATH = "/temp/ca.pem"
# decode base64 → pem file (ทำครั้งเดียวตอน start app)
if DB_CA_CERT:
    try:
        with open(DB_CA_PATH, "wb") as f:
            f.write(base64.b64decode(DB_CA_CERT))
    except Exception as e:
        print("❌ Error decoding CA cert:", e)



app = Flask(__name__)

def get_connection():
    # pymysql supports ssl parameter as a dict; provide path to CA file
    
    # ssl_args = {"ca": DB_CA} if DB_CA else None
    ssl_args = {"ca": DB_CA_PATH} if os.path.exists(DB_CA_PATH) else None

    return pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        cursorclass=DictCursor,
        ssl=ssl_args,
        connect_timeout=10
    )

@app.route("/")
def index():
    return render_template("index.html")


# Simple health check
@app.route("/health")
def health():
    try:
        conn = get_connection()
        conn.close()
        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

# CREATE
@app.route("/api/customers", methods=["POST"])
def add_customer():
    payload = request.get_json()
    name = payload.get("name")
    email = payload.get("email")
    phone = payload.get("phone")

    if not name:
        return jsonify({"error": "name is required"}), 400

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO customer_data (name, email, phone) VALUES (%s, %s, %s)",
                (name, email, phone)
            )
        conn.commit()
        return jsonify({"message": "created"}), 201
    except pymysql.err.IntegrityError as ie:
        return jsonify({"error": "integrity error", "detail": str(ie)}), 400
    except Exception as e:
        return jsonify({"error": "db error", "detail": str(e)}), 500
    finally:
        conn.close()

# READ all
@app.route("/api/customers", methods=["GET"])
def get_customers():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM customer_data ORDER BY id DESC")
            rows = cur.fetchall()
        return jsonify(rows)
    finally:
        conn.close()

# READ single
@app.route("/api/customers/<int:cid>", methods=["GET"])
def get_customer(cid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM customer_data WHERE id=%s", (cid,))
            row = cur.fetchone()
        if not row:
            return jsonify({"error": "not found"}), 404
        return jsonify(row)
    finally:
        conn.close()

# UPDATE
@app.route("/api/customers/<int:cid>", methods=["PUT"])
def update_customer(cid):
    payload = request.get_json()
    name = payload.get("name")
    email = payload.get("email")
    phone = payload.get("phone")

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE customer_data SET name=%s, email=%s, phone=%s WHERE id=%s",
                (name, email, phone, cid)
            )
        conn.commit()
        return jsonify({"message": "updated"})
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

# DELETE
@app.route("/api/customers/<int:cid>", methods=["DELETE"])
def delete_customer(cid):
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM customer_data WHERE id=%s", (cid,))
        conn.commit()
        return jsonify({"message": "deleted"})
    finally:
        conn.close()

if __name__ == "__main__":
    # For development only; in production use gunicorn/uwsgi
    app.run(host="0.0.0.0", port=5000, debug=True)
