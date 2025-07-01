from sqlalchemy import String, DECIMAL, TIMESTAMP, Boolean, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from Database.database import Base


class MoneyMovement(Base):
    __tablename__ = "money_movements"

    id: Mapped[str] = mapped_column(String(20), primary_key=True)
    batch_id: Mapped[str] = mapped_column(String(30))
    external_id: Mapped[str] = mapped_column(String(30))
    typee: Mapped[str] = mapped_column(String(20), default="spei")
    geo: Mapped[str] = mapped_column(String(10))
    source_id: Mapped[str] = mapped_column(String(30))
    destination_id: Mapped[str] = mapped_column(String(30))
    currency: Mapped[str] = mapped_column(String(10), default="mxn")
    amount: Mapped[float] = mapped_column(DECIMAL(18, 2))
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(TIMESTAMP, default=datetime.utcnow)
    checker_approval: Mapped[bool] = mapped_column(Boolean)

    status: Mapped["MoneyMovementStatus"] = relationship(
        back_populates="movement", uselist=False
    )
    metadata: Mapped["MoneyMovementMetadata"] = relationship(
        back_populates="movement", uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "batch_id": self.batch_id,
            "external_id": self.external_id,
            "type": self.typee,
            "geo": self.geo,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "currency": self.currency,
            "amount": float(self.amount),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "checker_approval": self.checker_approval,
            "status": self.status.to_dict() if self.status else None,
            "metadata": self.metadata.to_dict() if self.metadata else None,
        }


class MoneyMovementStatus(Base):
    __tablename__ = "money_movement_status"

    movement_id: Mapped[str] = mapped_column(
        ForeignKey("money_movements.id"), primary_key=True
    )
    state: Mapped[str] = mapped_column(String(20))
    code: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)

    movement: Mapped["MoneyMovement"] = relationship(back_populates="status")

    def to_dict(self):
        return {"state": self.state, "code": self.code, "description": self.description}


class MoneyMovementMetadata(Base):
    __tablename__ = "money_movement_metadata"

    movement_id: Mapped[str] = mapped_column(
        ForeignKey("money_movements.id"), primary_key=True
    )
    description: Mapped[str] = mapped_column(Text)
    tracking_key: Mapped[str] = mapped_column(String(100))
    reference: Mapped[str] = mapped_column(String(50))
    cep_url: Mapped[str] = mapped_column(Text)

    movement: Mapped["MoneyMovement"] = relationship(back_populates="metadata")

    def to_dict(self):
        return {
            "description": self.description,
            "tracking_key": self.tracking_key,
            "reference": self.reference,
            "cep_url": self.cep_url,
        }
