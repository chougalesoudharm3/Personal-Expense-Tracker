# 💰 Personal Expense Tracker

A simple, dependency-free command-line application to track your daily spending, built with Python.

## Features

- **Add / Edit / Delete** expenses
- **Category-wise summary** with totals and percentage share
- **Monthly total** with a list of that month's expenses
- **Search** by title, category or note
- Data saved automatically to a local `expenses.json` file

## Requirements

- Python 3.7 or higher (no external libraries needed)

## Getting Started

```bash
git clone https://github.com/<your-username>/expense-tracker.git
cd expense-tracker
python expense_tracker.py
```

## Usage

```
===== Personal Expense Tracker =====
1. Add expense
2. Edit expense
3. Delete expense
4. View all expenses
5. Category-wise summary
6. Monthly total
7. Search expenses
0. Exit
```

### Example

```
Choose an option: 1
Title: Lunch
Amount: 12.50
Category (e.g. Food, Travel, Bills): food
Date YYYY-MM-DD (blank = today):
Note (optional): With friends
Expense added.
```

Category summary:

```
Category            Total    Share
------------------------------------
Food                85.50    57.0%
Travel              40.00    26.7%
Bills               24.50    16.3%
```

## Project Structure

```
expense-tracker/
├── expense_tracker.py   # Main application
├── expenses.json        # Auto-generated data file (git-ignored)
├── README.md
└── .gitignore
```

## How It Works

| Feature | Function |
|---|---|
| Add | `add_expense()` |
| Edit | `edit_expense()` |
| Delete | `delete_expense()` |
| Category-wise | `category_totals()` |
| Monthly total | `monthly_total()` |
| Search | `search_expenses()` |

Core logic is separated from the menu/UI code, so it is easy to test or reuse.

## Future Improvements

- Export to CSV / Excel
- Budget limits and alerts
- Charts (matplotlib)
- GUI or web version (Tkinter / Flask)

## License

MIT License – free to use and modify.
