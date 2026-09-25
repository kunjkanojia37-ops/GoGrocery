from pydantic import BaseModel ,Field,EmailStr

class New_Users_Input(BaseModel):
    Name :str =Field(description="User Name")
    Email : EmailStr = Field(description="Email Id")
    Password : str = Field(description="Set Password")
    Confirm_Password : str = Field(description="Confirm Password")




class Old_User_Input(BaseModel):
    Email : EmailStr = Field(description="Email Id")
    Password : str = Field(description="Set Password")


class Old_User_Upgrade(BaseModel):
    Email : EmailStr = Field(description="Email Id")
    Password : str = Field(description="Set Password")

# from pydantic import BaseModel

# class ForgotPasswordInput(BaseModel):
#     Email: str

# class ResetPasswordInput(BaseModel):
#     Token: str
#     New_Password: str
#     Confirm_Password: str