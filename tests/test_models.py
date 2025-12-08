"""
Unit tests for database models.

Tests model creation, validation, relationships, and constraints.
Following PostgreSQL best practices:
- Test constraints and data integrity
- Test cascading deletes
- Verify schema enforcement
"""

import pytest
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy.exc import IntegrityError

from app.models.lease import Lease, LeaseScheduleEntry, LeaseClassification
from app.models.schedule import ASC842Schedule, IFRS16Schedule
from app.models.user import Users
from app.models.journals import (
    JournalEntries,
    JournalEntrySetups,
    Payments,
    Documents,
)


@pytest.mark.unit
@pytest.mark.database
class TestLeaseModel:
    """Test Lease model"""

    def test_create_lease_operating(self, db_session, sample_lease_data):
        """Test creating an operating lease"""
        lease = Lease(**sample_lease_data)
        db_session.add(lease)
        db_session.commit()
        db_session.refresh(lease)

        assert lease.id is not None
        assert lease.lease_name == "Office Space Lease"
        assert lease.classification == LeaseClassification.OPERATING
        assert lease.lease_term_months == 36
        assert lease.periodic_payment == Decimal("5000.00")
        assert lease.created_at is not None

    def test_create_lease_finance(self, db_session, sample_finance_lease_data):
        """Test creating a finance lease"""
        lease = Lease(**sample_finance_lease_data)
        db_session.add(lease)
        db_session.commit()
        db_session.refresh(lease)

        assert lease.id is not None
        assert lease.classification == LeaseClassification.FINANCE
        assert lease.residual_value == Decimal("50000.00")
        assert lease.incremental_borrowing_rate == Decimal("0.06")

    def test_lease_required_fields(self, db_session):
        """Test that required fields are enforced"""
        with pytest.raises(Exception):  # Will raise TypeError or IntegrityError
            lease = Lease(
                lease_name="Test Lease"
                # Missing required fields
            )
            db_session.add(lease)
            db_session.commit()

    def test_lease_defaults(self, db_session):
        """Test default values are set correctly"""
        lease = Lease(
            lease_name="Test Lease",
            lessor_name="Test Lessor",
            lessee_name="Test Lessee",
            commencement_date=date(2024, 1, 1),
            lease_term_months=12,
            periodic_payment=Decimal("1000.00")
        )
        db_session.add(lease)
        db_session.commit()
        db_session.refresh(lease)

        assert lease.payment_frequency == "monthly"
        assert lease.initial_direct_costs == Decimal("0")
        assert lease.classification == LeaseClassification.OPERATING
        assert lease.status == "active"

    def test_lease_update(self, db_session, sample_lease):
        """Test updating lease fields"""
        sample_lease.status = "terminated"
        sample_lease.periodic_payment = Decimal("6000.00")
        db_session.commit()
        db_session.refresh(sample_lease)

        assert sample_lease.status == "terminated"
        assert sample_lease.periodic_payment == Decimal("6000.00")

    def test_lease_delete_cascades_to_schedules(self, db_session, sample_lease):
        """Test that deleting a lease cascades to related schedules"""
        # Create related schedule entry
        entry = LeaseScheduleEntry(
            lease_id=sample_lease.id,
            schedule_type="ASC842",
            period=1,
            period_date=date(2024, 2, 1),
            lease_payment=Decimal("5000.00"),
            interest_expense=Decimal("200.00"),
            principal_reduction=Decimal("4800.00"),
            lease_liability_beginning=Decimal("150000.00"),
            lease_liability_ending=Decimal("145200.00"),
            rou_asset_beginning=Decimal("151000.00"),
            amortization=Decimal("4194.44"),
            rou_asset_ending=Decimal("146805.56")
        )
        db_session.add(entry)
        db_session.commit()

        # Delete lease
        db_session.delete(sample_lease)
        db_session.commit()

        # Verify cascade delete
        entries = db_session.query(LeaseScheduleEntry).filter_by(lease_id=sample_lease.id).all()
        assert len(entries) == 0


@pytest.mark.unit
@pytest.mark.database
class TestLeaseScheduleEntry:
    """Test LeaseScheduleEntry model"""

    def test_create_schedule_entry(self, db_session, sample_lease):
        """Test creating a schedule entry"""
        entry = LeaseScheduleEntry(
            lease_id=sample_lease.id,
            schedule_type="ASC842",
            period=1,
            period_date=date(2024, 2, 1),
            lease_payment=Decimal("5000.00"),
            interest_expense=Decimal("625.00"),
            principal_reduction=Decimal("4375.00"),
            lease_liability_beginning=Decimal("150000.00"),
            lease_liability_ending=Decimal("145625.00"),
            rou_asset_beginning=Decimal("151000.00"),
            amortization=Decimal("4194.44"),
            rou_asset_ending=Decimal("146805.56"),
            total_expense=Decimal("4819.44")
        )
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)

        assert entry.id is not None
        assert entry.lease_id == sample_lease.id
        assert entry.period == 1
        assert entry.schedule_type == "ASC842"

    def test_schedule_entry_relationship(self, db_session, sample_lease):
        """Test relationship between lease and schedule entries"""
        entry1 = LeaseScheduleEntry(
            lease_id=sample_lease.id,
            schedule_type="ASC842",
            period=1,
            period_date=date(2024, 2, 1),
            lease_payment=Decimal("5000.00"),
            interest_expense=Decimal("625.00"),
            principal_reduction=Decimal("4375.00"),
            lease_liability_beginning=Decimal("150000.00"),
            lease_liability_ending=Decimal("145625.00"),
            rou_asset_beginning=Decimal("151000.00"),
            amortization=Decimal("4194.44"),
            rou_asset_ending=Decimal("146805.56")
        )
        db_session.add(entry1)
        db_session.commit()

        # Access relationship
        assert len(sample_lease.schedule_entries) == 1
        assert sample_lease.schedule_entries[0].period == 1


@pytest.mark.unit
@pytest.mark.database
class TestUserModel:
    """Test Users model"""

    def test_create_user(self, db_session, sample_user_data):
        """Test creating a user"""
        user = Users(**sample_user_data)
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.id is not None
        assert user.username == "testuser"
        assert user.name == "Test User"
        assert user.role == "Contract Administrator"

    def test_username_unique_constraint(self, db_session, sample_user):
        """Test that username must be unique"""
        # Try to create another user with same username
        duplicate_user = Users(
            username=sample_user.username,
            password="different_password",
            name="Different Name",
            role="Admin"
        )
        db_session.add(duplicate_user)

        with pytest.raises(IntegrityError):
            db_session.commit()

    def test_user_default_role(self, db_session):
        """Test default role is set"""
        user = Users(
            username="newuser",
            password="password123",
            name="New User"
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        assert user.role == "Contract Administrator"


@pytest.mark.unit
@pytest.mark.database
class TestJournalModels:
    """Test journal-related models"""

    def test_create_journal_entry(self, db_session, sample_journal_entry_data):
        """Test creating a journal entry"""
        entry = JournalEntries(**sample_journal_entry_data)
        db_session.add(entry)
        db_session.commit()
        db_session.refresh(entry)

        assert entry.id is not None
        assert entry.debit_account == "Right-of-Use Asset"
        assert entry.credit_account == "Lease Liability"
        assert entry.amount == Decimal("150000.00")
        assert entry.created_at is not None

    def test_create_journal_entry_setup(self, db_session):
        """Test creating a journal entry setup"""
        setup = JournalEntrySetups(
            name="Monthly Lease Expense",
            entry_type="Lease Expense",
            trigger_event="month_end",
            debit_account="Lease Expense",
            credit_account="Lease Liability",
            amount_column="periodic_payment",
            period_reference="n",
            is_active=True,
            description="Automated monthly lease expense entry"
        )
        db_session.add(setup)
        db_session.commit()
        db_session.refresh(setup)

        assert setup.id is not None
        assert setup.is_active is True
        assert setup.trigger_event == "month_end"

    def test_create_payment(self, db_session, sample_lease):
        """Test creating a payment record"""
        payment = Payments(
            contract_id=str(sample_lease.id),
            amount=Decimal("5000.00"),
            due_date=datetime(2024, 2, 1),
            status="Scheduled"
        )
        db_session.add(payment)
        db_session.commit()
        db_session.refresh(payment)

        assert payment.id is not None
        assert payment.status == "Scheduled"
        assert payment.paid_date is None

    def test_update_payment_status(self, db_session, sample_lease):
        """Test updating payment status"""
        payment = Payments(
            contract_id=str(sample_lease.id),
            amount=Decimal("5000.00"),
            due_date=datetime(2024, 2, 1),
            status="Scheduled"
        )
        db_session.add(payment)
        db_session.commit()

        payment.status = "Paid"
        payment.paid_date = datetime(2024, 2, 1)
        db_session.commit()
        db_session.refresh(payment)

        assert payment.status == "Paid"
        assert payment.paid_date is not None

    def test_create_document(self, db_session):
        """Test creating a document record"""
        doc = Documents(
            filename="lease_agreement_001.pdf",
            original_name="Office Lease Agreement.pdf",
            mime_type="application/pdf",
            size=2048576,
            upload_path="/uploads/2024/01/lease_agreement_001.pdf",
            processing_status="completed"
        )
        db_session.add(doc)
        db_session.commit()
        db_session.refresh(doc)

        assert doc.id is not None
        assert doc.processing_status == "completed"
        assert doc.uploaded_at is not None


@pytest.mark.unit
@pytest.mark.database
class TestScheduleModels:
    """Test schedule models"""

    def test_create_asc842_schedule(self, db_session, sample_lease):
        """Test creating an ASC 842 schedule"""
        schedule = ASC842Schedule(
            lease_id=sample_lease.id,
            initial_rou_asset=Decimal("151000.00"),
            initial_lease_liability=Decimal("150000.00"),
            total_lease_cost=Decimal("180000.00"),
            discount_rate=Decimal("0.05")
        )
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.id is not None
        assert schedule.lease_id == sample_lease.id
        assert schedule.initial_rou_asset == Decimal("151000.00")

    def test_create_ifrs16_schedule(self, db_session, sample_lease):
        """Test creating an IFRS 16 schedule"""
        schedule = IFRS16Schedule(
            lease_id=sample_lease.id,
            initial_rou_asset=Decimal("151000.00"),
            initial_lease_liability=Decimal("150000.00"),
            total_lease_payments=Decimal("180000.00"),
            discount_rate=Decimal("0.05")
        )
        db_session.add(schedule)
        db_session.commit()
        db_session.refresh(schedule)

        assert schedule.id is not None
        assert schedule.lease_id == sample_lease.id
        assert schedule.total_lease_payments == Decimal("180000.00")

    def test_schedule_lease_relationship(self, db_session, sample_lease):
        """Test relationship between lease and ASC842 schedule"""
        schedule = ASC842Schedule(
            lease_id=sample_lease.id,
            initial_rou_asset=Decimal("151000.00"),
            initial_lease_liability=Decimal("150000.00"),
            total_lease_cost=Decimal("180000.00"),
            discount_rate=Decimal("0.05")
        )
        db_session.add(schedule)
        db_session.commit()

        # Access relationship
        assert len(sample_lease.asc842_schedules) == 1
        assert sample_lease.asc842_schedules[0].initial_rou_asset == Decimal("151000.00")
