from flask import Flask, request, jsonify, render_template, redirect, session, url_for
from flask_cors import CORS
import mysql.connector
from dotenv import load_dotenv
import os

load_dotenv()
app = Flask(__name__)
CORS(app)
app.secret_key = "supersecretkey"

USER = {"username": "admin", "password": "pass123"}

def get_connection():
    return mysql.connector.connect(
        host=os.getenv("MYSQL_HOST"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        database=os.getenv("MYSQL_DATABASE")
    )

@app.route('/')
def home():
    if 'user' in session:
        return render_template('index.html')
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.form
        if data['username'] == USER['username'] and data['password'] == USER['password']:
            session['user'] = data['username']
            return redirect(url_for('home'))
        return render_template('login.html', error="Invalid credentials")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))

@app.route('/patients', methods=['GET'])
def get_all_patients():
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM PATIENT_DB")
    rows = cur.fetchall()
    cols = [i[0] for i in cur.description]
    patients = [dict(zip(cols, row)) for row in rows]
    cur.close()
    conn.close()
    return jsonify(patients)

@app.route('/patients/<int:pid>', methods=['DELETE'])
def delete_patient(pid):
    if 'user' not in session:
        return redirect(url_for('login'))

    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM PATIENT_DB WHERE P_id = %s", (pid,))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Patient deleted successfully"})

@app.route('/patients/<int:pid>/fee', methods=['PUT'])
def update_fee(pid):
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE PATIENT_DB SET fee = %s WHERE P_id = %s", (data["fee"], pid))
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Fee updated successfully"})

@app.route('/patients', methods=['POST'])
def add_patient():
    if 'user' not in session:
        return redirect(url_for('login'))

    data = request.json
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO PATIENT_DB (P_name, age, Disease, Doc_Incharge, fee) VALUES (%s,%s,%s,%s,%s)",
        (data["P_name"], data["age"], data["Disease"], data["Doc_Incharge"], data["fee"])
    )
    conn.commit()
    cur.close()
    conn.close()
    return jsonify({"message": "Patient added successfully"}), 201

# ✅ New reset route
@app.route('/reset-patients', methods=['POST'])
def reset_patients():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("TRUNCATE TABLE PATIENT_DB")
    conn.commit()
    cur.close()
    conn.close()
    return redirect(url_for('home'))
