# =================================================================
# BAGIAN 1: IMPOR SEMUA PERALATAN DAPUR YANG DIBUTUHKAN
# =================================================================
from flask import Flask, request, jsonify
from flask_cors import CORS
from pymongo import MongoClient
from bson.objectid import ObjectId # Untuk berinteraksi dengan ID unik MongoDB
from functools import wraps # Untuk membuat decorator token
import bcrypt 
import jwt    
from datetime import datetime, timedelta
import tensorflow as tf
from transformers import BertTokenizer
import joblib
import numpy as np
import warnings

# Mengabaikan UserWarning dari Keras yang tidak relevan
warnings.filterwarnings("ignore", category=UserWarning, module='keras')


# =================================================================
# BAGIAN 2: INISIALISASI DAN KONFIGURASI APLIKASI
# =================================================================
app = Flask(__name__)
CORS(app, resources={r"/api/*": {"origins": "*"}})

# Ganti dengan connection string MongoDB Atlas Anda yang sudah lengkap
MONGO_URI = "mongodb+srv://ErliandikaSyahputra:syahputra2710@emoticacluster.iecl2wu.mongodb.net/?retryWrites=true&w=majority&appName=EmoticaCluster"
client = MongoClient(MONGO_URI)
db = client['emotica_db']

# Kunci rahasia untuk JWT. Di aplikasi nyata, ini harus sangat rahasia.
app.config['SECRET_KEY'] = 'kunci-rahasia-super-aman-yang-tidak-boleh-ada-disini'


# =================================================================
# BAGIAN 3: MEMUAT MODEL MACHINE LEARNING (SEKALI SAJA)
# =================================================================
try:
    model = tf.keras.models.load_model('models/best_sentiment_model.keras')
    tokenizer = BertTokenizer.from_pretrained('models/tokenizer')
    label_encoder = joblib.load('models/label_encoder.joblib')
    print(">>> Model, Tokenizer, dan Label Encoder berhasil dimuat! <<<")
except Exception as e:
    print(f">>> TERJADI ERROR SAAT MEMUAT MODEL: {e} <<<")
    model = None


# =================================================================
# BAGIAN 4: FUNGSI BANTUAN & DECORATOR
# =================================================================

# Fungsi untuk prediksi sentimen
def predict_sentiment(text):
    if not model:
        return "Model tidak siap", 0.0

    cleaned_text = text.lower()
    inputs = tokenizer(cleaned_text, return_tensors="tf", max_length=150, truncation=True, padding='max_length')
    
    input_dict = {
        "input_layer": inputs["input_ids"],
        "token_type_ids": inputs["token_type_ids"],
        "attention_mask": inputs["attention_mask"],
    }

    predictions = model.predict(input_dict)
    
    predicted_class_index = np.argmax(predictions, axis=1)[0]
    predicted_class_label = label_encoder.inverse_transform([predicted_class_index])[0]
    confidence = float(np.max(predictions))
    
    return predicted_class_label, confidence

# Decorator untuk melindungi endpoint yang butuh login
def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization'].split(" ")[1]
        
        if not token:
            return jsonify({'message': 'Token tidak ada!'}), 401
        
        try:
            data = jwt.decode(token, app.config['SECRET_KEY'], algorithms=["HS256"])
            # Cari pengguna berdasarkan ObjectId yang benar
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

# Pintu utama untuk tes server
@app.route('/')
def index():
    return "<h1>Backend Emotica Berhasil Berjalan!</h1>"

# Pintu untuk registrasi
@app.route('/api/auth/register', methods=['POST'])
def register():
    # ... (kode ini sudah benar, tidak perlu diubah)
    data = request.get_json()
    name = data.get('name')
    email = data.get('email')
    password = data.get('password')
    if not name or not email or not password: return jsonify({'message': 'Mohon isi semua kolom'}), 400
    if db.users.find_one({'email': email}): return jsonify({'message': 'Email sudah terdaftar'}), 409
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    db.users.insert_one({'name': name, 'email': email, 'password': hashed_password, 'createdAt': datetime.utcnow()})
    return jsonify({'message': 'Registrasi berhasil!'}), 201

# Pintu untuk login
@app.route('/api/auth/login', methods=['POST'])
def login():
    # ... (kode ini sudah benar, tidak perlu diubah)
    data = request.get_json()
    email = data.get('email')
    password = data.get('password')
    user = db.users.find_one({'email': email})
    if not user or not bcrypt.checkpw(password.encode('utf-8'), user['password']):
        return jsonify({'message': 'Email atau kata sandi salah'}), 401
    token = jwt.encode({'user_id': str(user['_id']),'exp': datetime.utcnow() + timedelta(hours=24)}, app.config['SECRET_KEY'], algorithm="HS256")
    return jsonify({'message': 'Login berhasil!','token': token,'user': { 'id': str(user['_id']), 'name': user['name'], 'email': user['email'] }}), 200

# [ENDPOINT BARU] Pintu untuk analisis sentimen
@app.route('/api/analyze', methods=['POST'])
@token_required # Lindungi pintu ini dengan "penjaga"
def analyze_text(current_user):
    data = request.get_json()
    text_to_analyze = data.get('text')

    if not text_to_analyze:
        return jsonify({"message": "Teks tidak boleh kosong"}), 400

    # Panggil fungsi prediksi yang sudah kita buat
    sentiment, confidence = predict_sentiment(text_to_analyze)

    # Simpan hasil analisis ke database
    db.analyses.insert_one({
        'user_id': current_user['_id'],
        'text': text_to_analyze,
        'sentiment': sentiment,
        'confidence': confidence,
        'createdAt': datetime.utcnow()
    })

    return jsonify({
        'sentiment': {'type': sentiment.lower(), 'score': confidence}, # Mengembalikan 'positive' atau 'negative'
    }), 200

# =================================================================
# BAGIAN 6: MENJALANKAN SERVER
# =================================================================
if __name__ == '__main__':
    # Menjalankan server Flask tanpa tes internal lagi
    app.run(debug=True, port=5001)

