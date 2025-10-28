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
python manage.py runserver
```

### To run tests:

```bash
pytest --cov=inspections
```

## ☁️ Deployment

- Deployed manually to AWS Elastic Beanstalk
- Production: main branch
- Integration: develop branch
- URL (example): http://your-elasticbeanstalk-env.us-east-1.elasticbeanstalk.com

## 🧩 Tech Stack

- Backend: Django REST Framework
- Frontend: React + Vite
- Database: SQLite (local) / PostgreSQL (AWS)
- Hosting: AWS Elastic Beanstalk
- CI/CD: GitHub Actions + Coveralls

## 📖 Features

- Search NYC restaurants by name
- Filter by borough and cuisine type
- View detailed inspection history for each restaurant
- Sort results by grade, score, or name
- Responsive modal-based UI for restaurant details
- Real-time inspection data from NYC Open Data API

## 📝 License

MIT License

