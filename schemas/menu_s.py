from pydantic import BaseModel ,Field ,ConfigDict
from typing import List , Optional

class Recipe(BaseModel):
    Raw_material : Optional[str] = Field(None,description="Raw material Name")
    Quantity : Optional[float] = Field(None,description="Quantity",gt=0.0)
    Unit : Optional[str] = Field(None,description="Unit")

class Menu_Input(BaseModel):

    Item_name : Optional[str] = Field(None,description="Item Name")
    Alte_name : Optional[str] = Field(None,description="Alternative Name")
    Price : Optional[float] = Field(None,description="Price",gt=0.0)
    Alte_price : Optional[float] = Field(None,description="Alternative Price",gt=0.0)
    Short_code : Optional[str] = Field(None,description="Short Code")
    Alte_short_code : Optional[str] = Field(None,description="Alternative Short Code")
    category: Optional[str] = Field(None,description="Item Category")
    Tax_rate : Optional[float] = Field(None,description="Tax Rate Amount ")
    Discount : Optional[float] = Field(None,description="Discount Amount")
    Hsn_code : Optional[int] = Field(None,description="Hsn Code")
    Recipes : Optional[List[Recipe]] = Field(None,description="Add Recipe")

class Menu_output(BaseModel):
    Item_name : str 
    Price : float 
    Short_code : str 
    Tax_rate : float 
    Discount : float 
    Hsn_code : int

    model_config = ConfigDict(from_attributes=True)

