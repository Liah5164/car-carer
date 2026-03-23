from datetime import date, datetime
from typing import Optional

from sqlalchemy import String, Integer, Date, DateTime, Text, Boolean, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database import Base


class MaintenanceReminder(Base):
    __tablename__ = "maintenance_reminders"

    id: Mapped[int] = mapped_column(primary_key=True)
    vehicle_id: Mapped[int] = mapped_column(ForeignKey("vehicles.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    trigger_mode: Mapped[str] = mapped_column(String(20), nullable=False)  # "km_only", "date_only", "km_or_date"
    km_interval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    months_interval: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_performed_km: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    last_performed_date: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=True)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[Optional[datetime]] = mapped_column(DateTime, onupdate=func.now(), nullable=True)

    vehicle = relationship("Vehicle", back_populates="reminders")
