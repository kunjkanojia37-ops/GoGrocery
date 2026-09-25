from sqlalchemy import Column, Integer,String, Float,DateTime,ForeignKey

from database import Base
from sqlalchemy.orm import relationship


# table
class Purchase_model(Base):
    __tablename__= "Purchase"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,ForeignKey("Users.User_id"),nullable=True)
    supplier_id = Column(String, ForeignKey("Supplier.Id"), nullable=False)
    Supplier_name= Column(String)
    Date = Column(DateTime)
    Invoice = Column(String)
    Raw_material = Column(String)
    Quantity = Column(Float)
    Rate = Column(Float)
    Discount = Column(Float)
    Taxable_amount = Column(Float)
    Tax_rate = Column(Integer)
    Other_charges = Column(Float)
    Total_amount =Column(Float)
    Amount_status = Column(String)
    Created_at = Column(DateTime)
    user = relationship("Users_model", back_populates="purchases")
    supplier = relationship("Supplier_model", back_populates="purchases")
