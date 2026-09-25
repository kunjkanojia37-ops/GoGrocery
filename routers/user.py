from fastapi import APIRouter,Depends,Query,HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import or_
from database import get_db
from schemas.users_s import Old_User_Upgrade,New_Users_Input,Old_User_Input
from models.users_m import Users_model
from generator.user_id import generate_unique_id
from auth import verify_token
from auth import create_token
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()

user_router = APIRouter(prefix="/User",tags=["New User"])

@user_router.post("/New_sign_in",status_code=201)
def new_user(request:New_Users_Input,db:Session = Depends(get_db)):
 
 if request.Password != request.Confirm_Password:
    raise HTTPException(
        status_code=400,
        detail="Password and Confirm Password do not match"
    )
 hashed_password = password_hash.hash(
    request.Password
)
 auto_user_id = generate_unique_id(db,Users_model,prefix="User")
 auto_Id = generate_unique_id(db,Users_model,prefix="ID")
 
 new_user_info = Users_model(
    Id =auto_Id  ,
    User_id = auto_user_id,
    Name = request.Name,
    Email = request.Email,
    Password = hashed_password,
    Confirm_Password =request.Confirm_Password
 )


 db.add(new_user_info)
 db.commit()
 db.refresh(new_user_info)
 return {
    "message": "Registration Done. Have a Good Day! Please Login ",
 }
@user_router.post("/login")
def user_login(
    request: Old_User_Input,
    db: Session = Depends(get_db)
):

    existing_user = (db.query(Users_model).filter(Users_model.Email == request.Email).first())

    if not existing_user:
        raise HTTPException(status_code=401,detail="Invalid email or password")

    if password_hash.verify(request.Password,existing_user.Password):
        
        raise HTTPException(status_code=401,detail="Invalid email or password")

    token = create_token({"user_id": existing_user.User_id})

    return {
        "access_token": token,
        "token_type": "bearer"
    }




@user_router.patch("/login/update", status_code=200) # Changed from 201 to 200
def update_data(
    request: Old_User_Upgrade,
    db: Session = Depends(get_db),
    current_user_id: str = Depends(verify_token) # Secure: Extracts the identity from the bearer token
):
    # 1. Fetch the user safely using the ID extracted securely from their login token
    existing_user = db.query(Users_model).filter(Users_model.User_id == current_user_id).first()
    
    if not existing_user:
        raise HTTPException(
            status_code=404, # Changed from 401 to 404 (Not Found)
            detail="User profile not found."
        )

    # 2. Extract only fields the user explicitly sent in the payload
    update_data = request.model_dump(exclude_unset=True)
    
    # 3. Dynamic Update Loop using setattr
    for key, value in update_data.items():
        # Prevent processing dummy string placeholders or null payloads
        if value == "string" or value is None:
            continue
        setattr(existing_user, key, value)
        
    # 4. Save changes to database
    db.commit()
    db.refresh(existing_user)

    # 5. Return a structured JSON dictionary response
    return {"message": "All data updated successfully"}

# import secrets
# from datetime import datetime, timedelta
# from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
# from sqlalchemy.orm import Session
# from database import get_db
# from models.users_m import Users_model
# from schemas.users_s import ForgotPasswordInput, ResetPasswordInput

# # --- 1. FORGOT PASSWORD ENDPOINT ---
# @user_router.post("/forgot-password", status_code=200)
# def forgot_password(
#     request: ForgotPasswordInput, 
#     db: Session = Depends(get_db)
# ):
#     # Search for user by email
#     user = db.query(Users_model).filter(Users_model.Email == request.Email).first()
    
#     # SECURITY BEST PRACTICE: To prevent user enumeration attacks, 
#     # always return a 200 success message even if the email doesn't exist.
#     if not user:
#         return {"message": "If the email exists, a password reset token has been generated."}
    
#     # Generate a secure random token
#     reset_token = secrets.token_urlsafe(32)
    
#     # Store token and expiry inside your user table (Add these columns to Users_model)
#     # Expiry is set to 15 minutes from now
#     user.Reset_Token = reset_token
#     user.Token_Expiry = datetime.utcnow() + timedelta(minutes=15)
    
#     db.commit()
    
#     # TODO: Send an email to the user containing the reset_token
#     # print(f"Reset Link: http://localhost:8000/reset-password?token={reset_token}")

#     return {"message": "If the email exists, a password reset token has been generated."}


# # --- 2. RESET PASSWORD ENDPOINT ---
# @user_router.post("/reset-password", status_code=200)
# def reset_password(
#     request: ResetPasswordInput, 
#     db: Session = Depends(get_db)
# ):
#     # 1. Check if passwords match
#     if request.New_Password != request.Confirm_Password:
#         raise HTTPException(status_code=400, detail="Passwords do not match.")
        
#     # 2. Find the user with this specific active token
#     user = db.query(Users_model).filter(Users_model.Reset_Token == request.Token).first()
    
#     if not user:
#         raise HTTPException(status_code=400, detail="Invalid or expired token.")
        
#     # 3. Check if token has expired
#     if user.Token_Expiry and user.Token_Expiry < datetime.utcnow():
#          raise HTTPException(status_code=400, detail="Token has expired.")
         
#     # 4. Update the password and clear the reset token columns
#     user.Password = request.New_Password  # Ideally, hash this password before saving!
#     user.Reset_Token = None
#     user.Token_Expiry = None
    
#     db.commit()
    
#     return {"message": "Password changed successfully. You can now log in."}