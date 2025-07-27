from sqlalchemy import ForeignKey
from Database.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from datetime import datetime


class CobreBalance(Base):
    __tablename__ = "cobre_balance"

    id: Mapped[int] = mapped_column(primary_key=True)
    provider_id: Mapped[str]
    provider_name: Mapped[str]
    alias: Mapped[str]
    connectivity: Mapped[str]
    account_number: Mapped[str]
    account_type: Mapped[str]
    obtained_balance: Mapped[float]
    obtained_balance_at: Mapped[datetime]
    primary_account: Mapped[str]
    geo: Mapped[str]
    currency: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())
    updated_at: Mapped[datetime] = mapped_column(default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "provider_id": self.provider_id,
            "provider_name": self.provider_name,
            "alias": self.alias,
            "connectivity": self.connectivity,
            "account_number": self.account_number,
            "account_type": self.account_type,
            "obtained_balance": self.obtained_balance,
            "obtained_balance_at": self.obtained_balance_at,
            "primary_account": self.primary_account,
            "geo": self.geo,
            "currency": self.currency,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class CobreAvailableServices(Base):
    __tablename__ = "cobre_available_services"

    id: Mapped[int] = mapped_column(primary_key=True)
    fk_cobre_balance: Mapped[str] = mapped_column(
        ForeignKey("cobre_balance.id"), primary_key=True
    )
    service_name: Mapped[str]

    def to_dict(self):
        return {
            "id": self.id,
            "fk_cobre_balance": self.fk_cobre_balance,
            "service_name": self.service_name,
        }
