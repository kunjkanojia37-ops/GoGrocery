from pydantic import BaseModel, Field, ConfigDict,EmailStr
from typing import Optional

# ... Keep your existing Suppliers_Input and Supplier_output as they are ...

# ADD THIS: Dedicated Schema for Partial PATCH Updates
class Suppliers_Input(BaseModel):
    Supplier : Optional[str] = Field(description="Supplier Name", default=None)
    Gst_number: Optional[str] = Field(description="Gst Number", default=None, max_length=15)
    Address : Optional[str] = Field(description="Address", default=None)
    phone_number : Optional[int] = Field(description="Phone Number", default=None)
    email_id : Optional[EmailStr] = Field(description="Email Id", default=None)
    Pan_number : Optional[str] = Field(description="Pan Number", default=None, max_length=10)
    Paid : Optional[float] = Field(description="Paid Amount", default=None)
    Unpaid : Optional[float] = Field(description="Unpaid Amount", default=None)
    Tan_number : Optional[str] = Field(description="Tan Number", default=None)
    Bank_Account_Number  : Optional[str] = Field(description="Bank Account Number", default=None, max_length=17)
    IFSC_code  : Optional[str] = Field(description="IFSC Code", default=None, max_length=10)
    UPI_ID  : Optional[str] = Field(description="UPI ID", default=None, max_length=15)

class Supplier_output(BaseModel):
    Supplier : str
    Gst_number: str
    Address : str
    phone_number :int
    UPI_ID  : str

    model_config =ConfigDict(from_attributes=True)



