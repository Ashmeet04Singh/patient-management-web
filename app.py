from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

app = Flask(__name__)
CORS(app)
app.secret_key = os.getenv("SECRET_KEY", "supersecretkey")

# Admin credentials from .env (No hardcoding)
ADMIN_USER = os.getenv("ADMIN_USER")
ADMIN_PASS = os.getenv("ADMIN_PASS")


# -----------------------------
# DATABASE CONNECTION
# -----------------------------
def get_connection():
    try:
        return mysql.connector.connect(
            host=os.getenv("MYSQL_HOST"),
            user=os.getenv("MYSQL_USER"),
            password=os.getenv("MYSQL_PASSWORD"),
            database=os.getenv("MYSQL_DATABASE")
        )
    except mysql.connector.Error as err:
        print("Database connection error:", err)
        return None


# -----------------------------
# ROUTES
# -----------------------------
@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))


# -----------------------------
# LOGIN SYSTEM
# -----------------------------
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get("username")
        password = request.form.get("password")

        if username == ADMIN_USER and password == ADMIN_PASS:
            session['user'] = username
            return redirect(url_for('home'))

        return render_template('login.html', error="Invalid username or password")

    return render_template('login.html')


@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# -----------------------------
# GET ALL PATIENTS
# -----------------------------
@app.route('/patients', methods=['GET'])
def get_all_patients():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "DB connection failed"}), 500

    cur = conn.cursor()
    cur.execute("SELECT * FROM PATIENT_DB")
    rows = cur.fetchall()
    cols = [i[0] for i in cur.description]

    patients = [dict(zip(cols, row)) for row in rows]

    cur.close()
    conn.close()
    return jsonify(patients), 200


# -----------------------------
# ADD PATIENT
# -----------------------------
@app.route('/patients', methods=['POST'])
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.json

    # Basic validation
    required = ["P_name", "age", "Disease", "Doc_Incharge", "fee"]
    if not all(key in data and data[key] for key in required):
        return jsonify({"error": "Missing fields"}), 400

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "DB connection failed"}), 500

    cur = conn.cursor()
    cur.execute("""
        INSERT INTO PATIENT_DB (P_name, age, Disease, Doc_Incharge, fee)
        VALUES (%s, %s, %s, %s, %s)
    """, (data["P_name"], data["age"], data["Disease"], data["Doc_Incharge"], data["fee"]))

    conn.commit()
    cur.close()
    conn.close()

    return jsonify({"message": "Patient added successfully"}), 201


# -----------------------------
# DELETE PATIENT
# -----------------------------
@app.route('/patients/<int:pid>', methods=['DELETE'])
def delete_patient(pid):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "DB connection failed"}), 500

    cur = conn.cursor()
    cur.execute("SELECT * FROM PATIENT_DB WHERE P_id = %s", (pid,))
    exists = cur.fetchone()

    if not exists:
        return jsonify({"error": "Patient not found"}), 404

    cur.execute("DELETE FROM PATIENT_DB WHERE P_id = %s", (pid,))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"message": "Patient deleted successfully"}), 200


# -----------------------------
# UPDATE FEE
# -----------------------------
@app.route('/patients/<int:pid>/fee', methods=['PUT'])
def update_fee(pid):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.json
    if "fee" not in data:
        return jsonify({"error": "Fee is required"}), 400

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "DB connection failed"}), 500

    cur = conn.cursor()
    cur.execute("SELECT * FROM PATIENT_DB WHERE P_id = %s", (pid,))
    exists = cur.fetchone()

    if not exists:
        return jsonify({"error": "Patient not found"}), 404

    cur.execute("UPDATE PATIENT_DB SET fee = %s WHERE P_id = %s",
                (data["fee"], pid))
    conn.commit()

    cur.close()
    conn.close()
    return jsonify({"message": "Fee updated successfully"}), 200


# -----------------------------
# RESET TABLE (ADMIN ONLY)
# -----------------------------
@app.route('/reset-patients', methods=['POST'])
def reset_patients():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    if conn is None:
        return jsonify({"error": "DB connection failed"}), 500

    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE PATIENT_DB")
    conn.commit()

    cur.close()
    conn.close()

    return redirect(url_for('home'))


# -----------------------------
# RUN
# -----------------------------
if __name__ == "__main__":
    app.run(debug=True)
