from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.supplier_s import Supplier_output, Suppliers_Input
from sqlalchemy.orm import Session
from database import get_db
from models.supplier_m import Supplier_model
from auth import verify_token
from generator.user_id import generate_unique_id
#-----------------
# CREATE APIROUTER
#-----------------
supplier_router = APIRouter(prefix="/supplier",tags=["supplier"])

#--------------
# CREATE SUPPLIER
#--------------
@supplier_router.post("/Add_supplier",response_model=Supplier_output,status_code=201)
def create_supplier(request:Suppliers_Input,db:Session =Depends(get_db),user_id=Depends(verify_token)):
        # 1. Automatically generate a unique supplier ID (e.g., SUP-0001)
    auto_id = generate_unique_id(db, Supplier_model, prefix="SUP")
    new_supplier = Supplier_model(
    Id = auto_id,
    User_id = user_id,
    Supplier = request.Supplier,
    Address = request.Address,
    Gst_number = request.Gst_number,
    phone_number= request.phone_number,
    email_id = request.email_id,
    Pan_number = request.Pan_number,
    Paid = request.Paid,
    Unpaid= request.Unpaid,
    Tan_number= request.Tan_number,
    Bank_Account_Number = request.Bank_Account_Number,
    IFSC_code = request.IFSC_code,
    UPI_ID= request.UPI_ID,
    
    ) 
    db.add(new_supplier)
    db.commit()
    db.refresh(new_supplier)

    return Supplier_output.model_validate(new_supplier)

# --------------------
# VIEW ALL supplier
# --------------------
@supplier_router.get("/supplier_view",response_model=list[Supplier_output],status_code=200)
def view_supplier(db:Session =Depends(get_db),user=Depends(verify_token)):
    return db.query(Supplier_model).all()


#---------------
# SEARCH supplier
# --------------
# ==========================================
# FILE: routers/supplier_r.py
# ==========================================
@supplier_router.get("/search_supplier", response_model=list[Supplier_output])
def search_supplier(
    supplier_name: str = Query(default=None),
    Gst_number: str = Query(default=None),
    db: Session = Depends(get_db), user_id = Depends(verify_token)
):
    # Initialize base criteria scoped strictly to the logged-in user context
    query = db.query(Supplier_model).filter(Supplier_model.User_id == user_id)

    if supplier_name:
        query = query.filter(Supplier_model.Supplier.ilike(f"%{supplier_name}%"))
    if Gst_number:
        query = query.filter(Supplier_model.Gst_number.ilike(f"%{Gst_number}%"))

    items = query.all()
    if not items:
        raise HTTPException(status_code=404, detail="No matching Supplier found")
    return items

# ----------------
# upgrade data
# ----------------

@supplier_router.patch("/upgrade",response_model=Supplier_output,status_code=200)
def upgrade_supplier(
    request : Suppliers_Input,
    supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search by suppiler name"),
    Gst_number: str = Query(default=None, max_length=50, min_length=1, description="search by GST Number"),
    db:Session =Depends(get_db),user_id = Depends(verify_token)
  ):

    query = db.query(Supplier_model).filter(Supplier_model.User_id == user_id)

    if supplier_name:
        query = query.filter(Supplier_model.Supplier.ilike(f"%{supplier_name}%"))

    if Gst_number:
        query = query.filter(Supplier_model.Gst_number.ilike(f"%{Gst_number}%"))

    existing_supplier = query.first()

    if not existing_supplier:
        raise HTTPException(status_code=404, detail="No matching Supplier found")
    
    # -------------------------
    # UPDATE EXISTING SUPPLIER
    # -------------------------
    # Extracts ONLY the fields the user explicitly sent in Swagger
    update_data = request.model_dump(exclude_unset=True)

    for key, value in update_data.items():
        # ⚠️ THE FIX: If the value is Swagger's default placeholder, skip updating it!
        if value == "string" or value is None:
            continue
        
        # Prevent numbers from resetting to zero if the user didn't intentionally change them
        if (key in ["phone_number", "Paid", "Unpaid"]) and value == 0:
            continue

        setattr(existing_supplier, key, value)

    

    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(query)

    return Supplier_output.model_validate(query)

#-------------------
# DELETE MENU ITEM
#-------------------

@supplier_router.delete("/Drop_supplier",status_code=200)
def delete_purchase(
    supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search by suppiler name"),
    Gst_number: str = Query(default=None, max_length=50, min_length=1, description="search by GST Number"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):

    query = db.query(Supplier_model).filter(Supplier_model.User_id == user_id)

    # ----------------------
    # SEARCH BY SUPPLIER NAME and GST Number
    # ----------------------

    if supplier_name :
        existing_supplier = query.filter(
            Supplier_model.Supplier == supplier_name
            ).first()
    if Gst_number:
        existing_supplier = query.filter(
            Supplier_model.Gst_number == Gst_number
            ).first()
                
    if existing_supplier is None:
        raise HTTPException(
            status_code=400,
            detail="Supplier  Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_supplier)
    db.commit()
    return "Supplier deleted Successfully"
