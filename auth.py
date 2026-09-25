from jose import jwt , JWTError
from datetime import datetime,timedelta,timezone
from fastapi import HTTPException,Depends
from fastapi.security import OAuth2PasswordBearer
import os
import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM ="HS256"
ACESS_TOKEN_EXPIRE = 30

oath2_schema = OAuth2PasswordBearer(tokenUrl="/User/login")

# token create
def create_token(data:dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc)+timedelta(minutes=ACESS_TOKEN_EXPIRE)

    to_encode.update({"exp":expire})

    return jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)

def verify_token(token: str = Depends(oath2_schema)):
    try:
        payload = jwt.decode(token, SECRET_KEY,algorithms=[ALGORITHM])
        user_id: str = payload.get("user_id")

        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token details")
        
        return user_id
    
    except JWTError:
        raise HTTPException(status_code=401 ,detail="Invaild Token Given")