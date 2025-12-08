from pydantic import BaseModel, Field
from datetime import datetime
from decimal import Decimal
from typing import Optional, Dict


# Journal Entries Schemas
class JournalEntryBase(BaseModel):
    contract_id: str = Field(..., description="ID of the associated contract/lease")
    entry_date: datetime = Field(..., description="Date of the journal entry")
    description: str = Field(..., description="Description of the journal entry")
    debit_account: str = Field(..., description="Debit account name")
    credit_account: str = Field(..., description="Credit account name")
    amount: Decimal = Field(..., gt=0, description="Amount of the journal entry")
    reference: Optional[str] = Field(None, description="Optional reference number")


class JournalEntryCreate(JournalEntryBase):
    pass


class JournalEntryUpdate(BaseModel):
    contract_id: Optional[str] = None
    entry_date: Optional[datetime] = None
    description: Optional[str] = None
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None
    amount: Optional[Decimal] = None
    reference: Optional[str] = None


class JournalEntryResponse(JournalEntryBase):
    id: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Journal Entry Setups Schemas
class JournalEntrySetupBase(BaseModel):
    name: str = Field(..., description="Name of the journal entry setup")
    entry_type: str = Field(..., description="Type of journal entry")
    trigger_event: str = Field(..., description="Event that triggers this entry")
    debit_account: str = Field(..., description="Debit account name")
    credit_account: str = Field(..., description="Credit account name")
    amount_column: str = Field(..., description="Column name for amount calculation")
    period_reference: str = Field(default="n", description="Period reference (n, n+1, etc.)")
    is_active: bool = Field(default=True, description="Whether this setup is active")
    description: Optional[str] = Field(None, description="Optional description")


class JournalEntrySetupCreate(JournalEntrySetupBase):
    pass


class JournalEntrySetupUpdate(BaseModel):
    name: Optional[str] = None
    entry_type: Optional[str] = None
    trigger_event: Optional[str] = None
    debit_account: Optional[str] = None
    credit_account: Optional[str] = None
    amount_column: Optional[str] = None
    period_reference: Optional[str] = None
    is_active: Optional[bool] = None
    description: Optional[str] = None


class JournalEntrySetupResponse(JournalEntrySetupBase):
    id: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Payments Schemas
class PaymentBase(BaseModel):
    contract_id: str = Field(..., description="ID of the associated contract/lease")
    amount: Decimal = Field(..., gt=0, description="Payment amount")
    due_date: datetime = Field(..., description="Payment due date")
    status: str = Field(default="Scheduled", description="Payment status")
    paid_date: Optional[datetime] = Field(None, description="Date payment was made")


class PaymentCreate(PaymentBase):
    pass


class PaymentUpdate(BaseModel):
    contract_id: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    status: Optional[str] = None
    paid_date: Optional[datetime] = None


class PaymentResponse(PaymentBase):
    id: str
    created_at: Optional[datetime]

    class Config:
        from_attributes = True


# Documents Schemas
class DocumentBase(BaseModel):
    filename: str = Field(..., description="Stored filename")
    original_name: str = Field(..., description="Original filename")
    mime_type: str = Field(..., description="MIME type of the document")
    size: int = Field(..., description="File size in bytes")
    upload_path: str = Field(..., description="Path where file is stored")
    processing_status: str = Field(default="pending", description="Processing status")
    extracted_data: Optional[Dict] = Field(None, description="Extracted data from document")


class DocumentCreate(DocumentBase):
    pass


class DocumentUpdate(BaseModel):
    filename: Optional[str] = None
    original_name: Optional[str] = None
    mime_type: Optional[str] = None
    size: Optional[int] = None
    upload_path: Optional[str] = None
    processing_status: Optional[str] = None
    extracted_data: Optional[Dict] = None


class DocumentResponse(DocumentBase):
    id: str
    uploaded_at: Optional[datetime]

    class Config:
        from_attributes = True
