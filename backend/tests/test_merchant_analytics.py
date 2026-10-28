"""Tests for deterministic merchant spending analytics."""

from decimal import Decimal
from pathlib import Path

import pytest

from app.analytics.merchants import calculate_top_merchants
from app.services.transaction_loader import load_transactions_from_csv


FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


def test_top_merchants_are_ranked_by_spending() -> None:
    """Merchants should be ranked by total expense magnitude."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    merchants = calculate_top_merchants(transactions)

    assert merchants[0].merchant == "Landlord"
    assert merchants[0].amount == Decimal("2000.00")
    assert merchants[0].transaction_count == 2

    assert merchants[1].merchant == "Mercadona"
    assert merchants[1].amount == Decimal("450.00")
    assert merchants[1].transaction_count == 2


def test_top_merchants_limit_is_respected() -> None:
    """The requested ranking limit should constrain the result."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    merchants = calculate_top_merchants(
        transactions,
        limit=2,
    )

    assert len(merchants) == 2


def test_income_and_transfers_are_not_merchants_spending() -> None:
    """Only expenses should contribute to merchant analytics."""
    transactions = load_transactions_from_csv(FIXTURE_PATH)

    merchants = calculate_top_merchants(transactions)

    merchant_names = {merchant.merchant for merchant in merchants}

    assert "Employer" not in merchant_names


def test_invalid_top_merchants_limit_is_rejected() -> None:
    """Ranking limits must be positive."""
    with pytest.raises(ValueError, match="limit must be greater than zero"):
        calculate_top_merchants([], limit=0)