# HabotConnect Backend

A Django REST Framework backend for managing LSA profiles, booking requests, and mock payment processing.

## Features

- Parent and LSA profile management
- LSA search by skill
- Booking creation and validation
- Overlapping booking prevention
- Mock payment gateway integration
- Payment status tracking
- Payment webhook handling
- PostgreSQL database support
- Automated testing with pytest
- GitHub Actions CI

## Tech Stack

- Python 3.13
- Django 6.1
- Django REST Framework
- PostgreSQL
- pytest & pytest-django
- Requests
- django-model-utils
- GitHub Actions

## Project Structure

```text
habotconnect_backend/
├── bookings/
│   ├── migrations/
│   ├── tests/
│   │   ├── test_booking_api.py
│   │   ├── test_lsa_search.py
│   │   ├── test_payment_service.py
│   │   └── test_payment_webhook.py
│   ├── models.py
│   ├── serializers.py
│   ├── services.py
│   └── views.py
├── config/
├── .github/
│   └── workflows/
│       └── tests.yml
├── manage.py
├── pytest.ini
├── requirements.txt
└── README.md
```

## Setup

### Clone the Repository

```bash
git clone https://github.com/Sourabh2517x/habotconnect-backend.git
cd habotconnect-backend
```

### Create Virtual Environment

```bash
python -m venv VE
VE\Scripts\activate
```

### Install Dependencies

```bash
pip install -r requirements.txt
```

### Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-secret-key
DB_NAME=habotconnect_db
DB_USER=postgres
DB_PASSWORD=your-postgres-password
DB_HOST=localhost
DB_PORT=5432
```

### Database

Create the PostgreSQL database:

```sql
CREATE DATABASE habotconnect_db;
```

Run migrations:

```bash
python manage.py migrate
```

Start the server:

```bash
python manage.py runserver
```

The API will be available at:

```text
http://127.0.0.1:8000/
```

> Do not commit `.env` or real credentials to GitHub.

## API Endpoints

### LSA Search

```http
GET /api/v1/lsas/?skill=<skill>
```

Example:

```http
GET /api/v1/lsas/?skill=python
```

### Create Booking

```http
POST /api/v1/bookings/
```

Example:

```json
{
    "parent": 1,
    "lsa": 1,
    "start_time": "2026-08-20T10:00:00+05:30",
    "end_time": "2026-08-20T11:00:00+05:30",
    "notes": "Need help with Python"
}
```

The booking API validates booking times and prevents overlapping bookings for the same LSA.

### Payment Webhook

```http
POST /api/v1/payments/webhook/
```

Processes payment status updates and updates the associated booking.

## Payment Integration

The project uses a mock external HTTP service with Python's `requests` library.

It demonstrates:

- External API requests
- Payment success and failure handling
- Exception handling
- Payment status updates
- Payment webhook processing

No real payment gateway or payment credentials are used.

## Testing

The project uses `pytest` and `pytest-django`.

Run all tests:

```bash
pytest -v
```

### Test Coverage

The test suite contains 8 tests covering:

- Successful booking creation
- Invalid booking time
- Overlapping booking prevention
- LSA search by skill
- Successful payment creation
- Payment gateway failure handling
- Successful payment webhook
- Failed payment webhook

Run individual test files:

```bash
pytest bookings/tests/test_booking_api.py -v
pytest bookings/tests/test_lsa_search.py -v
pytest bookings/tests/test_payment_service.py -v
pytest bookings/tests/test_payment_webhook.py -v
```

## Continuous Integration

GitHub Actions runs the test suite automatically on pushes and pull requests.

Workflow:

```text
.github/workflows/tests.yml
```

Tests are executed using:

```bash
pytest -v
```

## License

This project was created as part of a backend development assignment.