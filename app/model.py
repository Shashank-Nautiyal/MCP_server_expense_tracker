from app.database import Base
from sqlalchemy import Column ,Integer , String,Date ,Numeric


class Expense(Base):
    __tablename__="expenses"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(String(255), nullable=False, index=True)
    date = Column(Date, nullable=False)
    amount= Column(Numeric(10,2), nullable=False)
    category = Column(String(100), nullable=False)
    subcategory = Column(String(100), default="")
    note = Column(String(500), default="")