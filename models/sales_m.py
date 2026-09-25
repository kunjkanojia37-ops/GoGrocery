from sqlalchemy import Column, Integer,String, Float,ForeignKey
from database import Base
from sqlalchemy.orm import relationship



# table
class Sale_model(Base):
    __tablename__= "Sales"

    Id = Column(String,primary_key=True,index=True)
    menu_item_id = Column(String, ForeignKey("Menu.Id"), nullable=False)
    User_id = Column(String,ForeignKey("Users.User_id"),nullable=True)
    Invoice = Column(Integer)
    Order_type = Column(String)
    Customer_name = Column(String)
    Phone_number = Column(Integer)
    Address = Column(String)
    Gst_number = Column(String)
    Item_name = Column(String)
    Hsn_code = Column(Integer)  
    Quantity= Column(Float)
    Price = Column(Float)
    Tax_type = Column(String)
    Tax_Apply = Column(String)
    Tax_rate = Column(Integer)
    Tax_amount =Column(Float)
    Discount = Column(Float)
    Total_amount = Column(Integer)
    Payment_mode = Column(String)
    
    user = relationship("Users_model", back_populates="sales")
    menu_item = relationship("Menu_model", back_populates="sales")