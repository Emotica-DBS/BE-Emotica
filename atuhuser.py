# backend/app.py

# =================================================================
# BAGIAN 1: IMPOR SEMUA PERALATAN DAPUR YANG DIBUTUHKAN
# =================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
import bcrypt # Si brankas kata sandi
import jwt    # Si pencetak tiket VIP
from datetime import datetime, timedelta

# =================================================================
# BAGIAN 2: INISIALISASI DAN KONFIGURASI APLIKASI
# =================================================================
app = Flask(__name__)
CORS(app, supports_credentials=True) 

# Ganti dengan connection string MongoDB Atlas Anda yang sudah lengkap
MONGO_URI = "mongodb+srv://ErliandikaSyahputra:syahputra2710@emoticacluster.iecl2wu.mongodb.net/?retryWrites=true&w=majority&appName=EmoticaCluster"
client = MongoClient(MONGO_URI)
db = client['emotica_db']

# Kunci rahasia untuk JWT. Di aplikasi nyata, ini harus sangat rahasia.
app.config['SECRET_KEY'] = 'kunci-rahasia-super-aman-yang-tidak-boleh-ada-disini'


# =================================================================
# BAGIAN 3: PINTU-PINTU MASUK (API ENDPOINTS)
# =================================================================

# Pintu utama untuk tes server
@app.route('/')
def index():
    return "<h1>Backend Emotica Berhasil Berjalan!</h1>"

# Pintu untuk registrasi
@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')

    if not name or not email or not password:
        return jsonify({'message': 'Mohon isi semua kolom'}), 400

    if db.users.find_one({'email': email}):
        return jsonify({'message': 'Email sudah terdaftar'}), 409

    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    db.users.insert_one({
        'name': name,
        'email': email,
        'password': hashed_password,
        'createdAt': datetime.utcnow()
    })

    return jsonify({'message': 'Registrasi berhasil!'}), 201


# Pintu untuk login
@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')

    user = db.users.find_one({'email': email})

    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Email atau kata sandi salah'}), 401
        
    token = jwt.encode({
        'user_id': str(user['_id']),
        'exp': datetime.utcnow() + timedelta(hours=24)
    }, app.config['SECRET_KEY'], algorithm="HS256")

    return jsonify({
        'message': 'Login berhasil!',
        'token': token,
        'user': { 'id': str(user['_id']), 'name': user['name'], 'email': user['email'] }
    }), 200


# =================================================================
# BAGIAN 4: MENJALANKAN SERVER
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5001)