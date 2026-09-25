from sqlalchemy import Column, Integer,String, Float,ForeignKey
from database import Base
from sqlalchemy.orm import relationship


# table
class Stock_model(Base):
    __tablename__= "Stock"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,ForeignKey("Users.User_id"),nullable=True)
    Menu_id = Column(String, ForeignKey("Menu.Id"))
    Supplier = Column(String)
    Raw_material = Column(String)
    Quantity = Column(Float)
    Status = Column(String)
    Adjust = Column(Float)
    user = relationship("Users_model", back_populates="stocks")
    menu_item = relationship("Menu_model", back_populates="stock_record")
    