# SafeEats - Restaurant Inspection Viewer

A Django + React application for viewing NYC restaurant health inspection data.

## Features

- View restaurant health inspection records
- Search and filter restaurants
- REST API for inspection data
- Modern React frontend
- Django admin interface

## Tech Stack

**Backend:**
- Django 5.2.7
- Django REST Framework
- PostgreSQL (production) / SQLite (development)
- Gunicorn (WSGI server)

**Frontend:**
- React 19
- Vite
- Modern ES6+

## Local Development

### Prerequisites

- Python 3.11+
- Node.js 18+
- pip and npm

### Setup

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd safeeats_deploy
```

2. **Install Python dependencies**
```bash
pip install -r requirements.txt
```

3. **Install frontend dependencies**
```bash
cd frontend
npm install
cd ..
```

4. **Run migrations**
```bash
python manage.py migrate
```

5. **Create a superuser**
```bash
python manage.py createsuperuser
```

6. **Import NYC inspection data (optional)**
```bash
python manage.py import_nyc_inspections
```

7. **Run the development server**

Terminal 1 (Backend):
```bash
python manage.py runserver
```

Terminal 2 (Frontend):
```bash
cd frontend
npm run dev
```

8. **Access the application**
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000/api/
- Django Admin: http://localhost:8000/admin/

## Deployment

See [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md) for detailed AWS Elastic Beanstalk deployment instructions.

### Quick Deploy

**Windows (PowerShell):**
```powershell
.\build_and_deploy.ps1
```

**Linux/Mac:**
```bash
chmod +x build_and_deploy.sh
./build_and_deploy.sh
```

## Project Structure

```
safeeats_deploy/
├── inspections/              # Django app for inspection data
│   ├── models.py            # Database models
│   ├── serializers.py       # DRF serializers
│   ├── views.py             # API views
│   └── urls.py              # API routes
├── safe_eats_backend/       # Django project settings
│   ├── settings.py          # Main settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI application
├── frontend/                # React frontend
│   ├── src/
│   │   ├── App.jsx         # Main React component
│   │   └── main.jsx        # Entry point
│   ├── index.html
│   └── package.json
├── .ebextensions/          # Elastic Beanstalk configuration
├── requirements.txt        # Python dependencies
├── manage.py              # Django management script
└── DEPLOYMENT_GUIDE.md    # Deployment instructions
```

## API Endpoints

- `GET /api/restaurants/` - List all restaurants with inspections
- `GET /api/restaurants/?search=pizza` - Search restaurants
- `GET /api/inspections/` - List all inspections
- More endpoints in `inspections/urls.py`

## Environment Variables

Create a `.env` file for local development:

```env
SECRET_KEY=your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

For production, set these in Elastic Beanstalk environment configuration.

## Testing

```bash
python manage.py test
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

[Your License Here]

## Support

For issues or questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

---

Built with ❤️ using Django and React

