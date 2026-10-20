import pytest

import expense_server


@pytest.fixture(autouse=True)
def temp_db(tmp_path, monkeypatch):
    """Every test uses its own temporary database, so expenses.db is never touched."""
    monkeypatch.setattr(expense_server, "DB_PATH", str(tmp_path / "test.db"))


def test_add_expense_saves_valid_expense():
    result = expense_server.add_expense(250, "food", "lunch", "2026-10-05")
    assert result.startswith("Saved")
    assert "250.00" in result


def test_add_expense_rejects_negative_amount():
    result = expense_server.add_expense(-5, "food")
    assert result == "Error: amount must be greater than 0."


def test_add_expense_rejects_bad_date():
    result = expense_server.add_expense(100, "food", "", "20-10-2026")
    assert result.startswith("Error")


def test_monthly_total_adds_up_correctly():
    expense_server.add_expense(250, "food", "", "2026-10-05")
    expense_server.add_expense(120, "travel", "", "2026-10-06")
    result = expense_server.monthly_total("2026-10")
    assert "370.00" in result
    assert "2 expenses" in result


def test_top_categories_orders_by_amount():
    expense_server.add_expense(250, "food", "", "2026-10-05")
    expense_server.add_expense(50, "food", "", "2026-10-07")
    expense_server.add_expense(120, "travel", "", "2026-10-06")
    result = expense_server.top_categories("2026-10")
    assert "1. food: Rs.300.00" in result
    assert "2. travel: Rs.120.00" in result