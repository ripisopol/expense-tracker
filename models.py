from sqlalchemy import Column, Integer, String, Float, Date
from datetime import date as DateType
from database import Base

class Expense(Base):
    __tablename__ = "expenses"

    id          = Column(Integer, primary_key=True, index=True)
    amount      = Column(Float, nullable=False)
    category    = Column(String, nullable=False)
    description = Column(String, nullable=True)
    date        = Column(Date, nullable=False)