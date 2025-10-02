# SafeEats NYC

SafeEats NYC is a web application built on the **NYC DOHMH Restaurant Inspection Results dataset**.  
It allows users to search for restaurants by name, borough, or cuisine and view inspection grades, violations, and trends in a clean, modern UI.

---

## 🚀 Tech Stack

**Frontend**
- React + Vite
- TypeScript / JavaScript
- Tailwind CSS

**Backend**
- Django (Python Web Framework)
- Django REST Framework (API)

**Database**
- PostgreSQL (Relational database for production)
- SQLite (optional local dev)

**Cloud & Deployment**
- AWS Elastic Beanstalk (deployment)
- GitHub Actions (CI/CD pipeline)

**Dev Tools**
- GitHub + ZenHub (issues, epics, sprints)
- Black + Flake8 (Python formatting and linting)

---

## 🌱 Branch Workflow


We use **trunk-based flow** with `main` and `develop`:

- **main** = stable, demo-ready only (protected: PRs required)
- **develop** = integration/testing for the current sprint
- **feature/*** = short-lived branches for each task/story

### Create a feature branch (from `develop`)
```bash
git switch develop
git pull origin develop
git switch -c feature/<area>-<task>
# e.g., feature/frontend-search-ui, feature/backend-search-endpoint

### Pull Requests
All work must be pushed to a feature branch and opened as a Pull Request **into `develop`**.  
A teammate reviews the PR, and only the reviewer merges it into `develop`.  
No one merges their own code.
