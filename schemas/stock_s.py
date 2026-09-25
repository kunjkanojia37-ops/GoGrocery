from pydantic import BaseModel ,ConfigDict,Field
from typing import Optional

class Stocks_Input(BaseModel):
    
    
    Supplier : str = Field(description="Supplier Name")
    Raw_material: str = Field(description="Raw Materials")
    Quantity : str = Field(description="Quantity")
    Status: str = Field(description="Stock Level")
    Adjust : str = Field(description="New Value")

class Stock_output(BaseModel):
       Supplier : str
       Raw_material: str
       Quantity : str 
       Status: str 
       Adjust : str 

       model_config = ConfigDict(from_attributes=True)
       