from sqlalchemy import String, DECIMAL, DateTime, Boolean, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from Database.database import Base

class DirectDebitMovement(Base):
    __tablename__ = "direct_debit_movement"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    source_id: Mapped[str] = mapped_column(String(50), ForeignKey("cobre_balance.id"))
    destination_id: Mapped[str] = mapped_column(String(50), ForeignKey("counterparty.id"))
    amount: Mapped[float] = mapped_column(DECIMAL(18, 2))
    date_debit: Mapped[datetime] = mapped_column(DateTime)
    metadata_description: Mapped[str] = mapped_column(Text)
    metadata_reference: Mapped[str] = mapped_column(String(100))
    checker_approval: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "amount": float(self.amount),
            "date_debit": self.date_debit.isoformat() if self.date_debit else None,
            "metadata": {
                "description": self.metadata_description,
                "reference": self.metadata_reference,
            },
            "checker_approval": self.checker_approval,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }