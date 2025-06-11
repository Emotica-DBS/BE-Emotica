# backend/app.py

# =================================================================
# BAGIAN 1: IMPOR PERALATAN
# =================================================================
from flask import Flask
from flask_cors import CORS
import tensorflow as tf
from transformers import BertTokenizer
import joblib
import numpy as np
import warnings

# Mengabaikan UserWarning dari Keras yang tidak relevan
warnings.filterwarnings("ignore", category=UserWarning, module='keras')

# =================================================================
# BAGIAN 2: FUNGSI UNTUK MEMUAT MODEL (RESEP RAHASIA)
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
# BAGIAN 3: FUNGSI UNTUK PREDIKSI (PROSES MEMASAK)
# =================================================================
def predict_sentiment(text):
    if not model:
        return "Model tidak siap", 0.0

    cleaned_text = text.lower()
    
    # [PERBAIKAN UTAMA] Menyesuaikan max_length menjadi 150 agar sesuai dengan input model
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

# =================================================================
# BAGIAN 4: SERVER FLASK (PELAYAN)
# =================================================================
app = Flask(__name__)
CORS(app) 

@app.route('/')
def index():
    return "<h1>Backend Emotica Berhasil Berjalan!</h1>"
    
# NOTE: Endpoint untuk Autentikasi dan Analisis akan kita tambahkan di sini nanti

# =================================================================
# BAGIAN 5: UJI COBA INTERNAL
# =================================================================
if __name__ == '__main__':
    print("\n--- Memulai Tes Prediksi Internal ---")
    
    kalimat_tes = "saya sangat senang dengan produk ini, luar biasa!"
    hasil, skor = predict_sentiment(kalimat_tes)
    
    print(f"Kalimat: '{kalimat_tes}'")
    print(f"Prediksi Sentimen: {hasil.upper()}")
    print(f"Skor Kepercayaan: {skor:.2f}")
    
    print("--- Tes Prediksi Internal Selesai ---\n")
    
    app.run(debug=True, port=5001)
