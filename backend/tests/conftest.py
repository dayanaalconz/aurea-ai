"""Shared pytest fixtures for AUREA API tests."""

from collections.abc import Generator
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.pool import StaticPool
from app.data.database import Base, get_db_session
from app.data.repositories.transaction import TransactionRepository
from app.main import app
from app.services.transaction_loader import load_transactions_from_csv
from app.ai.tools.financial import FinancialTools
from app.services.financial_analytics import FinancialAnalyticsService

FIXTURE_PATH = (
    Path(__file__).resolve().parents[2]
    / "datasets"
    / "synthetic"
    / "transactions_fixture.csv"
)


@pytest.fixture
def api_client() -> Generator[TestClient, None, None]:
    """Provide an API client backed by an isolated populated SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

    def override_db_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db_session

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()

@pytest.fixture
def empty_api_client() -> Generator[TestClient, None, None]:
    """Provide an API client backed by an empty isolated SQLite database."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    def override_db_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_db_session] = override_db_session

    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(engine)
        engine.dispose()

@pytest.fixture
def financial_tools() -> Generator[FinancialTools, None, None]:
    """Provide financial AI tools backed by populated test data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        analytics_service = FinancialAnalyticsService(repository)
        tools = FinancialTools(analytics_service)

        yield tools

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def financial_tools() -> Generator[FinancialTools, None, None]:
    """Provide financial AI tools backed by deterministic test data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        analytics_service = FinancialAnalyticsService(repository)
        tools = FinancialTools(analytics_service)

        yield tools

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def financial_tools() -> Generator[FinancialTools, None, None]:
    """Provide financial AI tools backed by deterministic test data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        analytics_service = FinancialAnalyticsService(repository)
        tools = FinancialTools(analytics_service)

        yield tools

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def populated_session() -> Generator[Session, None, None]:
    """Provide a database session populated with ground-truth transactions."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        yield session

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def financial_tools() -> Generator[FinancialTools, None, None]:
    """Provide financial AI tools backed by deterministic test data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        analytics_service = FinancialAnalyticsService(repository)
        tools = FinancialTools(analytics_service)

        yield tools

    Base.metadata.drop_all(engine)
    engine.dispose()

@pytest.fixture
def financial_tools() -> Generator[FinancialTools, None, None]:
    """Provide financial AI tools backed by deterministic fixture data."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(engine)

    transactions = load_transactions_from_csv(FIXTURE_PATH)

    with Session(engine) as session:
        repository = TransactionRepository(session)
        repository.add_many(transactions)

        analytics_service = FinancialAnalyticsService(repository)
        tools = FinancialTools(analytics_service)

        yield tools

    Base.metadata.drop_all(engine)
    engine.dispose()