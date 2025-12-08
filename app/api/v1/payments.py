from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc
from datetime import datetime

from app.database import get_db
from app.models.journals import Payments
from app.schemas.journals import (
    PaymentCreate,
    PaymentUpdate,
    PaymentResponse,
)
from app.auth import get_current_user

router = APIRouter(prefix="/payments", tags=["payments"], dependencies=[Depends(get_current_user)])


# ==================== PAYMENT ENDPOINTS ====================

@router.post("/", response_model=PaymentResponse, status_code=201)
def create_payment(
    payment: PaymentCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new payment record.

    - **contract_id**: ID of the associated contract/lease
    - **amount**: Payment amount
    - **due_date**: Payment due date
    - **status**: Payment status (default: Scheduled)
    - **paid_date**: Date payment was made (optional)
    """
    db_payment = Payments(**payment.model_dump())
    db.add(db_payment)
    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/", response_model=List[PaymentResponse])
def list_payments(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    contract_id: Optional[str] = Query(None, description="Filter by contract ID"),
    status: Optional[str] = Query(None, description="Filter by payment status"),
    sort_by: str = Query("due_date", description="Field to sort by"),
    sort_order: str = Query("asc", description="Sort order (asc/desc)"),
    db: Session = Depends(get_db)
):
    """
    Retrieve a list of payments with optional filters.

    Supports filtering by:
    - contract_id
    - status

    Supports sorting by any field (default: due_date ascending)
    """
    query = db.query(Payments)

    # Apply filters
    if contract_id:
        query = query.filter(Payments.contract_id == contract_id)
    if status:
        query = query.filter(Payments.status == status)

    # Apply sorting
    if hasattr(Payments, sort_by):
        order_column = getattr(Payments, sort_by)
        if sort_order.lower() == "desc":
            query = query.order_by(desc(order_column))
        else:
            query = query.order_by(asc(order_column))

    # Apply pagination
    payments = query.offset(skip).limit(limit).all()
    return payments


@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Retrieve a specific payment by ID.
    """
    payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    return payment


@router.put("/{payment_id}", response_model=PaymentResponse)
def update_payment(
    payment_id: str,
    payment_update: PaymentUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing payment.

    Only provided fields will be updated.
    """
    db_payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    # Update only provided fields
    update_data = payment_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_payment, field, value)

    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.delete("/{payment_id}", status_code=204)
def delete_payment(
    payment_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a payment.
    """
    db_payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    db.delete(db_payment)
    db.commit()
    return None


@router.post("/{payment_id}/mark-paid", response_model=PaymentResponse)
def mark_payment_as_paid(
    payment_id: str,
    paid_date: Optional[datetime] = None,
    db: Session = Depends(get_db)
):
    """
    Mark a payment as paid.

    - **paid_date**: Date payment was made (defaults to current date/time if not provided)
    """
    db_payment = db.query(Payments).filter(Payments.id == payment_id).first()

    if not db_payment:
        raise HTTPException(status_code=404, detail="Payment not found")

    db_payment.status = "Paid"
    db_payment.paid_date = paid_date or datetime.now()

    db.commit()
    db.refresh(db_payment)
    return db_payment


@router.get("/contract/{contract_id}/summary", response_model=dict)
def get_contract_payment_summary(
    contract_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a summary of all payments for a specific contract.

    Returns:
    - total_amount: Sum of all payment amounts
    - total_paid: Sum of paid payments
    - total_scheduled: Sum of scheduled payments
    - total_overdue: Sum of overdue payments
    - payment_count: Total number of payments
    """
    payments = db.query(Payments).filter(Payments.contract_id == contract_id).all()

    if not payments:
        return {
            "contract_id": contract_id,
            "total_amount": 0,
            "total_paid": 0,
            "total_scheduled": 0,
            "total_overdue": 0,
            "payment_count": 0
        }

    total_amount = sum(float(p.amount) for p in payments)
    total_paid = sum(float(p.amount) for p in payments if p.status == "Paid")
    total_scheduled = sum(float(p.amount) for p in payments if p.status == "Scheduled")

    # Calculate overdue (scheduled payments past due date)
    now = datetime.now()
    total_overdue = sum(
        float(p.amount) for p in payments
        if p.status == "Scheduled" and p.due_date < now
    )

    return {
        "contract_id": contract_id,
        "total_amount": total_amount,
        "total_paid": total_paid,
        "total_scheduled": total_scheduled,
        "total_overdue": total_overdue,
        "payment_count": len(payments)
    }
