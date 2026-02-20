# 💸 Expense Tracker API
A clean REST API for tracking personal expenses, built with Flask and SQLAlchemy. Supports categorized expenses, monthly summaries, and full CRUD operations.

## Features

- Create, read, update, and delete expenses
- Organize expenses with custom color-coded categories
- Monthly spending summaries with per-category breakdown
- Filter expenses by month, year, or category
- Pagination support on expense listings
- Seed command for quick local testing

## Tech Stack

- **Python 3.11+**
- **Flask 3.1** — web framework
- **Flask-SQLAlchemy** — ORM
- **Flask-Migrate** — database migrations
- **SQLite** (default) or any SQLAlchemy-compatible database (PostgreSQL, MySQL)
- **pytest** — testing

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/your-username/expense-tracker.git
cd expense-tracker
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # macOS / Linux
venv\Scripts\activate           # Windows
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure environment

```bash
cp .env.example .env
# Edit .env as needed
```

### 5. Initialize the database

```bash
flask --app main.py db init
flask --app main.py db migrate -m "initial migration"
flask --app main.py db upgrade
```

### 6. (Optional) Seed with sample data

```bash
flask --app main.py seed
```

### 7. Run the server

```bash
python main.py
```

The API will be available at `http://127.0.0.1:5000`.

## API Reference

### Expenses

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/expenses` | List all expenses |
| `GET` | `/api/expenses?month=3&year=2025` | Filter by month/year |
| `GET` | `/api/expenses?category_id=1` | Filter by category |
| `GET` | `/api/expenses/<id>` | Get a single expense |
| `POST` | `/api/expenses` | Create an expense |
| `PUT` | `/api/expenses/<id>` | Update an expense |
| `DELETE` | `/api/expenses/<id>` | Delete an expense |

**Create / Update Expense Body:**

```json
{
  "title": "Grocery run",
  "amount": 85.40,
  "date": "2025-03-15",
  "note": "Weekly groceries",
  "category_id": 1
}
```

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/categories` | List all categories |
| `POST` | `/api/categories` | Create a category |
| `DELETE` | `/api/categories/<id>` | Delete a category (cascades to expenses) |

**Create Category Body:**

```json
{
  "name": "Food & Dining",
  "color": "#e74c3c"
}
```

### Summary

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/summary` | Current month summary |
| `GET` | `/api/summary?month=3&year=2025` | Summary for a specific month |

**Example Response:**

```json
{
  "year": 2025,
  "month": 3,
  "total": 450.75,
  "by_category": [
    { "category": "Food & Dining", "color": "#e74c3c", "total": 210.50 },
    { "category": "Transport",     "color": "#3498db", "total": 145.00 }
  ],
  "uncategorized": 95.25
}
```

## Running Tests

```bash
pytest tests/ -v
```

## Project Structure

```
expense-tracker/
├── app/
│   ├── __init__.py      # App factory
│   ├── models.py        # SQLAlchemy models
│   └── routes.py        # Blueprints and route handlers
├── tests/
│   └── test_api.py      # Pytest test suite
├── config.py            # Configuration classes
├── main.py              # Entry point + CLI commands
├── requirements.txt
├── .env.example
├── .gitignore
└── README.md
```

## Using with PostgreSQL

Update `DATABASE_URL` in your `.env`:

```
DATABASE_URL=postgresql://user:password@localhost:5432/expenses
```

Then install the driver:

```bash
pip install psycopg2-binary
```

## License

MIT
