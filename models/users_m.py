from sqlalchemy import Column, Integer,String, Float,DateTime
from database import Base
from sqlalchemy.orm import relationship



# table
class Users_model(Base):
    __tablename__= "Users"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,nullable=True,unique=True)
    Name = Column(String)
    Email = Column(String)
    Password = Column(String)
    # Reset_Token = Column(String, nullable=True, unique=True)
    # Token_Expiry = Column(DateTime, nullable=True)

        # Relationships: One user has many suppliers, menu items, sales, etc.
    suppliers = relationship("Supplier_model", back_populates="user")
    menu_items = relationship("Menu_model", back_populates="user")
    purchases = relationship("Purchase_model", back_populates="user")
    sales = relationship("Sale_model", back_populates="user")
    stocks = relationship("Stock_model", back_populates="user")