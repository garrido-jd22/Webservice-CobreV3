from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped
from datetime import datetime
from Database.database import Base


class DirectDebitRegistration(Base):
    __tablename__ = "direct_debit_registration"

    id: Mapped[str] = mapped_column(String(50), primary_key=True)
    source_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("cobre_balance.id")
    )
    destination_id: Mapped[str] = mapped_column(
        String(50), ForeignKey("counterparty.id")
    )
    registration_description: Mapped[str] = mapped_column(String(255))
    state_local: Mapped[str]
    state: Mapped[str]
    code: Mapped[str]
    description: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "source_id": self.source_id,
            "destination_id": self.destination_id,
            "registration_description": self.registration_description,
            "state_local": self.state_local,
            "state": self.state,
            "code": self.code,
            "description": self.description,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }
