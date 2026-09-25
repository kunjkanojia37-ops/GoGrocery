from sqlalchemy import Column, Integer,String, Float,ForeignKey
from sqlalchemy.dialects.postgresql import JSONB
from database import Base

from sqlalchemy.orm import relationship

# table
class Menu_model(Base):
    __tablename__= "Menu"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,ForeignKey("Users.User_id"),nullable=True)
    Item_name = Column(String,nullable=True)
    Alte_name = Column(String)
    Price = Column(Float,nullable=True)
    Alte_price = Column(Float)
    Short_code = Column(String,nullable=True)
    Alte_short_code = Column(String)
    Category = Column(String, nullable=True)
    Tax_rate = Column(Integer)
    Discount = Column(Float)
    Hsn_code = Column(Integer,nullable=True)
    Recipe = Column(JSONB)

    user = relationship("Users_model", back_populates="menu_items")
    sales = relationship("Sale_model", back_populates="menu_item")
    stock_record = relationship("Stock_model", back_populates="menu_item", uselist=False) # One-to-One with Stock

