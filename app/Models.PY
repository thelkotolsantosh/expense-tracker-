from datetime import datetime, timezone
from app import db


class Category(db.Model):
    __tablename__ = "categories"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(64), nullable=False, unique=True)
    color = db.Column(db.String(7), default="#3498db")  # hex color
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    expenses = db.relationship("Expense", backref="category", lazy="dynamic", cascade="all, delete-orphan")

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "color": self.color,
            "expense_count": self.expenses.count(),
            "created_at": self.created_at.isoformat(),
        }

    def __repr__(self):
        return f"<Category {self.name}>"


class Expense(db.Model):
    __tablename__ = "expenses"

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(128), nullable=False)
    amount = db.Column(db.Numeric(10, 2), nullable=False)
    note = db.Column(db.Text, nullable=True)
    date = db.Column(db.Date, nullable=False, default=lambda: datetime.now(timezone.utc).date())
    category_id = db.Column(db.Integer, db.ForeignKey("categories.id"), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = db.Column(
        db.DateTime,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "amount": float(self.amount),
            "note": self.note,
            "date": self.date.isoformat(),
            "category": self.category.to_dict() if self.category else None,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def __repr__(self):
        return f"<Expense {self.title} ${self.amount}>"
