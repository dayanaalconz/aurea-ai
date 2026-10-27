# Synthetic Financial Data

This directory contains deterministic synthetic datasets used to develop and
validate AUREA's financial data and analytics components.

No real financial or personal data is included.

## Ground-Truth Fixture

`transactions_fixture.csv` is a deliberately small dataset whose expected
financial metrics can be verified manually.

### January 2026

Income:

3000.00 EUR

Expenses:

- Housing: 1000.00 EUR
- Groceries: 200.00 EUR
- Restaurants: 100.00 EUR

Total expenses:

1300.00 EUR

Net cash flow excluding internal transfers:

1700.00 EUR

### February 2026

Income:

3000.00 EUR

Expenses:

- Housing: 1000.00 EUR
- Groceries: 250.00 EUR
- Restaurants: 200.00 EUR

Total expenses:

1450.00 EUR

Net cash flow excluding internal transfers:

1550.00 EUR

### Month-over-Month Expense Change

February expenses increased from 1300.00 EUR to 1450.00 EUR.

Absolute increase:

150.00 EUR

Percentage increase:

11.54%

Category contribution to the increase:

- Groceries: +50.00 EUR
- Restaurants: +100.00 EUR
- Housing: 0.00 EUR

Internal transfers must not contribute to income, expenses, or net cash flow.