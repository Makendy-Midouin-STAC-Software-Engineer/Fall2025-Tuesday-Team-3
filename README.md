# 🏙️ SafeEats NYC

A Django + React web application that helps users explore NYC restaurant health inspection data using the official NYC Open Data API.

---

## 🚀 Sprint 6 — CI/CD and Testing

**Goal:**  
Implement Continuous Integration (CI) and Continuous Deployment (CD) for the team project.  
Each member also configured CI and test suites individually.

### ✅ What We Accomplished
- Added **GitHub Actions workflow** for automated CI  
- Runs **black**, **flake8**, and **coverage.py**  
- Added **unit tests** under `inspections/tests`  
- Configured **daily post-submit job** on `main` branch  
- Deployed app to **AWS Elastic Beanstalk** (manual ZIP for now)  
- Achieved 85%+ test coverage  

---

## ⚙️ CI/CD Badges

| Branch | Build Status | Coverage |
|--------|---------------|-----------|
| `main` | ![CI](https://github.com/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3/actions/workflows/django.yml/badge.svg?branch=main) | [![Coverage Status](https://coveralls.io/repos/github/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3/badge.svg?branch=main)](https://coveralls.io/github/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3?branch=main) |
| `develop` | ![CI](https://github.com/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3/actions/workflows/django.yml/badge.svg?branch=develop) | [![Coverage Status](https://coveralls.io/repos/github/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3/badge.svg?branch=develop)](https://coveralls.io/github/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3?branch=develop) |

> If Coveralls badges don't show yet, connect the repo at [https://coveralls.io](https://coveralls.io).

---

## 🧪 How to Run Locally

```bash
git clone https://github.com/Makendy-Midouin-STAC-Software-Engineer/Fall2025-Tuesday-Team-3.git
cd Fall2025-Tuesday-Team-3
python -m venv venv
venv\Scripts\activate  # (on Windows)
pip install -r requirements.txt
python manage.py migrate  # Create database tables
python manage.py runserver
```

### Import Data

To import NYC restaurant inspection data:

```bash
# Import all data (no limit)
python manage.py import_nyc_inspections

# Or import with a limit (for testing)
python manage.py import_nyc_inspections --limit 10000
```

### To run tests:

```bash
pytest --cov=inspections
```

## ☁️ Deployment

- Deployed manually to AWS Elastic Beanstalk
- Production: main branch
- Integration: develop branch
- **URL:** http://safeeats-app-env.eba-nknmey2d.us-east-2.elasticbeanstalk.com/

## 🧩 Tech Stack

- Backend: Django REST Framework
- Frontend: React + Vite
- Database: PostgreSQL (production) / SQLite (local dev fallback)
- Hosting: AWS Elastic Beanstalk
- CI/CD: GitHub Actions + Coveralls

## 🗄️ Database Setup

### Local Development (SQLite)
By default, the application uses SQLite for local development. No setup required.

### PostgreSQL Migration
To migrate to PostgreSQL and import all NYC restaurant inspection data:

1. **See [MIGRATION_GUIDE.md](MIGRATION_GUIDE.md)** for detailed instructions
2. **Quick start:**
   ```bash
   # Install PostgreSQL and create database
   # Set DATABASE_URL environment variable
   export DATABASE_URL="postgresql://user:pass@localhost:5432/safeeats_db"
   
   # Run migrations
   python manage.py migrate
   
   # Import all data (no limit)
   python manage.py import_nyc_inspections
   ```

The application automatically uses PostgreSQL when `DATABASE_URL` is set, otherwise falls back to SQLite.

## 👥 Team Members

- Nick Nikac – Backend Developer / CI Lead
- Makendy Midouin – Scrum Master
- [Add others here]

## 📖 Features

- Search NYC restaurants by name
- Filter by borough and cuisine type
- View detailed inspection history for each restaurant
- Sort results by grade, score, or name
- Responsive modal-based UI for restaurant details
- Real-time inspection data from NYC Open Data API

## 📝 License

MIT License
