from flask import Flask, render_template, request, jsonify
import mysql.connector
from mysql.connector import Error
import os

# Get the absolute path to the project directory
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, "frontend", "templates")
STATIC_DIR = os.path.join(BASE_DIR, "frontend", "static")

app = Flask(__name__, template_folder=TEMPLATE_DIR, static_folder=STATIC_DIR)

DB_CONFIG = {
    "host": os.getenv("MYSQL_HOST", "localhost"),
    "user": os.getenv("MYSQL_USER", "root"),
    "password": os.getenv("MYSQL_PASSWORD", "Dhina@2706"),
    "database": os.getenv("MYSQL_DATABASE", "pharmacy_management"),
}

def get_db():
    return mysql.connector.connect(**DB_CONFIG)

def rows(table):
    conn = get_db()
    cur = conn.cursor(dictionary=True)
    cur.execute(f"SELECT * FROM {table} ORDER BY id DESC")
    data = cur.fetchall()
    cur.close()
    conn.close()
    return data

@app.get("/")
def home():
    return render_template("index.html")

@app.get("/api/medicines")
def get_medicines():
    return jsonify(rows("medicines"))

@app.post("/api/medicines")
def create_medicine():
    d = request.get_json() or {}
    required = ["name", "category", "batch", "price", "stock", "expiry"]
    if any(not d.get(k) and d.get(k) != 0 for k in required):
        return jsonify(error="All required medicine fields must be filled"), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""INSERT INTO medicines
        (name, category, batch, price, stock, expiry, supplier)
        VALUES (%s,%s,%s,%s,%s,%s,%s)""",
        (d["name"], d["category"], d["batch"], d["price"], d["stock"],
         d["expiry"], d.get("supplier", "")))
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return jsonify({"id": new_id, **d}), 201

@app.put("/api/medicines/<int:item_id>")
def update_medicine(item_id):
    d = request.get_json() or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute("""UPDATE medicines SET name=%s, category=%s, batch=%s,
        price=%s, stock=%s, expiry=%s, supplier=%s WHERE id=%s""",
        (d.get("name"), d.get("category"), d.get("batch"), d.get("price"),
         d.get("stock"), d.get("expiry"), d.get("supplier", ""), item_id))
    conn.commit()
    if cur.rowcount == 0:
        cur.close(); conn.close()
        return jsonify(error="Medicine not found"), 404
    cur.close(); conn.close()
    return jsonify({"id": item_id, **d})

@app.delete("/api/medicines/<int:item_id>")
def delete_medicine(item_id):
    return delete_record("medicines", item_id)

@app.get("/api/suppliers")
def get_suppliers():
    return jsonify(rows("suppliers"))

@app.post("/api/suppliers")
def create_supplier():
    return create_generic("suppliers")

@app.put("/api/suppliers/<int:item_id>")
def update_supplier(item_id):
    return update_generic("suppliers", item_id)

@app.delete("/api/suppliers/<int:item_id>")
def delete_supplier(item_id):
    return delete_record("suppliers", item_id)

@app.get("/api/customers")
def get_customers():
    return jsonify(rows("customers"))

@app.post("/api/customers")
def create_customer():
    return create_generic("customers")

@app.put("/api/customers/<int:item_id>")
def update_customer(item_id):
    return update_generic("customers", item_id)

@app.delete("/api/customers/<int:item_id>")
def delete_customer(item_id):
    return delete_record("customers", item_id)

def create_generic(table):
    d = request.get_json() or {}
    if not d.get("name"):
        return jsonify(error="Name is required"), 400
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"INSERT INTO {table} (name, phone, email, extra) VALUES (%s,%s,%s,%s)",
                (d["name"], d.get("phone",""), d.get("email",""), d.get("extra","")))
    conn.commit()
    new_id = cur.lastrowid
    cur.close(); conn.close()
    return jsonify({"id": new_id, **d}), 201

def update_generic(table, item_id):
    d = request.get_json() or {}
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"UPDATE {table} SET name=%s, phone=%s, email=%s, extra=%s WHERE id=%s",
                (d.get("name"), d.get("phone",""), d.get("email",""),
                 d.get("extra",""), item_id))
    conn.commit()
    if cur.rowcount == 0:
        cur.close(); conn.close()
        return jsonify(error="Record not found"), 404
    cur.close(); conn.close()
    return jsonify({"id": item_id, **d})

def delete_record(table, item_id):
    conn = get_db()
    cur = conn.cursor()
    cur.execute(f"DELETE FROM {table} WHERE id=%s", (item_id,))
    conn.commit()
    deleted = cur.rowcount
    cur.close(); conn.close()
    if not deleted:
        return jsonify(error="Record not found"), 404
    return jsonify(message="Deleted successfully")

@app.get("/api/health")
def health():
    try:
        conn = get_db()
        conn.close()
        return jsonify(status="ok", database="MySQL")
    except Error as e:
        return jsonify(status="error", database="MySQL", error=str(e)), 500

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=5000)
