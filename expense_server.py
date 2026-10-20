import os
import sqlite3
from datetime import date, datetime

from mcp.server.fastmcp import FastMCP

# The database file is saved next to this script (can be changed with EXPENSE_DB).
DB_PATH = os.environ.get(
    "EXPENSE_DB",
    os.path.join(os.path.dirname(os.path.abspath(__file__)), "expenses.db"),
)

mcp = FastMCP("expense-tracker")


def get_connection():
    """Open the database and create the table if it does not exist."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            amount REAL NOT NULL,
            category TEXT NOT NULL,
            description TEXT,
            date TEXT NOT NULL
        )
        """
    )
    return conn


def current_month():
    return date.today().strftime("%Y-%m")


@mcp.tool()
def add_expense(amount: float, category: str, description: str = "", expense_date: str = "") -> str:
    """Save a new expense. amount must be greater than 0. category is a word like food or travel.
    expense_date is optional, format YYYY-MM-DD (default is today)."""
    if amount <= 0:
        return "Error: amount must be greater than 0."
    category = category.strip().lower()
    if not category:
        return "Error: category cannot be empty."
    if not expense_date:
        expense_date = date.today().isoformat()
    try:
        datetime.strptime(expense_date, "%Y-%m-%d")
    except ValueError:
        return "Error: expense_date must look like 2026-10-20 (YYYY-MM-DD)."
    conn = get_connection()
    with conn:
        conn.execute(
            "INSERT INTO expenses (amount, category, description, date) VALUES (?, ?, ?, ?)",
            (amount, category, description, expense_date),
        )
    conn.close()
    return f"Saved: Rs.{amount:.2f} on {category} ({expense_date})."


@mcp.tool()
def monthly_total(month: str = "") -> str:
    """Get the total amount spent in a month. month format is YYYY-MM (default is the current month)."""
    if not month:
        month = current_month()
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        return "Error: month must look like 2026-10 (YYYY-MM)."
    conn = get_connection()
    total, count = conn.execute(
        "SELECT COALESCE(SUM(amount), 0), COUNT(*) FROM expenses WHERE substr(date, 1, 7) = ?",
        (month,),
    ).fetchone()
    conn.close()
    if count == 0:
        return f"No expenses found for {month}."
    return f"Total for {month}: Rs.{total:.2f} across {count} expenses."


@mcp.tool()
def top_categories(month: str = "", limit: int = 3) -> str:
    """List the categories where the most money was spent in a month. month format is YYYY-MM (default current month)."""
    if not month:
        month = current_month()
    try:
        datetime.strptime(month, "%Y-%m")
    except ValueError:
        return "Error: month must look like 2026-10 (YYYY-MM)."
    if limit < 1:
        return "Error: limit must be at least 1."
    conn = get_connection()
    rows = conn.execute(
        "SELECT category, SUM(amount) AS total FROM expenses "
        "WHERE substr(date, 1, 7) = ? GROUP BY category ORDER BY total DESC LIMIT ?",
        (month, limit),
    ).fetchall()
    conn.close()
    if not rows:
        return f"No expenses found for {month}."
    lines = [f"{i}. {cat}: Rs.{total:.2f}" for i, (cat, total) in enumerate(rows, start=1)]
    return f"Top categories for {month}:\n" + "\n".join(lines)
@mcp.resource("expenses://current-month")
def current_month_expenses() -> str:
    """All expenses recorded in the current month."""
    month = current_month()
    conn = get_connection()
    rows = conn.execute(
        "SELECT date, category, amount, description FROM expenses "
        "WHERE substr(date, 1, 7) = ? ORDER BY date",
        (month,),
    ).fetchall()
    conn.close()
    if not rows:
        return f"No expenses recorded for {month}."
    lines = [f"{d} | {c} | Rs.{a:.2f} | {desc or '-'}" for d, c, a, desc in rows]
    return f"Expenses for {month}:\n" + "\n".join(lines)


@mcp.prompt(name="budget-summary")
def budget_summary(month: str = "") -> str:
    """Ask the AI for a short budget summary of a month."""
    target = month or "the current month"
    return (
        f"Give me a short budget summary for {target}. "
        "Use the monthly_total tool for the total and the top_categories tool "
        "for the biggest categories. Then give one simple tip to save money."
    )

if __name__ == "__main__":
    mcp.run()