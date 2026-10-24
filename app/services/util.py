from datetime import date as Date
import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.model import Expense


class ExpenseNotFoundError(Exception):
    """The expense doesn't exist OR belongs to another user.

    Both cases raise the same error on purpose, so nobody can probe which
    ids exist.
    """


# ************* helper ****************

def parse_date(value: str) -> Date:
    """Parse a date in YYYY-MM-DD format."""
    try:
        return Date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("Invalid date. Use YYYY-MM-DD format.") from exc

def _parse_range(
    start_date: str,
    end_date: str,
) -> tuple[Date, Date]:
    """Parse and validate an inclusive date range."""
    start = parse_date(start_date)
    end = parse_date(end_date)

    if start > end:
        raise ValueError(
            "start_date must be before or equal to end_date."
        )

    return start, end


def to_dict(expense: Expense) -> dict[str, Any]:
    """Plain-dict view of an expense, safe to return from a tool."""
    return {
        "id": expense.id,
        "date": str(expense.date),
        "amount": str(expense.amount),
        "category": expense.category,
        "subcategory": expense.subcategory,
        "note": expense.note,
    }


async def _get_owned(db: AsyncSession, user_id: str, expense_id: int) -> Expense:
    """Fetch an expense only if it belongs to user_id."""
    result = await db.execute(
        select(Expense).where(Expense.id == expense_id, Expense.user_id == user_id)
    )
    expense = result.scalar_one_or_none()
    if expense is None:
        raise ExpenseNotFoundError(f"Expense {expense_id} not found")
    return expense


# ***************** actions ******************


async def add_expense(
    db: AsyncSession,
    user_id: str,
    *,
    date: str,
    amount: float,
    category: str,
    subcategory: str = "",
    note: str = "",
) -> dict[str, Any]:
    expense = Expense(
        user_id=user_id,
        date=parse_date(date),
        amount=amount,
        category=category,
        subcategory=subcategory,
        note=note,
    )
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return to_dict(expense)


async def update_expense(
    db: AsyncSession,
    user_id: str,
    expense_id: int,
    *,
    amount: float | None = None,
    category: str | None = None,
    subcategory: str | None = None,
    note: str | None = None,
) -> dict[str, Any]:
    expense = await _get_owned(db, user_id, expense_id)

    if amount is not None:
        expense.amount = amount
    if category is not None:
        expense.category = category
    if subcategory is not None:
        expense.subcategory = subcategory
    if note is not None:
        expense.note = note

    await db.commit()
    await db.refresh(expense)
    return to_dict(expense)


async def delete_expense(db: AsyncSession, user_id: str, expense_id: int) -> int:
    """Delete the expense and return its id."""
    expense = await _get_owned(db, user_id, expense_id)
    await db.delete(expense)
    await db.commit()
    return expense_id


async def list_expenses(
    db: AsyncSession, user_id: str, start_date: str, end_date: str
) -> list[dict[str, Any]]:
    start, end = _parse_range(start_date, end_date)
    result = await db.execute(
        select(Expense)
        .where(
            Expense.user_id == user_id,
            Expense.date >= start,
            Expense.date <= end,
        )
        .order_by(Expense.date.asc(), Expense.id.asc())
    )
    return [to_dict(e) for e in result.scalars().all()]


async def summarize_expenses(
    db: AsyncSession,
    user_id: str,
    start_date: str,
    end_date: str,
    category: str | None = None,
) -> list[dict[str, Any]]:
    start, end = _parse_range(start_date, end_date)

    stmt = select(Expense.category, func.sum(Expense.amount).label("total_amount")).where(
        Expense.user_id == user_id,
        Expense.date >= start,
        Expense.date <= end,
    )
    if category:
        stmt = stmt.where(Expense.category == category)

    stmt = stmt.group_by(Expense.category).order_by(Expense.category.asc())

    result = await db.execute(stmt)
    return [
        {"category": row.category, "total_amount": float(row.total_amount)}
        for row in result.all()
    ]