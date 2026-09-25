from sqlalchemy import Column, BigInteger,String, Float,ForeignKey
from database import Base
from sqlalchemy.orm import relationship


# table
class Supplier_model(Base):
    __tablename__= "Supplier"
    Id = Column(String,primary_key=True,index=True)
    User_id = Column(String,ForeignKey("Users.User_id"),nullable=True)
    Supplier = Column(String)
    Gst_number= Column(String)
    Address = Column(String)
    phone_number = Column(BigInteger)
    email_id = Column(String)
    Pan_number = Column(String)
    Paid = Column(Float)
    Unpaid = Column(Float)
    Tan_number = Column(String)
    Bank_Account_Number = Column(String)
    IFSC_code = Column(String)
    UPI_ID = Column(String)

        
    # Link back to User, link forward to Purchases
    user = relationship("Users_model", back_populates="suppliers")
    purchases = relationship("Purchase_model", back_populates="supplier")