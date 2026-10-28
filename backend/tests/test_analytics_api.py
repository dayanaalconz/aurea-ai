"""Tests for the financial analytics API."""

from fastapi.testclient import TestClient


def test_financial_summary_endpoint(api_client: TestClient) -> None:
    """The summary endpoint should expose persisted financial metrics."""
    response = api_client.get("/analytics/summary")

    assert response.status_code == 200

    assert response.json() == {
        "total_income": "6000.00",
        "total_expenses": "2750.00",
        "net_cash_flow": "3250.00",
        "currency": "EUR",
    }

def test_spending_by_category_endpoint(api_client: TestClient) -> None:
    """Category endpoint should return ranked persisted spending."""
    response = api_client.get("/analytics/spending-by-category")

    assert response.status_code == 200

    assert response.json() == {
        "currency": "EUR",
        "categories": [
            {
                "category": "housing",
                "amount": "2000.00",
            },
            {
                "category": "groceries",
                "amount": "450.00",
            },
            {
                "category": "restaurants",
                "amount": "300.00",
            },
        ],
    }

def test_monthly_trends_endpoint(api_client: TestClient) -> None:
    """Monthly trends endpoint should expose chronological persisted metrics."""
    response = api_client.get("/analytics/monthly-trends")

    assert response.status_code == 200

    assert response.json() == {
        "currency": "EUR",
        "months": [
            {
                "month": "2026-01",
                "total_income": "3000.00",
                "total_expenses": "1300.00",
                "net_cash_flow": "1700.00",
                "transaction_count": 4,
            },
            {
                "month": "2026-02",
                "total_income": "3000.00",
                "total_expenses": "1450.00",
                "net_cash_flow": "1550.00",
                "transaction_count": 4,
            },
        ],
    }

def test_top_merchants_endpoint(api_client: TestClient) -> None:
    """Top merchants endpoint should expose ranked persisted spending."""
    response = api_client.get("/analytics/top-merchants?limit=2")

    assert response.status_code == 200

    assert response.json() == {
        "currency": "EUR",
        "merchants": [
            {
                "merchant": "Landlord",
                "amount": "2000.00",
                "transaction_count": 2,
            },
            {
                "merchant": "Mercadona",
                "amount": "450.00",
                "transaction_count": 2,
            },
        ],
    }

def test_largest_expenses_endpoint(api_client: TestClient) -> None:
    """Largest expenses endpoint should expose ranked expense transactions."""
    response = api_client.get("/analytics/largest-expenses?limit=2")

    assert response.status_code == 200

    payload = response.json()

    assert payload["currency"] == "EUR"
    assert len(payload["expenses"]) == 2

    assert payload["expenses"][0] == {
        "transaction_id": "txn_002",
        "transaction_date": "2026-01-06",
        "description": "Rent",
        "amount": "1000.00",
        "category": "housing",
        "merchant": "Landlord",
    }

    assert payload["expenses"][1] == {
        "transaction_id": "txn_008",
        "transaction_date": "2026-02-06",
        "description": "Rent",
        "amount": "1000.00",
        "category": "housing",
        "merchant": "Landlord",
    }

def test_largest_expenses_rejects_invalid_limit(
    api_client: TestClient,
) -> None:
    """Largest expenses endpoint should reject non-positive limits."""
    response = api_client.get("/analytics/largest-expenses?limit=0")

    assert response.status_code == 422

def test_invalid_financial_transaction_is_rejected(
    empty_api_client: TestClient,
) -> None:
    """Financially invalid CSV rows should return HTTP 422."""
    invalid_csv = (
        "transaction_id,account_id,transaction_date,description,"
        "amount,currency,transaction_type,category,merchant\n"
        "txn_invalid,checking_001,2026-03-01,"
        "Invalid expense,50.00,EUR,expense,groceries,Test Merchant\n"
    )

    response = empty_api_client.post(
        "/transactions/upload",
        files={
            "file": (
                "invalid_transactions.csv",
                invalid_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 422
    assert response.json() == {
        "detail": "The CSV contains invalid transaction data.",
    }

def test_duplicate_transaction_ids_return_conflict(
    empty_api_client: TestClient,
) -> None:
    """Duplicate transaction IDs should return HTTP 409."""
    duplicate_csv = (
        "transaction_id,account_id,transaction_date,description,"
        "amount,currency,transaction_type,category,merchant\n"
        "txn_duplicate,checking_001,2026-03-01,"
        "Groceries,-20.00,EUR,expense,groceries,Merchant A\n"
        "txn_duplicate,checking_001,2026-03-02,"
        "Restaurant,-40.00,EUR,expense,restaurants,Merchant B\n"
    )

    response = empty_api_client.post(
        "/transactions/upload",
        files={
            "file": (
                "duplicate_transactions.csv",
                duplicate_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert response.status_code == 409
    assert response.json() == {
        "detail": (
            "The CSV contains transactions that conflict "
            "with existing records."
        ),
    }

def test_failed_duplicate_upload_leaves_database_unchanged(
    empty_api_client: TestClient,
) -> None:
    """A failed batch should leave no partially persisted transactions."""
    duplicate_csv = (
        "transaction_id,account_id,transaction_date,description,"
        "amount,currency,transaction_type,category,merchant\n"
        "txn_duplicate,checking_001,2026-03-01,"
        "Groceries,-20.00,EUR,expense,groceries,Merchant A\n"
        "txn_duplicate,checking_001,2026-03-02,"
        "Restaurant,-40.00,EUR,expense,restaurants,Merchant B\n"
    )

    upload_response = empty_api_client.post(
        "/transactions/upload",
        files={
            "file": (
                "duplicate_transactions.csv",
                duplicate_csv.encode("utf-8"),
                "text/csv",
            )
        },
    )

    assert upload_response.status_code == 409

    summary_response = empty_api_client.get("/analytics/summary")

    assert summary_response.status_code == 200
    assert summary_response.json() == {
        "total_income": "0.00",
        "total_expenses": "0.00",
        "net_cash_flow": "0.00",
        "currency": "EUR",
    }