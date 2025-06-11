# 🎭 Emotica Backend API

## 📋 Overview
Emotica is an Indonesian sentiment analysis tool that helps analyze emotions in text using advanced machine learning models.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- MongoDB Atlas account
- Virtual environment

### Installation
1. Clone the repository
```bash
git clone https://github.com/Emotica-DBS/BE-Emotica.git
cd BE-Emotica
```

2. Create and activate virtual environment
```bash
python -m venv venv
.\venv\Scripts\activate  # Windows
```

3. Install dependencies
```bash
pip install -r requirements.txt
```

4. Set up environment variables
```bash
cp .env.example .env
# Edit .env with your credentials
```

## 🛠️ API Endpoints

### Authentication
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login user |

### Sentiment Analysis
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/analyze` | Analyze text sentiment |

## 🧪 Testing
Run tests using:
```bash
python -m pytest
```

## 📦 Model Information
- BERT-based Indonesian sentiment analysis
- Supports multiple emotion classifications
- Pre-trained on Indonesian language corpus

## 🤝 Contributing
1. Fork the repository
2. Create feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License
MIT License - see LICENSE file for details

## 👥 Team
- DBS Team Emotica