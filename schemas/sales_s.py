from pydantic import BaseModel ,ConfigDict, Field
from typing import Optional

class Sales_Input(BaseModel):
    Invoice : Optional[str] = Field(None,description="Invoice Number")
    Order_type : Optional[str] = Field(None,description="Pick Up or Delivery")
    Customer_name : Optional[str] =Field(None,description="Customer Name")
    Phone_number : Optional[int] =Field(None,description="Phone Number")
    Address : Optional[str] =Field(None,description="Address")
    Gst_number  : Optional[str] = Field(None,description="Gst Number")
    Item_name : Optional[str] = Field(None,description="Item Name")
    Hsn_code : Optional[str] = Field(None,description="Hsn Code")
    Quantity: Optional[str] = Field(description="Quantity",default=1.0)
    Price : Optional[str] = Field(None,description="Price",gt=0)
    Tax_type : Optional[str] = Field(None,description="Tax Type (CGST/SGST , IGST)")
    Tax_Apply : Optional[str] = Field(None,description="Tax Apply (Backword , Forward)")
    Tax_rate : Optional[float] = Field(None,description="Tax Rate")
    Tax_amount : Optional[float] = Field(None,description="Tax Amount",gt=0)
    Discount : Optional[str] = Field(None,description="Discount")
    Total_amount : Optional[float] = Field(None,description="Total Amount",gt=0)
    Payment_mode : Optional[str] = Field(None,description="cash , Card , Part  and UPI")

class Sales_Output(BaseModel):
    Invoice : str
    Customer_name : str
    Order_type : str
    Total_amount: float

    model_config = ConfigDict(from_attributes=True)
