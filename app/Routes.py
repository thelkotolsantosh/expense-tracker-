from datetime import date, datetime
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request
from sqlalchemy import extract, func

from app import db
from app.models import Category, Expense

expenses_bp = Blueprint("expenses", __name__)
categories_bp = Blueprint("categories", __name__)
summary_bp = Blueprint("summary", __name__)


# ─── Helpers ────────────────────────────────────────────────────────────────

def error(message, status=400):
    return jsonify({"error": message}), status


def success(data, status=200):
    return jsonify(data), status


# ─── Expenses ────────────────────────────────────────────────────────────────

@expenses_bp.route("", methods=["GET"])
def list_expenses():
    """List all expenses with optional filters."""
    month = request.args.get("month", type=int)
    year = request.args.get("year", type=int)
    category_id = request.args.get("category_id", type=int)
    limit = request.args.get("limit", default=50, type=int)
    offset = request.args.get("offset", default=0, type=int)

    query = Expense.query

    if year:
        query = query.filter(extract("year", Expense.date) == year)
    if month:
        query = query.filter(extract("month", Expense.date) == month)
    if category_id:
        query = query.filter(Expense.category_id == category_id)

    total = query.count()
    expenses = query.order_by(Expense.date.desc()).limit(limit).offset(offset).all()

    return success({
        "total": total,
        "limit": limit,
        "offset": offset,
        "expenses": [e.to_dict() for e in expenses],
    })


@expenses_bp.route("/<int:expense_id>", methods=["GET"])
def get_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    return success(expense.to_dict())


@expenses_bp.route("", methods=["POST"])
def create_expense():
    data = request.get_json(silent=True)
    if not data:
        return error("Request body must be JSON")

    title = data.get("title", "").strip()
    if not title:
        return error("'title' is required")

    try:
        amount = Decimal(str(data.get("amount", "")))
        if amount <= 0:
            raise ValueError
    except (InvalidOperation, ValueError):
        return error("'amount' must be a positive number")

    # Parse optional date
    expense_date = date.today()
    if "date" in data:
        try:
            expense_date = date.fromisoformat(data["date"])
        except ValueError:
            return error("'date' must be ISO format: YYYY-MM-DD")

    # Validate optional category
    category_id = data.get("category_id")
    if category_id and not Category.query.get(category_id):
        return error(f"Category {category_id} not found", 404)

    expense = Expense(
        title=title,
        amount=amount,
        note=data.get("note"),
        date=expense_date,
        category_id=category_id,
    )
    db.session.add(expense)
    db.session.commit()

    return success(expense.to_dict(), 201)


@expenses_bp.route("/<int:expense_id>", methods=["PUT"])
def update_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    data = request.get_json(silent=True)
    if not data:
        return error("Request body must be JSON")

    if "title" in data:
        title = data["title"].strip()
        if not title:
            return error("'title' cannot be empty")
        expense.title = title

    if "amount" in data:
        try:
            amount = Decimal(str(data["amount"]))
            if amount <= 0:
                raise ValueError
            expense.amount = amount
        except (InvalidOperation, ValueError):
            return error("'amount' must be a positive number")

    if "note" in data:
        expense.note = data["note"]

    if "date" in data:
        try:
            expense.date = date.fromisoformat(data["date"])
        except ValueError:
            return error("'date' must be ISO format: YYYY-MM-DD")

    if "category_id" in data:
        cid = data["category_id"]
        if cid is not None and not Category.query.get(cid):
            return error(f"Category {cid} not found", 404)
        expense.category_id = cid

    db.session.commit()
    return success(expense.to_dict())


@expenses_bp.route("/<int:expense_id>", methods=["DELETE"])
def delete_expense(expense_id):
    expense = Expense.query.get_or_404(expense_id)
    db.session.delete(expense)
    db.session.commit()
    return success({"message": f"Expense '{expense.title}' deleted"})


# ─── Categories ──────────────────────────────────────────────────────────────

@categories_bp.route("", methods=["GET"])
def list_categories():
    categories = Category.query.order_by(Category.name).all()
    return success([c.to_dict() for c in categories])


@categories_bp.route("", methods=["POST"])
def create_category():
    data = request.get_json(silent=True)
    if not data:
        return error("Request body must be JSON")

    name = data.get("name", "").strip()
    if not name:
        return error("'name' is required")

    if Category.query.filter_by(name=name).first():
        return error(f"Category '{name}' already exists", 409)

    color = data.get("color", "#3498db")
    if not (color.startswith("#") and len(color) == 7):
        return error("'color' must be a 7-character hex code like #3498db")

    category = Category(name=name, color=color)
    db.session.add(category)
    db.session.commit()
    return success(category.to_dict(), 201)


@categories_bp.route("/<int:category_id>", methods=["DELETE"])
def delete_category(category_id):
    category = Category.query.get_or_404(category_id)
    db.session.delete(category)
    db.session.commit()
    return success({"message": f"Category '{category.name}' and its expenses deleted"})


# ─── Summary ─────────────────────────────────────────────────────────────────

@summary_bp.route("", methods=["GET"])
def get_summary():
    """Monthly summary with per-category breakdown."""
    today = date.today()
    year = request.args.get("year", default=today.year, type=int)
    month = request.args.get("month", default=today.month, type=int)

    # Total for the month
    monthly_total = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .scalar()
        or 0
    )

    # Per-category breakdown
    breakdown = (
        db.session.query(Category.name, Category.color, func.sum(Expense.amount).label("total"))
        .join(Expense, Expense.category_id == Category.id)
        .filter(
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .group_by(Category.id)
        .order_by(func.sum(Expense.amount).desc())
        .all()
    )

    # Uncategorized
    uncategorized = (
        db.session.query(func.sum(Expense.amount))
        .filter(
            Expense.category_id.is_(None),
            extract("year", Expense.date) == year,
            extract("month", Expense.date) == month,
        )
        .scalar()
        or 0
    )

    return success({
        "year": year,
        "month": month,
        "total": float(monthly_total),
        "by_category": [
            {"category": name, "color": color, "total": float(total)}
            for name, color, total in breakdown
        ],
        "uncategorized": float(uncategorized),
    })
