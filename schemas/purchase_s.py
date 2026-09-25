
from pydantic import BaseModel ,Field, ConfigDict
from typing import Optional

class Purchase_Input(BaseModel):
    Supplier_name: Optional[str] = Field(None,description="Supplier Name")
    Date : Optional[str] = Field(None,description="Date")
    Invoice : Optional[str] = Field(None,description="Invoice")
    Raw_material : Optional[str] = Field(None,description="Raw Material")
    Quantity : Optional[float] = Field(description="Quantity",default=1.0)
    Rate : Optional[float] = Field(None,description="Rate" , gt=0)
    Discount : Optional[float] = Field(None,description="Discount")
    Taxable_amount :Optional[float] =Field(None,description= "Taxable value",gt=0)
    Tax_rate : Optional[float] = Field(None,description="Tax Rate")
    Other_charges : Optional[float] = Field(None,description="User ID")
    Total_amount : Optional[float] =Field(None,description="Total amount",gt=0)
    Amount_status : Optional[str] = Field(None,description="paid, unpaid and part paid")
    Created_at : Optional[str] = Field(None,description="current date")

class Purchase_output(BaseModel):
    Supplier_name: str = Field(description="Supplier Name")
    Date : str = Field(description="Date")
    Invoice : str = Field(description="Invoice")
    Total_amount : float =Field(description="Total amount")
    Amount_status : str = Field(description="paid, unpaid and part paid")

    model_config = ConfigDict(from_attributes= True)

