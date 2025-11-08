# Database Migration Guide: SQLite to PostgreSQL

This guide will help you migrate your SafeEats application from SQLite to PostgreSQL and import all NYC restaurant inspection data.

## Prerequisites

1. **PostgreSQL installed** on your system (or access to a PostgreSQL database)
2. **Python virtual environment** activated
3. **All dependencies installed** (`pip install -r requirements.txt`)

## Step 1: Install PostgreSQL (if not already installed)

### Windows
Download and install from: https://www.postgresql.org/download/windows/

### macOS
```bash
brew install postgresql@15
brew services start postgresql@15
```

### Linux (Ubuntu/Debian)
```bash
sudo apt-get update
sudo apt-get install postgresql postgresql-contrib
sudo systemctl start postgresql
```

## Step 2: Create PostgreSQL Database

1. **Open PostgreSQL command line** (psql) or use pgAdmin

2. **Create a new database:**
```sql
CREATE DATABASE safeeats_db;
```

3. **Create a user** (optional, or use your existing user):
```sql
CREATE USER safeeats_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE safeeats_db TO safeeats_user;
```

## Step 3: Set Up Environment Variables

Create a `.env` file in your project root (or set environment variables):

```bash
# For local development
DATABASE_URL=postgresql://safeeats_user:your_secure_password@localhost:5432/safeeats_db

# Optional: NYC Open Data API token (for higher rate limits)
SODA_APP_TOKEN=your_token_here
```

**Note:** If you're using the default `postgres` user:
```bash
DATABASE_URL=postgresql://postgres:your_password@localhost:5432/safeeats_db
```

## Step 4: Install Updated Dependencies

```bash
pip install -r requirements.txt
```

This will install `psycopg2-binary` and `dj-database-url` if not already installed.

## Step 5: Run Migrations on PostgreSQL

1. **Set the DATABASE_URL environment variable** (if not using .env file):
   - Windows PowerShell: `$env:DATABASE_URL="postgresql://user:pass@localhost:5432/safeeats_db"`
   - Windows CMD: `set DATABASE_URL=postgresql://user:pass@localhost:5432/safeeats_db`
   - Linux/Mac: `export DATABASE_URL="postgresql://user:pass@localhost:5432/safeeats_db"`

2. **Create the database schema:**
```bash
python manage.py migrate
```

This will create all the necessary tables in PostgreSQL.

## Step 6: Import All Data from NYC API

Now import **all** the NYC restaurant inspection data (no limit):

```bash
python manage.py import_nyc_inspections
```

**Note:** This will import ALL available data from the NYC Open Data API. This may take a while depending on your internet connection and the amount of data available.

**Optional:** If you want to limit the import (for testing), you can still use:
```bash
python manage.py import_nyc_inspections --limit 50000
```

**Optional:** Import only recent data:
```bash
python manage.py import_nyc_inspections --since 2024-01-01
```

## Step 7: Verify the Migration

1. **Check the data:**
```bash
python manage.py shell
```

Then in the Python shell:
```python
from inspections.models import Restaurant, Inspection
print(f"Restaurants: {Restaurant.objects.count()}")
print(f"Inspections: {Inspection.objects.count()}")
```

2. **Test the API:**
```bash
python manage.py runserver
```

Visit `http://localhost:8000/api/restaurants/` to verify the data is accessible.

## Step 8: (Optional) Migrate Existing SQLite Data

If you have existing data in your SQLite database that you want to migrate to PostgreSQL:

### Option A: Export from SQLite and Import to PostgreSQL

1. **Export data from SQLite:**
```bash
python manage.py dumpdata inspections > data.json
```

2. **Switch to PostgreSQL** (set DATABASE_URL)

3. **Import data to PostgreSQL:**
```bash
python manage.py loaddata data.json
```

### Option B: Use Django's database router (more complex)

This requires custom code to read from SQLite and write to PostgreSQL simultaneously.

## Production Deployment

For production (e.g., AWS Elastic Beanstalk), set the `DATABASE_URL` environment variable in your deployment configuration:

```
DATABASE_URL=postgresql://username:password@hostname:5432/database_name
```

## Troubleshooting

### Connection Issues

- **"FATAL: password authentication failed"**: Check your username and password
- **"could not connect to server"**: Ensure PostgreSQL is running (`sudo systemctl status postgresql` on Linux)
- **"database does not exist"**: Create the database first (Step 2)

### Import Issues

- **Rate limiting**: Get a free API token from https://data.cityofnewyork.us/profile/app_tokens
- **Timeout errors**: The script uses 60-second timeouts. For very large imports, you may need to increase this.
- **Memory issues**: For extremely large datasets, consider importing in batches using the `--since` flag

### Performance Tips

- **Indexes**: The models already have indexes on `camis`, `name`, `borough`, and `cuisine_description`
- **Batch size**: The import script uses 5000 rows per API call, which is optimal for most cases
- **Connection pooling**: The settings use `conn_max_age=600` for connection reuse

## Rollback to SQLite

If you need to switch back to SQLite for local development:

1. **Remove or unset DATABASE_URL:**
   - Windows PowerShell: `Remove-Item Env:\DATABASE_URL`
   - Linux/Mac: `unset DATABASE_URL`

2. **The application will automatically use SQLite** (as configured in settings.py)

## Next Steps

- Set up database backups for PostgreSQL
- Configure connection pooling for production
- Monitor database performance
- Consider setting up read replicas for scaling

