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