# 🧠 Emotica – Backend API (Flask)

<div align="center">
  <img src="https://github.com/Emotica-DBS/FE-Emotica/blob/main/public/assets/logo.png" alt="Emotica Logo" width="160" />
</div>

Selamat datang di **Backend Emotica** – dapur digital dari aplikasi Emotica. Di sinilah semua proses analisis emosi dijalankan melalui model machine learning, terintegrasi dengan sistem otentikasi dan API.

---

## 📋 Ringkasan Proyek

Emotica adalah aplikasi analisis sentimen Bahasa Indonesia berbasis Flask. Backend ini menangani:
- Autentikasi pengguna
- API analisis emosi
- Integrasi model ML dari tim Emotica

---

## 🚀 Cara Menjalankan Proyek

### Prasyarat
- Python 3.8+
- Akun MongoDB Atlas (atau MongoDB lokal)
- Virtual environment (opsional tapi disarankan)

### Langkah Instalasi

1. Clone repository ini dan masuk ke direktori `BE-Emotica`
2. Buat virtual environment dan aktifkan:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
3. Install semua dependensi dengan `pip install -r requirements.txt`
4. Salin file `.env.example` menjadi `.env`, lalu isi:
   - `MONGO_URI` (dari MongoDB Atlas)
   - `JWT_SECRET` (buat secret key JWT)
5. Jalankan server menggunakan perintah `python app.py`

Aplikasi akan berjalan di `http://localhost:5000/api/`

---

## 🔐 Endpoint API

### Autentikasi
| Method | Endpoint            | Keterangan               |
|--------|---------------------|--------------------------|
| POST   | `/api/auth/register` | Registrasi pengguna baru |
| POST   | `/api/auth/login`    | Login pengguna            |

### Analisis Emosi
| Method | Endpoint       | Keterangan                              |
|--------|----------------|------------------------------------------|
| POST   | `/api/analyze` | Mengirim teks dan menerima hasil emosi  |

---

## 🧪 Pengujian

Untuk menjalankan unit test:
Gunakan perintah `python -m pytest` di direktori utama proyek.

---

## 🧠 Tentang Model

- Model berbasis **BERT Bahasa Indonesia**
- Dikembangkan untuk klasifikasi **positif**, **netral**, dan **negatif**
- Sudah terintegrasi ke endpoint analisis secara real-time
- Dikembangkan oleh tim Machine Learning Emotica

---

## 🤝 Kontribusi

Kami terbuka terhadap kontribusi dari siapa saja. Langkah umum:
1. Fork repository
2. Buat branch fitur (`fitur/NamaFitur`)
3. Commit dan push
4. Buka Pull Request ke repo utama

---

## 👥 Tim Pengembang

Proyek ini dikembangkan oleh tim Capstone **DBS Coding Camp 2025**:

| Nama                          | Peran               |
|-------------------------------|---------------------|
| Fajri Nurhadi                 | Back-End Developer  |
| Erliandika Syahputra         | Front-End Lead      |
| Addien Munadiya Yunadi       | Machine Learning    |
| Mahendra Kirana M.B          | Machine Learning    |
| Bivandira Aurel Maha Dewa    | Machine Learning    |

---

## 📝 Lisensi

Proyek ini menggunakan lisensi **MIT**. Lihat file [LICENSE](LICENSE) untuk detail selengkapnya.

---

> Dibangun untuk mendukung komunikasi digital yang lebih sehat dan berempati. – Tim Emotica ❤️
