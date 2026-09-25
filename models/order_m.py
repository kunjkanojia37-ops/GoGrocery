from sqlalchemy import Column, Integer,String, Float,DateTime
from database import Base


# table

class Order_model(Base):
    __tablename__= "Order"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,nullable=True)
    Order_id= Column(Integer)
    Customer_name= Column(String)
    Price = Column(Float)
    Slot = Column(Float)
    Created_at = Column(DateTime)
    Status = Column(String)
    Action = Column(String)
    Items = Column(String)
    Quantity = Column(Float)
    Payment_mode = Column(String)
    