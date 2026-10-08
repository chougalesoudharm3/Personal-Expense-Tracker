#!/usr/bin/env python3
"""Personal Expense Tracker - a simple command-line app.

Features:
  * Add / edit / delete expenses
  * Category-wise expense summary
  * Monthly total
  * Search expenses (by title, category or note)

Data is stored in a local JSON file (expenses.json).
"""

import json
import os
from datetime import datetime

DATA_FILE = "expenses.json"
DATE_FMT = "%Y-%m-%d"


# ---------------------------------------------------------------- storage ---
def load_expenses(path=DATA_FILE):
    """Load expenses from the JSON file (returns [] if none exist)."""
    if not os.path.exists(path):
        return []
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        print("Warning: could not read data file. Starting with empty list.")
        return []


def save_expenses(expenses, path=DATA_FILE):
    """Save expenses to the JSON file."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(expenses, f, indent=2)


def next_id(expenses):
    return max((e["id"] for e in expenses), default=0) + 1


# ---------------------------------------------------------- core functions ---
def add_expense(expenses, title, amount, category, date, note=""):
    expense = {
        "id": next_id(expenses),
        "title": title.strip(),
        "amount": round(float(amount), 2),
        "category": category.strip().title(),
        "date": date,
        "note": note.strip(),
    }
    expenses.append(expense)
    return expense


def find_expense(expenses, expense_id):
    return next((e for e in expenses if e["id"] == expense_id), None)


def edit_expense(expenses, expense_id, **changes):
    """Update fields of an expense. Only non-empty values are applied."""
    expense = find_expense(expenses, expense_id)
    if not expense:
        return None
    for key, value in changes.items():
        if value not in (None, ""):
            if key == "amount":
                value = round(float(value), 2)
            elif key == "category":
                value = value.strip().title()
            expense[key] = value
    return expense


def delete_expense(expenses, expense_id):
    expense = find_expense(expenses, expense_id)
    if expense:
        expenses.remove(expense)
    return expense


def category_totals(expenses):
    """Return {category: total} sorted from highest to lowest."""
    totals = {}
    for e in expenses:
        totals[e["category"]] = totals.get(e["category"], 0) + e["amount"]
    return dict(sorted(totals.items(), key=lambda kv: kv[1], reverse=True))


def monthly_total(expenses, year, month):
    """Return (total, list_of_expenses) for the given month."""
    prefix = f"{year:04d}-{month:02d}"
    items = [e for e in expenses if e["date"].startswith(prefix)]
    return round(sum(e["amount"] for e in items), 2), items


def search_expenses(expenses, keyword):
    kw = keyword.lower().strip()
    return [
        e for e in expenses
        if kw in e["title"].lower()
        or kw in e["category"].lower()
        or kw in e["note"].lower()
    ]


# ---------------------------------------------------------------- display ---
def print_table(items):
    if not items:
        print("\nNo expenses found.")
        return
    print(f"\n{'ID':<4} {'Date':<11} {'Title':<20} {'Category':<14} {'Amount':>10}  Note")
    print("-" * 75)
    for e in sorted(items, key=lambda x: x["date"]):
        print(f"{e['id']:<4} {e['date']:<11} {e['title'][:19]:<20} "
              f"{e['category'][:13]:<14} {e['amount']:>10.2f}  {e['note']}")
    print("-" * 75)
    print(f"{'Total':<51} {sum(e['amount'] for e in items):>10.2f}")


# ------------------------------------------------------------ input helpers ---
def ask_amount(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if allow_blank and raw == "":
            return ""
        try:
            value = float(raw)
            if value <= 0:
                raise ValueError
            return value
        except ValueError:
            print("  Please enter a positive number.")


def ask_date(prompt, allow_blank=False):
    while True:
        raw = input(prompt).strip()
        if raw == "":
            return "" if allow_blank else datetime.now().strftime(DATE_FMT)
        try:
            datetime.strptime(raw, DATE_FMT)
            return raw
        except ValueError:
            print("  Use format YYYY-MM-DD.")


def ask_id(prompt):
    try:
        return int(input(prompt).strip())
    except ValueError:
        return None


# ------------------------------------------------------------ menu actions ---
def ui_add(expenses):
    title = input("Title: ").strip()
    if not title:
        print("Title cannot be empty.")
        return
    amount = ask_amount("Amount: ")
    category = input("Category (e.g. Food, Travel, Bills): ").strip() or "Other"
    date = ask_date("Date YYYY-MM-DD (blank = today): ")
    note = input("Note (optional): ")
    add_expense(expenses, title, amount, category, date, note)
    save_expenses(expenses)
    print("Expense added.")


def ui_edit(expenses):
    expense_id = ask_id("Expense ID to edit: ")
    expense = find_expense(expenses, expense_id) if expense_id else None
    if not expense:
        print("Expense not found.")
        return
    print("Leave a field blank to keep its current value.")
    title = input(f"Title [{expense['title']}]: ")
    amount = ask_amount(f"Amount [{expense['amount']}]: ", allow_blank=True)
    category = input(f"Category [{expense['category']}]: ")
    date = ask_date(f"Date [{expense['date']}]: ", allow_blank=True)
    note = input(f"Note [{expense['note']}]: ")
    edit_expense(expenses, expense_id, title=title, amount=amount,
                 category=category, date=date, note=note)
    save_expenses(expenses)
    print("Expense updated.")


def ui_delete(expenses):
    expense_id = ask_id("Expense ID to delete: ")
    expense = find_expense(expenses, expense_id) if expense_id else None
    if not expense:
        print("Expense not found.")
        return
    if input(f"Delete '{expense['title']}'? (y/n): ").lower() == "y":
        delete_expense(expenses, expense_id)
        save_expenses(expenses)
        print("Expense deleted.")


def ui_categories(expenses):
    totals = category_totals(expenses)
    if not totals:
        print("\nNo expenses yet.")
        return
    grand = sum(totals.values())
    print(f"\n{'Category':<16} {'Total':>10} {'Share':>8}")
    print("-" * 36)
    for cat, total in totals.items():
        print(f"{cat:<16} {total:>10.2f} {total / grand * 100:>7.1f}%")
    print("-" * 36)
    print(f"{'All':<16} {grand:>10.2f}")


def ui_monthly(expenses):
    now = datetime.now()
    raw = input(f"Month YYYY-MM (blank = {now:%Y-%m}): ").strip()
    try:
        dt = datetime.strptime(raw, "%Y-%m") if raw else now
    except ValueError:
        print("Use format YYYY-MM.")
        return
    total, items = monthly_total(expenses, dt.year, dt.month)
    print(f"\nExpenses for {dt:%B %Y}")
    print_table(items)
    print(f"Monthly total: {total:.2f}")


def ui_search(expenses):
    keyword = input("Search keyword: ")
    print_table(search_expenses(expenses, keyword))


MENU = """
===== Personal Expense Tracker =====
1. Add expense
2. Edit expense
3. Delete expense
4. View all expenses
5. Category-wise summary
6. Monthly total
7. Search expenses
0. Exit
"""


def main():
    expenses = load_expenses()
    actions = {
        "1": ui_add,
        "2": ui_edit,
        "3": ui_delete,
        "4": lambda ex: print_table(ex),
        "5": ui_categories,
        "6": ui_monthly,
        "7": ui_search,
    }
    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()
        if choice == "0":
            print("Goodbye!")
            break
        action = actions.get(choice)
        if action:
            action(expenses)
        else:
            print("Invalid option.")


if __name__ == "__main__":
    main()
