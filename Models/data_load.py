from Database.database import Base
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import Mapped
from datetime import datetime


class DataLoad(Base):
    __tablename__ = "data_load"

    id: Mapped[str] = mapped_column(primary_key=True)
    state: Mapped[str]
    created_at: Mapped[datetime] = mapped_column(default=datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "state": self.state,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
