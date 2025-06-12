from Database.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from datetime import datetime


class CounterParty(Base):
    __tablename__ = "counter_party"

    id: Mapped[int] = mapped_column(primary_key=True)
    geo: Mapped[str]
    tipe: Mapped[str]
    alias: Mapped[str]
    account_number: Mapped[str]
    counterparty_full_name: Mapped[str]
    counterparty_id_type: Mapped[str]
    counterparty_id_number: Mapped[str]
    fecha_reg: Mapped[datetime] = mapped_column(default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "geo": self.geo,
            "tipe": self.tipe,
            "alias": self.alias,
            "account_number": self.account_number,
            "counterparty_full_name": self.counterparty_full_name,
            "counterparty_id_type": self.counterparty_id_type,
            "counterparty_id_number": self.counterparty_id_number,
            "fecha_reg": self.fecha_reg.isoformat() if self.fecha_reg else None,
        }
