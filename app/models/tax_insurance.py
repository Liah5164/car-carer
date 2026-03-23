from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Float, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class TaxInsuranceRecord(Base):
    __tablename__ = "tax_insurance_records"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    record_type: Mapped[str] = mapped_column(String(50), nullable=False)  # "insurance", "vignette", "carbon_tax", "registration", "parking", "toll_tag", "other"
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    provider: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    cost: Mapped[float] = mapped_column(Float, nullable=False)
    next_renewal_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    renewal_frequency: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)  # "monthly", "annual", "biennial", "one_time"
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    document_id: Mapped[Optional[int]] = mapped_column(ForeignKey("documents.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    vehicle = relationship("Vehicle", back_populates="tax_insurance_records")
