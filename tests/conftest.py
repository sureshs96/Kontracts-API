"""
Pytest configuration and fixtures.

This module provides shared fixtures and configuration for all tests.
Following PostgreSQL best practices:
- Use PostgreSQL database from tests/.env file
- Rollback transactions after each test
- Isolate test data
- Use Alembic migrations for test database setup
"""

import os
import pytest
from typing import Generator
from pathlib import Path
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from fastapi.testclient import TestClient
from alembic import command
from alembic.config import Config
from dotenv import load_dotenv

from app.database import Base, get_db
from app.main import app
from app.models.lease import Lease, LeaseScheduleEntry, LeaseClassification
from app.models.schedule import ASC842Schedule, IFRS16Schedule
from app.models.user import Users
from app.models.journals import (
    JournalEntries,
    JournalEntrySetups,
    Payments,
    Documents,
)

# Load test environment variables from tests/.env
test_env_path = Path(__file__).parent / ".env"
load_dotenv(dotenv_path=test_env_path)


@pytest.fixture(scope="session")
def database_url():
    """
    Get database URL from tests/.env file.

    Returns a connection URL for the test PostgreSQL database.
    """
    db_url = os.getenv("DATABASE_URL")
    if not db_url:
        raise ValueError(
            "DATABASE_URL not found in tests/.env file.\n"
            "Please create tests/.env with DATABASE_URL=postgresql://user:pass@host:port/dbname"
        )
    return db_url


@pytest.fixture(scope="session")
def engine(database_url):
    """
    Create a test database engine.

    Scope: session - created once per test session
    PostgreSQL best practice: Use a separate test database

    This connects to the PostgreSQL database specified in tests/.env
    """
    # Create engine
    test_engine = create_engine(
        database_url,
        echo=False,  # Set to True for SQL debugging
        pool_pre_ping=True,  # Verify connections before using
    )

    # Create kontracts schema
    with test_engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS kontracts"))

    # Run Alembic migrations to set up the database schema
    alembic_cfg = Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", database_url)

    # Run migrations
    command.upgrade(alembic_cfg, "head")

    yield test_engine

    # Cleanup: drop all tables, types, and schema after entire test session
    with test_engine.begin() as conn:
        # Drop the schema with all its contents
        conn.execute(text("DROP SCHEMA IF EXISTS kontracts CASCADE"))
        # Drop enum types that may have been created in public schema
        conn.execute(text("DROP TYPE IF EXISTS leaseclassification CASCADE"))
    test_engine.dispose()


@pytest.fixture(scope="function")
def db_session(engine) -> Generator[Session, None, None]:
    """
    Create a new database session for a test.

    Scope: function - new session per test
    PostgreSQL best practice: Use transactions that rollback after each test
    This ensures test isolation and prevents test data pollution.
    """
    connection = engine.connect()
    transaction = connection.begin()

    # Create session bound to the connection
    TestSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=connection
    )
    session = TestSessionLocal()

    yield session

    # Rollback transaction to undo all changes made during the test
    session.close()
    transaction.rollback()
    connection.close()


@pytest.fixture(scope="function")
def client(db_session: Session) -> Generator[TestClient, None, None]:
    """
    Create a test client with a test database session.

    This fixture overrides the get_db dependency to use our test database.
    """
    def override_get_db():
        try:
            yield db_session
        finally:
            pass  # Don't close here, managed by db_session fixture

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()


# Sample data fixtures

@pytest.fixture
def sample_lease_data():
    """Sample lease data for testing"""
    return {
        "lease_name": "Office Space Lease",
        "lessor_name": "ABC Properties",
        "lessee_name": "Tech Startup Inc",
        "commencement_date": "2024-01-01",
        "lease_term_months": 36,
        "periodic_payment": 5000.00,
        "payment_frequency": "monthly",
        "initial_direct_costs": 1000.00,
        "prepaid_rent": 0.00,
        "lease_incentives": 0.00,
        "residual_value": 0.00,
        "incremental_borrowing_rate": 0.05,
        "discount_rate": 0.05,
        "classification": "operating",
        "contract_type": "lease",
        "status": "active"
    }


@pytest.fixture
def sample_lease(db_session: Session, sample_lease_data):
    """Create and return a sample lease in the database"""
    lease = Lease(**sample_lease_data)
    db_session.add(lease)
    db_session.commit()
    db_session.refresh(lease)
    return lease


@pytest.fixture
def sample_finance_lease_data():
    """Sample finance lease data for testing"""
    return {
        "lease_name": "Equipment Lease",
        "lessor_name": "Equipment Leasing Co",
        "lessee_name": "Manufacturing Corp",
        "commencement_date": "2024-01-01",
        "lease_term_months": 60,
        "periodic_payment": 10000.00,
        "payment_frequency": "monthly",
        "initial_direct_costs": 5000.00,
        "prepaid_rent": 10000.00,
        "lease_incentives": 2000.00,
        "residual_value": 50000.00,
        "incremental_borrowing_rate": 0.06,
        "discount_rate": 0.06,
        "classification": "finance",
        "contract_type": "lease",
        "status": "active"
    }


@pytest.fixture
def sample_finance_lease(db_session: Session, sample_finance_lease_data):
    """Create and return a sample finance lease in the database"""
    lease = Lease(**sample_finance_lease_data)
    db_session.add(lease)
    db_session.commit()
    db_session.refresh(lease)
    return lease


@pytest.fixture
def sample_user_data():
    """Sample user data for testing"""
    return {
        "username": "testuser",
        "password": "securepassword123",
        "name": "Test User",
        "role": "Contract Administrator"
    }


@pytest.fixture
def sample_user(db_session: Session, sample_user_data):
    """Create and return a sample user in the database"""
    user = Users(**sample_user_data)
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user


@pytest.fixture
def sample_journal_entry_data(sample_lease):
    """Sample journal entry data for testing"""
    return {
        "contract_id": str(sample_lease.id),
        "entry_date": "2024-01-01T00:00:00",
        "description": "Initial ROU Asset recognition",
        "debit_account": "Right-of-Use Asset",
        "credit_account": "Lease Liability",
        "amount": 150000.00,
        "reference": "LEASE-001"
    }


@pytest.fixture
def cleanup_database(db_session: Session):
    """
    Cleanup fixture to ensure clean database state.

    PostgreSQL best practice: Clean up in reverse order of foreign key dependencies
    """
    yield

    # Clean up in reverse order of dependencies
    db_session.query(LeaseScheduleEntry).delete()
    db_session.query(ASC842Schedule).delete()
    db_session.query(IFRS16Schedule).delete()
    db_session.query(JournalEntries).delete()
    db_session.query(JournalEntrySetups).delete()
    db_session.query(Payments).delete()
    db_session.query(Documents).delete()
    db_session.query(Lease).delete()
    db_session.query(Users).delete()
    db_session.commit()
