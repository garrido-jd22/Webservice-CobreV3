from sqlalchemy import String, DECIMAL, TIMESTAMP, Boolean, ForeignKey, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from datetime import datetime
from Database.database import Base


class DirectDebitRegistration(Base):
    __tablename__ = "direct_debit_registration"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    debit_destination_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("debit_destination.debit_destination_id")
    )
    registration_description: Mapped[str] = mapped_column(String(255))
    created_at: Mapped[str] = mapped_column(TIMESTAMP)
    updated_at: Mapped[str] = mapped_column(TIMESTAMP)
    checker_approval: Mapped[bool] = mapped_column(Boolean)
    amount: Mapped[float] = mapped_column(DECIMAL(18, 2))
    external_id: Mapped[str] = mapped_column(String(50))
    source_id: Mapped[str] = mapped_column(String(50))

    status = relationship("DebitStatus", back_populates="registration", uselist=False)
    metadata = relationship(
        "DebitMetadata", back_populates="registration", uselist=False
    )

    def to_dict(self):
        return {
            "id": self.id,
            "destination_id": self.debit_destination_id,
            "registration_description": self.registration_description,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "checker_approval": self.checker_approval,
            "amount": float(self.amount),
            "external_id": self.external_id,
            "source_id": self.source_id,
            "status": self.status.to_dict() if self.status else None,
            "metadata": self.metadata.to_dict() if self.metadata else None,
        }


class DebitStatus(Base):
    __tablename__ = "debit_status"
    debit_status_id: Mapped[str] = mapped_column(
        ForeignKey("direct_debit_registration.id"), primary_key=True
    )
    state: Mapped[str] = mapped_column(String(50))
    code: Mapped[str] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(Text)
    registration = relationship("DirectDebitRegistration", back_populates="status")

    def to_dict(self):
        return {"state": self.state, "code": self.code, "description": self.description}


class DebitMetadata(Base):
    __tablename__ = "debit_metadata"
    debit_registration_id: Mapped[str] = mapped_column(
        ForeignKey("direct_debit_registration.id"), primary_key=True
    )
    description: Mapped[str] = mapped_column(Text)
    reference: Mapped[str] = mapped_column(String(50))
    registration = relationship("DirectDebitRegistration", back_populates="metadata")

    def to_dict(self):
        return {"description": self.description, "reference": self.reference}
