# AUREA Canonical Transaction Schema

## 1. Purpose

This document defines the canonical financial transaction model used by AUREA.

All imported transaction data must be validated and normalized into this
representation before it can be persisted or used by the financial analytics
engine.

The canonical schema is intentionally independent from any specific bank,
CSV format, or external data provider.

## 2. Design Principles

The transaction model follows these principles:

1. Financial calculations must be deterministic and reproducible.
2. Transaction semantics must not depend on an LLM.
3. Income, expenses, and transfers must be distinguishable explicitly.
4. Internal transfers must not inflate income or expense metrics.
5. Monetary values must use decimal arithmetic rather than binary floating point.
6. Currency must be explicit for every transaction.
7. Validation errors must be detectable before persistence.
8. The normalized model must preserve enough source information for auditing.

## 3. Canonical Schema

| Field | Type | Required | Description |
|---|---|---:|---|
| transaction_id | string | Yes | Unique identifier of the normalized transaction |
| account_id | string | Yes | Identifier of the account associated with the transaction |
| transaction_date | date | Yes | Effective transaction date |
| description | string | Yes | Normalized human-readable transaction description |
| amount | decimal | Yes | Signed monetary amount in the transaction currency |
| currency | string | Yes | ISO 4217 currency code |
| transaction_type | enum | Yes | Financial classification of the transaction |
| category | string | No | Normalized analytical spending/income category |
| merchant | string | No | Normalized merchant or counterparty when available |

## 4. Amount Convention

AUREA uses a signed cash-flow convention from the perspective of the account
owner.

- Positive amounts represent money entering an owned account.
- Negative amounts represent money leaving an owned account.
- Zero-value transactions are invalid in the initial canonical model.

Examples:

| Description | Amount | Meaning |
|---|---:|---|
| Monthly salary | 2800.00 | Cash inflow |
| Grocery purchase | -64.35 | Cash outflow |
| Restaurant payment | -32.50 | Cash outflow |
| Incoming refund | 32.50 | Cash inflow associated with a previous expense |

The sign of `amount` represents movement of money, while `transaction_type`
represents the financial meaning of the transaction.

## 5. Transaction Types

The initial canonical transaction types are:

### `income`

Money received that represents economic income.

Examples:

- Salary
- Bonus
- Interest income

Expected amount sign: positive.

### `expense`

Money spent on goods, services, or other external outflows.

Examples:

- Groceries
- Rent
- Restaurants
- Utilities
- Subscriptions

Expected amount sign: negative.

### `transfer`

Movement of money between accounts that does not represent new income or
consumption.

Transfers between accounts owned by the same user are excluded from income
and expense metrics.

Depending on the account side being represented, transfer amounts may be
positive or negative.

### `refund`

Money returned as a reversal or partial reversal of a previous expense.

Expected amount sign: positive.

Refunds are tracked separately from income so they do not artificially inflate
income metrics.

## 6. Core Invariants

A valid canonical transaction must satisfy the following rules:

1. `transaction_id` must not be empty.
2. `account_id` must not be empty.
3. `transaction_date` must be a valid date.
4. `description` must contain non-whitespace characters.
5. `amount` must be a valid decimal value.
6. `amount` must not be zero.
7. `currency` must be present and normalized to uppercase.
8. `transaction_type` must be one of the supported canonical transaction types.
9. `income` transactions must have a positive amount.
10. `expense` transactions must have a negative amount.
11. `refund` transactions must have a positive amount.
12. `transfer` transactions may have either sign.