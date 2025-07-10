from sqlalchemy import String, DECIMAL, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from Database.database import Base

class DirectDebitMovement(Base):
    __tablename__ = "money_movement"

    id: Mapped[str] = mapped_column(primary_key=True)
    source_id: Mapped[str] = mapped_column(String(20), ForeignKey("cobre_balance.id"))
    destination_id: Mapped[str] = mapped_column(String(50), ForeignKey("counterparty.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(18, 2))
    date_debit: Mapped[datetime] = mapped_column(DateTime)
    description: Mapped[str] = mapped_column(Text)
    reference_debit: Mapped[str] = mapped_column(String(100))
    checker_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    hora_fecha_exacta_movimiento : Mapped[datetime] = mapped_column(DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "amount": float(self.amount),
            "date_debit": self.date_debit.isoformat() if self.date_debit else None,
            "metadata": {
                "description": self.description,
                "reference_debit": self.reference_debit,
            },
            "checker_approval": self.checker_approval,
            "hora_fecha_exacta_movimiento ": self.hora_fecha_exacta_movimiento,
        }