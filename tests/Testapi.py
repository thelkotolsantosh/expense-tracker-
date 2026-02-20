import json
import pytest
from app import create_app, db
from app.models import Category, Expense
from config import TestingConfig


@pytest.fixture
def app():
    app = create_app(TestingConfig)
    with app.app_context():
        db.create_all()
        yield app
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def sample_category(app):
    with app.app_context():
        cat = Category(name="Food", color="#e74c3c")
        db.session.add(cat)
        db.session.commit()
        return cat.id


# ─── Category Tests ───────────────────────────────────────────────────────────

class TestCategories:
    def test_list_categories_empty(self, client):
        res = client.get("/api/categories")
        assert res.status_code == 200
        assert res.get_json() == []

    def test_create_category(self, client):
        res = client.post("/api/categories", json={"name": "Food", "color": "#e74c3c"})
        assert res.status_code == 201
        data = res.get_json()
        assert data["name"] == "Food"
        assert data["color"] == "#e74c3c"

    def test_create_category_duplicate(self, client):
        client.post("/api/categories", json={"name": "Food", "color": "#e74c3c"})
        res = client.post("/api/categories", json={"name": "Food", "color": "#e74c3c"})
        assert res.status_code == 409

    def test_create_category_missing_name(self, client):
        res = client.post("/api/categories", json={"color": "#e74c3c"})
        assert res.status_code == 400

    def test_create_category_invalid_color(self, client):
        res = client.post("/api/categories", json={"name": "Food", "color": "red"})
        assert res.status_code == 400

    def test_delete_category(self, client, sample_category):
        res = client.delete(f"/api/categories/{sample_category}")
        assert res.status_code == 200


# ─── Expense Tests ────────────────────────────────────────────────────────────

class TestExpenses:
    def test_list_expenses_empty(self, client):
        res = client.get("/api/expenses")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total"] == 0
        assert data["expenses"] == []

    def test_create_expense(self, client):
        res = client.post("/api/expenses", json={"title": "Lunch", "amount": 12.50})
        assert res.status_code == 201
        data = res.get_json()
        assert data["title"] == "Lunch"
        assert data["amount"] == 12.50

    def test_create_expense_with_category(self, client, sample_category):
        res = client.post(
            "/api/expenses",
            json={"title": "Pizza", "amount": 20.0, "category_id": sample_category},
        )
        assert res.status_code == 201
        data = res.get_json()
        assert data["category"]["id"] == sample_category

    def test_create_expense_invalid_amount(self, client):
        res = client.post("/api/expenses", json={"title": "Test", "amount": -5})
        assert res.status_code == 400

    def test_create_expense_invalid_date(self, client):
        res = client.post("/api/expenses", json={"title": "Test", "amount": 10, "date": "not-a-date"})
        assert res.status_code == 400

    def test_get_expense(self, client):
        create_res = client.post("/api/expenses", json={"title": "Coffee", "amount": 4.50})
        expense_id = create_res.get_json()["id"]

        res = client.get(f"/api/expenses/{expense_id}")
        assert res.status_code == 200
        assert res.get_json()["title"] == "Coffee"

    def test_update_expense(self, client):
        create_res = client.post("/api/expenses", json={"title": "Old title", "amount": 10.0})
        expense_id = create_res.get_json()["id"]

        res = client.put(f"/api/expenses/{expense_id}", json={"title": "New title", "amount": 20.0})
        assert res.status_code == 200
        data = res.get_json()
        assert data["title"] == "New title"
        assert data["amount"] == 20.0

    def test_delete_expense(self, client):
        create_res = client.post("/api/expenses", json={"title": "To delete", "amount": 5.0})
        expense_id = create_res.get_json()["id"]

        res = client.delete(f"/api/expenses/{expense_id}")
        assert res.status_code == 200

        res = client.get(f"/api/expenses/{expense_id}")
        assert res.status_code == 404

    def test_get_nonexistent_expense(self, client):
        res = client.get("/api/expenses/9999")
        assert res.status_code == 404


# ─── Summary Tests ────────────────────────────────────────────────────────────

class TestSummary:
    def test_summary_empty(self, client):
        res = client.get("/api/summary")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total"] == 0
        assert data["by_category"] == []

    def test_summary_with_data(self, client, sample_category):
        client.post("/api/expenses", json={"title": "A", "amount": 50.0, "category_id": sample_category})
        client.post("/api/expenses", json={"title": "B", "amount": 30.0, "category_id": sample_category})

        res = client.get("/api/summary")
        assert res.status_code == 200
        data = res.get_json()
        assert data["total"] >= 80.0
