from flask import Flask, request, jsonify
import pyodbc
import os
from datetime import datetime

app = Flask(__name__)

server = os.environ.get('AZURE_SQL_SERVER')
database = os.environ.get('AZURE_SQL_DATABASE')
username = os.environ.get('AZURE_SQL_USERNAME')
password = os.environ.get('AZURE_SQL_PASSWORD')
driver = '{ODBC Driver 18 for SQL Server}'

connection_string = f'DRIVER={driver};SERVER={server};PORT=1433;DATABASE={database};UID={username};PWD={password};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

def get_db_connection():
    return pyodbc.connect(connection_string)

@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        user_name = data.get('username')
        user_password = data.get('password')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT ID, Role, UserName, PhoneNo FROM Users WHERE UserName = ? AND Password = ?"
        cursor.execute(query, (user_name, user_password))
        result = cursor.fetchone()
        
        conn.close()
        
        if result:
            return jsonify({
                'success': True,
                'user': {
                    'ID': result[0],
                    'Role': result[1],
                    'UserName': result[2],
                    'PhoneNo': result[3]
                }
            })
        else:
            return jsonify({
                'success': False,
                'message': 'Invalid credentials'
            })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

@app.route('/api/patient-submission', methods=['POST'])
def patient_submission():
    try:
        data = request.get_json()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = """INSERT INTO PatientRawSubmission 
                   (Name, DOB, Gender, PhoneNo, City, District, Lesion, Redness, Disability, NoSensation, NoneSymptoms, DirectContact)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)"""
        
        cursor.execute(query, (
            data.get('name'),
            data.get('dob'),
            data.get('gender'),
            data.get('phoneNo'),
            data.get('city'),
            data.get('district'),
            data.get('lesion'),
            data.get('redness'),
            data.get('disability'),
            data.get('noSensation'),
            data.get('noneSymptoms'),
            data.get('directContact')
        ))
        
        conn.commit()
        conn.close()
        
        return jsonify({
            'success': True,
            'message': 'Patient data submitted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

@app.route('/api/patients', methods=['GET'])
def get_patients():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM PatientRawSubmission"
        cursor.execute(query)
        results = cursor.fetchall()
        
        patients = []
        for row in results:
            patients.append({
                'UID': row[0],
                'Name': row[1],
                'DOB': row[2].strftime('%Y-%m-%d') if row[2] else None,
                'Gender': row[3],
                'PhoneNo': row[4],
                'City': row[5],
                'District': row[6],
                'Lesion': row[7],
                'Redness': row[8],
                'Disability': row[9],
                'NoSensation': row[10],
                'NoneSymptoms': row[11],
                'DirectContact': row[12]
            })
        
        conn.close()
        
        return jsonify({
            'success': True,
            'patients': patients
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': 'Server error'
        }), 500

@app.route('/', methods=['GET'])
def home():
    return jsonify({
        'message': 'Azure SQL API is running',
        'status': 'OK'
    })

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
