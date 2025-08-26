# server/schemas/order.py
from sqlalchemy import Column, Integer, String, DateTime
from infrastructure.db import Base

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, nullable=True)
    phone = Column(String, nullable=True)
    address = Column(String, nullable=False)

    kit_id = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    note = Column(String, nullable=True)

    status = Column(String, nullable=False, default="pending")
    created_at = Column(DateTime, nullable=False)
