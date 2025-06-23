from Database.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from datetime import datetime


class CounterParty(Base):
    __tablename__ = "counter_party"

    id: Mapped[int] = mapped_column(primary_key=True)
    geo: Mapped[str]
    type: Mapped[str]
    alias: Mapped[str]
    beneficiary_institution: Mapped[int]
    account_number: Mapped[str]
    counterparty_fullname: Mapped[str]
    counterparty_id_type: Mapped[str]
    counterparty_id_number: Mapped[str]
    counterparty_phone: Mapped[str]
    counterparty_email: Mapped[str]
    registered_account: Mapped[bool]
    fecha_reg: Mapped[datetime] = mapped_column(default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "geo": self.geo,
            "type": self.type,
            "alias": self.alias,
            "account_number": self.account_number,
            "counterparty_fullname": self.counterparty_fullname,
            "counterparty_id_type": self.counterparty_id_type,
            "counterparty_id_number": self.counterparty_id_number,
            "counterparty_phone": self.counterparty_phone,
            "counterparty_email": self.counterparty_email,
            "registered_account": self.registered_account,
            "fecha_reg": self.fecha_reg.isoformat() if self.fecha_reg else None,
        }
