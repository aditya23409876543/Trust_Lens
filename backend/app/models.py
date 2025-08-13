from sqlalchemy import Column, Integer, Float, String, DateTime
from datetime import datetime
from .database import Base

class Feedback(Base):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    buyer_id = Column(Integer, nullable=False)
    product_id = Column(Integer, nullable=False)
    seller_id = Column(Integer, nullable=False)
    rating = Column(Float, nullable=False)
    comment = Column(String, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)
