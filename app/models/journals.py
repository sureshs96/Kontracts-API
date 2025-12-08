from typing import Optional
import datetime
import decimal

from sqlalchemy import Boolean, DateTime, Integer, Numeric, PrimaryKeyConstraint, String, Text, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class JournalEntries(Base):
    """Journal entries for accounting transactions"""
    __tablename__ = 'journal_entries'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='journal_entries_pkey'),
        {'schema': 'kontracts'}
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text('gen_random_uuid()'))
    contract_id: Mapped[str] = mapped_column(String)
    entry_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(Text)
    debit_account: Mapped[str] = mapped_column(Text)
    credit_account: Mapped[str] = mapped_column(Text)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2))
    reference: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))


class JournalEntrySetups(Base):
    """Automated journal entry setup configurations"""
    __tablename__ = 'journal_entry_setups'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='journal_entry_setups_pkey'),
        {'schema': 'kontracts'}
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text('gen_random_uuid()'))
    name: Mapped[str] = mapped_column(Text)
    entry_type: Mapped[str] = mapped_column(Text)
    trigger_event: Mapped[str] = mapped_column(Text)
    debit_account: Mapped[str] = mapped_column(Text)
    credit_account: Mapped[str] = mapped_column(Text)
    amount_column: Mapped[str] = mapped_column(Text)
    period_reference: Mapped[str] = mapped_column(Text, server_default=text("'n'::text"))
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text('true'))
    description: Mapped[Optional[str]] = mapped_column(Text)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))


class Payments(Base):
    """Payment tracking for contracts and leases"""
    __tablename__ = 'payments'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='payments_pkey'),
        {'schema': 'kontracts'}
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text('gen_random_uuid()'))
    contract_id: Mapped[str] = mapped_column(String)
    amount: Mapped[decimal.Decimal] = mapped_column(Numeric(12, 2))
    due_date: Mapped[datetime.datetime] = mapped_column(DateTime)
    status: Mapped[str] = mapped_column(Text, server_default=text("'Scheduled'::text"))
    paid_date: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime)
    created_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))


class Documents(Base):
    """Document storage and processing tracking"""
    __tablename__ = 'documents'
    __table_args__ = (
        PrimaryKeyConstraint('id', name='documents_pkey'),
        {'schema': 'kontracts'}
    )

    id: Mapped[str] = mapped_column(String, primary_key=True, server_default=text('gen_random_uuid()'))
    filename: Mapped[str] = mapped_column(Text)
    original_name: Mapped[str] = mapped_column(Text)
    mime_type: Mapped[str] = mapped_column(Text)
    size: Mapped[int] = mapped_column(Integer)
    upload_path: Mapped[str] = mapped_column(Text)
    processing_status: Mapped[str] = mapped_column(Text, server_default=text("'pending'::text"))
    extracted_data: Mapped[Optional[dict]] = mapped_column(JSONB)
    uploaded_at: Mapped[Optional[datetime.datetime]] = mapped_column(DateTime, server_default=text('now()'))


