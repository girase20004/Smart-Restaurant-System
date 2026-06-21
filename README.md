# Smart-Restaurant-System
# SMART RESTAURANT ORDERING & MANAGEMENT SYSTEM (SROMS)

Phase 1 is a Flask + PostgreSQL backend for restaurant staff authentication, table QR codes, menu management, and basic order creation.

## Tech Stack

- **Backend:** Python Flask
- **Database:** PostgreSQL
- **ORM:** SQLAlchemy
- **Authentication:** JWT with password hashing
- **QR Codes:** `qrcode` library

## Project Structure

```text
Smart-Restaurant-System/
├── app.py
├── config.py
├── extensions.py
├── requirements.txt
├── models/
│   ├── __init__.py
│   ├── user.py
│   ├── table.py
│   ├── menu.py
│   └── order.py
├── routes/
│   ├── auth_routes.py
│   ├── table_routes.py
│   ├── menu_routes.py
│   └── order_routes.py
├── templates/
├── static/
└── qr_codes/
```

## PostgreSQL Configuration

The app reads configuration from environment variables:

| Variable | Default | Purpose |
| --- | --- | --- |
| `DATABASE_URL` | `postgresql://postgres:postgres@localhost:5432/sroms` | SQLAlchemy PostgreSQL connection string |
| `SECRET_KEY` | `change-me-in-production` | Flask secret key |
| `JWT_SECRET_KEY` | `change-me-jwt-secret` | JWT signing secret |
| `JWT_ACCESS_TOKEN_HOURS` | `8` | Access token lifetime in hours |
| `CUSTOMER_URL_BASE` | `http://localhost:5000` | Base URL encoded in QR codes |
| `QR_CODE_FOLDER` | `qr_codes` | Folder where QR PNG files are saved |

Create a local PostgreSQL database:

```bash
createdb sroms
export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sroms"
export SECRET_KEY="replace-with-a-secure-secret"
export JWT_SECRET_KEY="replace-with-a-secure-jwt-secret"
```

## Run the Project

1. Create and activate a virtual environment.

   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies.

   ```bash
   pip install -r requirements.txt
   ```

3. Export PostgreSQL and secret configuration.

   ```bash
   export DATABASE_URL="postgresql://postgres:postgres@localhost:5432/sroms"
   export SECRET_KEY="replace-with-a-secure-secret"
   export JWT_SECRET_KEY="replace-with-a-secure-jwt-secret"
   export FLASK_APP=app.py
   ```

4. Initialize database tables.

   ```bash
   flask init-db
   ```

5. Start the API server.

   ```bash
   flask run --host 0.0.0.0 --port 5000
   ```

6. Verify the service.

   ```bash
   curl http://localhost:5000/health
   ```

## Sample API Requests

### Create Staff Users

```bash
curl -X POST http://localhost:5000/api/auth/users \
  -H "Content-Type: application/json" \
  -d '{"name":"Admin User","email":"admin@sroms.test","password":"StrongPass123!","role":"admin"}'
```

Repeat with `role` values `chef` and `waiter` for chef and waiter logins.

### Login API

```bash
curl -X POST http://localhost:5000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@sroms.test","password":"StrongPass123!","role":"admin"}'
```

Save the returned token:

```bash
export TOKEN="paste-access-token-here"
```

### Create Table API

```bash
curl -X POST http://localhost:5000/api/tables \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"table_number":"T1","status":"available"}'
```

This also saves a QR image such as `qr_codes/table_T1.png`. The QR opens `/customer/T1` using `CUSTOMER_URL_BASE`.

### Generate QR API

```bash
curl -X POST http://localhost:5000/api/tables/1/qr \
  -H "Authorization: Bearer $TOKEN"
```

### Add Menu Item API

```bash
curl -X POST http://localhost:5000/api/menu \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "dish_name":"Paneer Tikka",
    "price":249.00,
    "category":"Starter",
    "image":"https://example.com/paneer-tikka.jpg",
    "ingredients":"Paneer, yogurt, spices, capsicum",
    "prep_time":20,
    "veg_nonveg":"veg",
    "availability":true
  }'
```

### Get Menu API

```bash
curl http://localhost:5000/api/menu
curl "http://localhost:5000/api/menu?category=Starter&available=true"
```

### Create Order API

```bash
curl -X POST http://localhost:5000/api/orders \
  -H "Content-Type: application/json" \
  -d '{"table_id":1,"status":"pending","total":249.00}'
```