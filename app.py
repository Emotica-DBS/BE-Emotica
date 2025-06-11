# =================================================================
# BAGIAN 1: IMPOR SEMUA PERALATAN DAPUR YANG DIBUTUHKAN
# =================================================================
import os
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId
from functools import wraps
import bcrypt 
import jwt    
from datetime import datetime, timedelta
import tensorflow as tf
from transformers import BertTokenizer
import joblib
import numpy as np
import warnings

# Mengabaikan beberapa pesan peringatan yang tidak krusial dari Keras & TensorFlow
warnings.filterwarnings("ignore", category=UserWarning, module='keras')
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2' # Menyembunyikan pesan info TensorFlow

# =================================================================
# BAGIAN 2: INISIALISASI DAN KONFIGURASI APLIKASI
# =================================================================
app = Flask(__name__)
# [UNTUK DEPLOYMENT] Mengatur CORS agar lebih aman di produksi
CORS(app, resources={r"/api/*": {"origins": "*"}}) 

# [UNTUK DEPLOYMENT] Mengambil konfigurasi dari Environment Variables
# Di lokal, Anda bisa membuat file .env atau mengaturnya secara manual
# Di Railway, kita akan memasukkan ini di tab "Variables"
MONGO_URI = os.environ.get('MONGO_URI')
SECRET_KEY = os.environ.get('SECRET_KEY')

# Fallback untuk pengembangan lokal jika environment variable tidak diatur
if not MONGO_URI:
    MONGO_URI = "mongodb+srv://ErliandikaSyahputra:syahputra2710@emoticacluster.iecl2wu.mongodb.net/?retryWrites=true&w=majority&appName=EmoticaCluster"
if not SECRET_KEY:
    SECRET_KEY = 'kunci-rahasia-lokal-yang-tetap-harus-diamankan'

app.config['SECRET_KEY'] = SECRET_KEY

# Koneksi ke Database
try:
    client = MongoClient(MONGO_URI)
    db = client['emotica_db']
    print(">>> Koneksi ke MongoDB berhasil! <<<")
except Exception as e:
    print(f">>> GAGAL KONEKSI KE MONGODB: {e} <<<")
    db = None


# =================================================================
# BAGIAN 3: MEMUAT MODEL MACHINE LEARNING (SEKALI SAJA)
# =================================================================
model = None
tokenizer = None
label_encoder = None
try:
    # Memastikan path relatif terhadap lokasi app.py
    model_path = os.path.join(os.path.dirname(__file__), 'models', 'best_sentiment_model.keras')
    tokenizer_path = os.path.join(os.path.dirname(__file__), 'models', 'tokenizer')
    encoder_path = os.path.join(os.path.dirname(__file__), 'models', 'label_encoder.joblib')
    
    model = tf.keras.models.load_model(model_path)
    tokenizer = BertTokenizer.from_pretrained(tokenizer_path)
    label_encoder = joblib.load(encoder_path)
    print(">>> Model, Tokenizer, dan Label Encoder berhasil dimuat! <<<")
except Exception as e:
    print(f">>> TERJADI ERROR SAAT MEMUAT MODEL: {e} <<<")
    
# =================================================================
# BAGIAN 4: FUNGSI BANTUAN & DECORATOR ("Penjaga Pintu")
# =================================================================

def predict_sentiment(text):
    if not all([model, tokenizer, label_encoder]):
        return "Model tidak siap", 0.0

    cleaned_text = text.lower()
    inputs = tokenizer(cleaned_text, return_tensors="tf", max_length=150, truncation=True, padding='max_length')
    
    input_dict = {
        "input_layer": inputs["input_ids"],
        "token_type_ids": inputs["token_type_ids"],
        "attention_mask": inputs["attention_mask"],
    }

    predictions = model.predict(input_dict, verbose=0) # verbose=0 untuk menyembunyikan progress bar
    
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_class_label = label_encoder.inverse_transform([predicted_class_index])[0]
    confidence = float(np.max(predictions))
    
    return predicted_class_label, confidence

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Bearer '):
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token tidak ada!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            current_user = db.users.find_one({'_id': ObjectId(data['user_id'])})
            if not current_user:
                 return jsonify({'message': 'User tidak ditemukan!'}), 401
        except Exception as e:
            return jsonify({'message': 'Token tidak valid atau kedaluwarsa!', 'error': str(e)}), 401
        
        return f(current_user, *args, **kwargs)
    return decorated


# =================================================================
# BAGIAN 5: API ENDPOINTS (PINTU-PINTU LAYANAN)
# =================================================================

@app.route('/')
def index():
    return "<h1>Backend Emotica Berhasil Berjalan!</h1>"

@app.route('/api/auth/register', methods=['POST'])
def register():
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password: return jsonify({'message': 'Mohon isi semua kolom'}), 400
    if db.users.find_one({'email': email}): return jsonify({'message': 'Email sudah terdaftar'}), 409
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db.users.insert_one({'name': name, 'email': email, 'password': hashed_password, 'createdAt': datetime.utcnow()})
    return jsonify({'message': 'Registrasi berhasil!'}), 201

@app.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = db.users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Email atau kata sandi salah'}), 401
    token = jwt.encode({'user_id': str(user['_id']),'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'message': 'Login berhasil!','token': token,'user': { 'id': str(user['_id']), 'name': user['name'], 'email': user['email'] }}), 200

@app.route('/api/analyze', methods=['POST'])
@token_required
def analyze_text(current_user):
    data = request.get_json()
    text_to_analyze = data.get('text')
    if not text_to_analyze:
        return jsonify({"message": "Teks tidak boleh kosong"}), 400

    sentiment, confidence = predict_sentiment(text_to_analyze)

    # Simpan ke database
    db.analyses.insert_one({
        'user_id': current_user['_id'],
        'text': text_to_analyze,
        'sentiment': sentiment,
        'confidence': confidence,
        'createdAt': datetime.utcnow()
    })
    return jsonify({'sentiment': {'type': sentiment.lower(), 'score': confidence}}), 200

# =================================================================
# BAGIAN 6: MENJALANKAN SERVER (HANYA UNTUK LOKAL)
# =================================================================
if __name__ == '__main__':
    app.run(debug=True, port=5001)
