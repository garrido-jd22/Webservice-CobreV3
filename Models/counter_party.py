from sqlalchemy import ForeignKey, String
from Database.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from datetime import datetime


class CounterParty(Base):
    __tablename__ = "counterparty"

    id: Mapped[str] = mapped_column(primary_key=True)
    fk_data_load: Mapped[str] = mapped_column(String(20), ForeignKey("data_load.id"))
    geo: Mapped[str]
    type: Mapped[str]
    alias: Mapped[str]
    beneficiary_institution: Mapped[str]
    account_number: Mapped[int]
    reference_debit: Mapped[str]
    amount: Mapped[int]
    counterparty_fullname: Mapped[str]
    counterparty_id_type: Mapped[str]
    counterparty_id_number: Mapped[int]
    counterparty_phone: Mapped[str]
    counterparty_email: Mapped[str]
    fecha_reg: Mapped[datetime] = mapped_column(default=datetime.now())
    date_debit: Mapped[datetime] 

    def to_dict(self):
        return {
            "id": self.id,
            "geo": self.geo,
            "type": self.type,
            "alias": self.alias,
            "beneficiary_institution": self.beneficiary_institution,
            "account_number": self.account_number,
            "amount": self.amount,
            "reference_debit": self.reference_debit,
            "counterparty_fullname": self.counterparty_fullname,
            "counterparty_id_type": self.counterparty_id_type,
            "counterparty_id_number": self.counterparty_id_number,
            "counterparty_phone": self.counterparty_phone,
            "counterparty_email": self.counterparty_email,
            "fecha_reg": self.fecha_reg.isoformat() if self.fecha_reg else None,
            "date_debit": self.date_debit.isoformat() if self.date_debit else None,
        }
