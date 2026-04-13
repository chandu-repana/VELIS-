# VELIS — Voice Enabled AI Interview System

## 🚀 Overview
VELIS is a full-stack AI-powered interview preparation system that enables real-time voice interaction, resume analysis, and intelligent feedback.

## ✨ Features
- 🎤 Real-time voice interaction (Speech-to-Text + Text-to-Speech)
- 🤖 AI-based question generation
- 📄 Resume parsing and evaluation
- 🔐 JWT + OAuth authentication (Google, GitHub)
- 📊 Performance feedback using NLP scoring
- ⚡ Scalable backend with FastAPI and Redis caching

## 🛠 Tech Stack

### Frontend
- React 18
- TailwindCSS
- Vite

### Backend
- FastAPI
- SQLAlchemy
- PostgreSQL
- Redis

### AI/ML
- Whisper (STT)
- Transformers (NLP)
- Custom evaluation engine

### DevOps
- Docker
- Docker Compose
- Nginx

---

## 🧠 Architecture
- React frontend → FastAPI backend
- Redis for caching
- PostgreSQL for persistence
- Docker for deployment

---

## ⚙️ Setup

```bash
git clone https://github.com/chandu-repana/VELIS-
cd VELIS-

# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
npm run dev
