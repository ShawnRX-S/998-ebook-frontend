"""
Order status service for the privacy-preserving OT ebook flow.

Purpose:
- After the frontend starts or completes a purchase/payment process,
  create an order_status record in the database.

Privacy rule:
- Do NOT store book_id.
- Do NOT store choice_index.
- Do NOT store selected_book_index.
- Do NOT store filename/title of the selected book.

This table only records order/payment state at user level.
The selected ebook remains hidden inside the OT flow.
"""

from datetime import datetime
from uuid import uuid4
from typing import Optional

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from database import Base


ALLOWED_PAYMENT_STATUSES = {"pending", "paid", "failed", "cancelled", "refunded"}


class OrderStatus(Base):
    """
    Database table: order_status

    Required columns:
    - order_id
    - user_id
    - payment_status
    - created_at

    Important:
    This table must not contain book_id or choice_index.
    """

    __tablename__ = "order_status"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(String(64), unique=True, nullable=False, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    payment_status = Column(String(32), nullable=False, default="pending", index=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)


def generate_order_id() -> str:
    """
    Generate a random order_id.

    The order_id must not be derived from book_id, choice_index,
    selected book index, filename, or title.
    """

    return f"ORD-{uuid4().hex[:16].upper()}"


def validate_payment_status(payment_status: str) -> None:
    """Validate payment_status before saving it to the database."""

    if payment_status not in ALLOWED_PAYMENT_STATUSES:
        allowed = ", ".join(sorted(ALLOWED_PAYMENT_STATUSES))
        raise ValueError(f"Invalid payment_status: {payment_status}. Allowed values: {allowed}")


def serialize_order_status(order: OrderStatus) -> dict:
    """Convert an OrderStatus SQLAlchemy object into a safe API-friendly dict."""

    return {
        "order_id": order.order_id,
        "user_id": order.user_id,
        "payment_status": order.payment_status,
        "created_at": order.created_at.isoformat(),
    }


def create_order_status(
    db: Session,
    user_id: int,
    payment_status: str = "pending",
) -> dict:
    """
    Create one order_status record.

    Use this after the frontend starts or completes the purchase/payment flow.

    Args:
        db: SQLAlchemy database session.
        user_id: The user who created the order.
        payment_status: One of pending, paid, failed, cancelled, refunded.

    Returns:
        A dict containing order_id, user_id, payment_status, created_at.

    Privacy note:
        Do not pass book_id, choice_index, or selected_book_index here.
    """

    if user_id <= 0:
        raise ValueError("user_id must be a positive integer")

    validate_payment_status(payment_status)

    order = OrderStatus(
        order_id=generate_order_id(),
        user_id=user_id,
        payment_status=payment_status,
        created_at=datetime.utcnow(),
    )

    db.add(order)
    db.commit()
    db.refresh(order)

    return serialize_order_status(order)


def get_order_status_by_order_id(db: Session, order_id: str) -> Optional[dict]:
    """
    Get one order_status record by order_id.

    Returns None if the order_id does not exist.
    """

    order = db.query(OrderStatus).filter(OrderStatus.order_id == order_id).first()

    if order is None:
        return None

    return serialize_order_status(order)


def update_payment_status(db: Session, order_id: str, payment_status: str) -> dict:
    """
    Update payment_status for an existing order_status record.

    Example transitions:
    - pending -> paid
    - pending -> failed
    - paid -> refunded
    """

    validate_payment_status(payment_status)

    order = db.query(OrderStatus).filter(OrderStatus.order_id == order_id).first()

    if order is None:
        raise ValueError("order_id not found")

    order.payment_status = payment_status
    db.commit()
    db.refresh(order)

    return serialize_order_status(order)
