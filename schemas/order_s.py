from pydantic import BaseModel ,Field ,ConfigDict



class Order_Input(BaseModel):
    Customer_name: str = Field(description="Customer Name")
    Price : str = Field(description="Price")
    Slot : str = Field(description="Slot")
    Created_at: str = Field(description="created at")
    Status : str = Field(description="Order Status(pending , cancel , done)")
    Action : str = Field(description="Order action (cancel or ready)")
    Items : str = Field(description="List of Items")
    Quantity : str = Field(description="Quantity of Item")
    Payment_mode :str = Field(description="like cash, upi, part and card")

class Order_output(BaseModel):
       Order_id: str
       Customer_name: str 
       Price : str
       Slot : str 
       Created_at: str 
       Status : str 
       Action : str 
       Items : str 
       Quantity : str
       Payment_mode :str 

       model_config =ConfigDict(from_attributes=True)