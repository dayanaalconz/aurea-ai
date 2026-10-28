"""Integration tests for the transaction ingestion API."""

from pathlib import Path

from fastapi.testclient import TestClient


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_valid_csv_upload_persists_transactions(
    empty_api_client: TestClient,
) -> None:
    """A valid CSV should be validated and persisted atomically."""
    with FIXTURE_PATH.open("rb") as csv_file:
        response = empty_api_client.post(
            "/transactions/upload",
            files={
                "file": (
                    "transactions.csv",
                    csv_file,
                    "text/csv",
                )
            },
        )

    assert response.status_code == 201

    assert response.json() == {
        "status": "success",
        "imported_transactions": 12,
    }

def test_uploaded_transactions_are_available_to_analytics(
    empty_api_client: TestClient,
) -> None:
    """Analytics should immediately reflect successfully uploaded data."""
    with FIXTURE_PATH.open("rb") as csv_file:
        upload_response = empty_api_client.post(
            "/transactions/upload",
            files={
                "file": (
                    "transactions.csv",
                    csv_file,
                    "text/csv",
                )
            },
        )

    assert upload_response.status_code == 201

    analytics_response = empty_api_client.get("/analytics/summary")

    assert analytics_response.status_code == 200
    assert analytics_response.json() == {
        "total_income": "6000.00",
        "total_expenses": "2750.00",
        "net_cash_flow": "3250.00",
        "currency": "EUR",
    }

def test_non_csv_upload_is_rejected(
    empty_api_client: TestClient,
) -> None:
    """The upload endpoint should reject unsupported file extensions."""
    response = empty_api_client.post(
        "/transactions/upload",
        files={
            "file": (
                "transactions.txt",
                b"not a csv file",
                "text/plain",
            )
        },
    )

    assert response.status_code == 400
    assert response.json() == {
        "detail": "Only CSV files are supported.",
    }

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

def test_failed_upload_does_not_partially_persist_data(
    empty_api_client: TestClient,
) -> None:
    """A failed batch must leave the database unchanged."""
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