# 🌾 KrishiMitra AI

<div align="center">

### 🤖 AI-Powered Agriculture Platform (Seed to Post-Harvest)

**Helping farmers with crop planning, crop health, harvest timing, quality grading, and shelf-life insights**

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-green)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-orange)
![Alembic](https://img.shields.io/badge/Alembic-Migrations-purple)
![JWT](https://img.shields.io/badge/Auth-JWT-yellowgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

</div>

---

## 📖 Overview

**KrishiMitra AI** is an intelligent decision-support platform for agriculture with a strong focus on reducing **post-harvest losses**.

The current repository contains a **production-style FastAPI backend** with modular architecture, authentication, profile management, prediction APIs, history tracking, and API documentation.  
Prediction services currently use deterministic logic and are designed to be replaced with trained ML/CV models without changing API contracts.

---

## 🎯 Problem Statement

A significant share of agricultural losses occurs after harvest due to:

- Poor grading and quality assessment
- Limited shelf-life visibility
- Weak storage and logistics planning
- Lack of timely market intelligence

Most tools solve isolated parts.  
**KrishiMitra AI** aims to provide an integrated, end-to-end platform across the agricultural lifecycle.

---

## ✅ Current Implementation Status

### Implemented (Backend)

- Modular FastAPI architecture
- JWT authentication (register/login/me)
- Role-aware protected routes
- Farmer profile management
- Prediction APIs with history tables:
  - Crop recommendation
  - Disease detection
  - Harvest prediction
  - Shelf-life prediction
  - Produce quality grading
- SQLAlchemy models + Alembic migrations
- OpenAPI/Swagger documentation
- Health and root endpoints

### In Progress / Planned

- Real ML/CV model integration
- Marketplace and order lifecycle
- Weather + market intelligence APIs
- Frontend application
- PostgreSQL migration and cloud deployment
- Test automation and CI/CD

---

## 🧠 AI Modules (Roadmap-Aligned)

- 🌱 **Crop Recommendation**
- 🌿 **Disease Detection**
- 🌾 **Harvest Prediction**
- 📦 **Shelf-Life Prediction**
- 🥭 **Produce Quality Grading**
- 🚚 **Logistics & Market Intelligence** (planned)
- 🤖 **Multilingual AI Assistant** (planned)

---

## 🏗 Architecture

```text
Frontend (Planned: React)
        │
        ▼
FastAPI Backend (Implemented)
        │
 ┌──────┼───────────┐
 │      │           │
 ▼      ▼           ▼
Services DB Layer   Auth Layer
        │
        ▼
AI Model Adapter Layer (Current: deterministic, Future: trained models)
```

---

## 🛠 Tech Stack

### Backend (Current)
- Python 3.11
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- JWT Auth
- SQLite (development)

### AI/ML (Planned Integration)
- Scikit-learn
- PyTorch / TensorFlow
- OpenCV
- XGBoost

### Frontend (Planned)
- React
- Tailwind CSS

### Deployment (Planned)
- Docker
- GitHub Actions
- Render / Railway / AWS / Azure

---

## 📂 Project Structure

```text
KrishiMitra-AI/
├── backend/
│   └── app/
│       ├── api/
│       ├── core/
│       ├── db/
│       ├── models/
│       ├── schemas/
│       ├── services/
│       └── main.py
├── frontend/        # planned
├── ai_models/       # planned
├── datasets/        # planned
├── deployment/      # planned
├── docs/            # planned
└── README.md
```

---

## 🔌 API Highlights

### Auth
- `POST /auth/register`
- `POST /auth/login`
- `GET /auth/me`

### Farmer
- `POST /farmers/profile`
- `GET /farmers/profile`
- `PUT /farmers/profile`

### AI Prediction (current deterministic implementations)
- `POST /crop/recommend` + `GET /crop/history`
- `POST /disease/predict` + `GET /disease/history`
- `POST /harvest/predict` + `GET /harvest/history`
- `POST /shelf-life/predict` + `GET /shelf-life/history`
- `POST /quality/predict` + `GET /quality/history`

### Utility
- `GET /health`
- `GET /`
- `GET /docs`
- `GET /openapi.json`

---

## 🗺 Roadmap

### Phase 1 (Done)
- Backend setup, auth, profile, prediction APIs, history, docs

### Phase 2 (Next)
- Replace deterministic logic with trained models
- Add model versioning + inference loaders
- Add test suite (unit + API)

### Phase 3
- Marketplace core (products, cart, orders)
- Buyer/consumer modules
- Dashboard APIs

### Phase 4
- Weather + market data integrations
- Notification services
- Storage/logistics modules

### Phase 5
- Frontend integration
- PostgreSQL + cloud storage
- CI/CD + production deployment

---

## 🧪 Local Development (Backend)

```bash
# 1) Clone
git clone https://github.com/ALOK-KUMAR-SAH/KrishiMitra-AI.git
cd KrishiMitra-AI/backend

# 2) Create virtual environment
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run migrations
alembic upgrade head

# 5) Start server
uvicorn app.main:app --reload
```

Open:
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI JSON: `http://127.0.0.1:8000/openapi.json`

---

## 👥 Team

### Alok Kumar Sah — Team Lead
- AI/ML, CV, backend engineering, architecture

### Aman Anand — Agriculture Domain Expert
- Crop science, post-harvest workflows, domain validation

---

## 🏆 Hackathon Alignment

Built for **CII Post-Harvest Innovation Hackathon** with emphasis on:

- Reducing post-harvest losses
- Better grading and shelf-life decisions
- Data-driven harvest and market planning
- End-to-end agricultural value chain digitization

---

## 📜 License

This project is licensed under the MIT License.
