from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.purchase_s import Purchase_Input,Purchase_output
from sqlalchemy.orm import Session
from database import get_db
from models.purchase_m import Purchase_model
from sqlalchemy import or_
from auth import verify_token
from generator.user_id import generate_unique_id
from models.supplier_m import Supplier_model
#-----------------
# CREATE APIROUTER
#-----------------
purchase_router = APIRouter(prefix="/purchase",tags=["purchase"])

#--------------
# CREATE PURCAHSE
#--------------

from models.stock_m import Stock_model

@purchase_router.post("/Add_purchase", response_model=Purchase_output, status_code=201)
def create_purchase(request: Purchase_Input, db: Session = Depends(get_db), user_id = Depends(verify_token)):
    
    # 1. VERIFY AND FETCH THE SUPPLIER BY NAME
    supplier_record = db.query(Supplier_model).filter(
        Supplier_model.Supplier == request.Supplier_name,
        Supplier_model.User_id == user_id
    ).first()
    
    if not supplier_record:
        raise HTTPException(status_code=404, detail=f"Supplier '{request.Supplier_name}' not found. Please register the supplier first.")

    # 2. FETCH OR AUTO-CREATE THE RAW MATERIAL IN STOCK
    stock_record = db.query(Stock_model).filter(
        Stock_model.Raw_material.ilike(request.Raw_material),
        Stock_model.User_id == user_id
    ).first()
    
    if not stock_record:
        # If this raw material was never tracked, initialize a brand new line item
        auto_stock_id = generate_unique_id(db, Stock_model, prefix="STK")
        stock_record = Stock_model(
            Id=auto_stock_id,
            User_id=user_id,
            Supplier=request.Supplier_name,
            Raw_material=request.Raw_material,
            Quantity=0.0,
            Status="In Stock"
        )
        db.add(stock_record)
    
    # 3. STOCK INCREMENT LOGIC
    stock_record.Quantity += request.Quantity
    stock_record.Status = "In Stock" if stock_record.Quantity > 0 else "Out of Stock"

    # 4. SUPPLIER BALANCE ADJUSTMENT LOGIC
    # Dynamically tracking debt based on payment criteria strings
    if request.Amount_status.lower() == "paid":
        supplier_record.Paid += request.Total_amount
    elif request.Amount_status.lower() == "unpaid":
        supplier_record.Unpaid += request.Total_amount
    else:
        raise HTTPException(status_code=400, detail="Amount_status must be either 'Paid' or 'Unpaid'")

    # 5. GENERATE TRANSACTION PRIMARY KEY AND PERSIST
    auto_id = generate_unique_id(db, Purchase_model, prefix="PUR")
    
    new_purchase = Purchase_model(
        Id=auto_id,
        User_id=user_id,
        supplier_id=supplier_record.Id, # Crucial: Save the structural link key reference
        Supplier_name=request.Supplier_name,
        Date=request.Date,
        Invoice=request.Invoice,
        Raw_material=request.Raw_material,
        Quantity=request.Quantity,
        Rate=request.Rate,
        Discount=request.Discount,
        Taxable_amount=request.Taxable_amount,
        Tax_rate=request.Tax_rate,
        Other_charges=request.Other_charges,
        Total_amount=request.Total_amount,
        Amount_status=request.Amount_status,
        Created_at=request.Created_at
    ) 
    
    db.add(new_purchase)
    db.commit() # Saves Purchase Invoice, updates Stock inventory levels, and Supplier balances simultaneously
    db.refresh(new_purchase)

    return Purchase_output.model_validate(new_purchase)

# --------------------
# VIEW ALL PURCHASES
# --------------------
@purchase_router.get("/purchase_view",response_model=list[Purchase_output],status_code=200)
def view_purchases(db:Session =Depends(get_db),user_id=Depends(verify_token)):
    return db.query(Purchase_model).filter(Purchase_model.User_id == user_id).all()


#---------------
# SEARCH purchase 
# --------------

@purchase_router.get("/search_purchase",response_model=list [Purchase_output])
def search_purchase(
    supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search by suppiler name"),
    Date_from: str = Query(default=None, max_length=50, min_length=1, description="search by Date from"),
    Date_to :str = Query(default= None ,max_length=50 , min_length=1 , description="search by Date to"),
    amount_status : str =Query(default=None ,description="search by Amount satuts"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Purchase_model).filter(Purchase_model.User_id == user_id)
    # ---------------- 
    # Search by suppplier name
    # ----------------

    if supplier_name:
        query = query.filter(
            Purchase_model.Supplier_name.ilike(f"%{supplier_name}%")
        )
    # --------------------
    # Search by DATE
    # --------------------
    if Date_from:
        query = query.filter(Purchase_model.Date >= Date_from)

    if Date_to:
        query = query.filter(Purchase_model.Date <= Date_to)
    # -----------------
    # Search by amount Status
    # -----------------

    if amount_status:
        query = query.filter(
            Purchase_model.Amount_status.ilike(f"%{amount_status}%")
        )


    items = query.all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching purchase found"
        )

    return items

# ----------------
# upgrade data
# ----------------

@purchase_router.patch("/upgrade",response_model=Purchase_output,status_code=200)
def upgrade_purchase(
    request : Purchase_Input,
    supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search by suppiler name"),
    Date_from: str = Query(default=None, max_length=50, min_length=1, description="search by Date from"),
    Date_to :str = Query(default= None ,max_length=50 , min_length=1 , description="search by Date to"),
    amount_status : str =Query(default=None ,description="search by Amount satuts"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Purchase_model).filter(Purchase_model.User_id == user_id)

    # ---------------- 
    # Search by suppplier name
    # ----------------

    if supplier_name:
        existing_purchase = query.filter(
            Purchase_model.Supplier_name.ilike(f"%{supplier_name}%")
        ).first()
    # --------------------
    # Search by DATE
    # --------------------
    if Date_from and Date_to :
        existing_purchase = query.filter(
            Purchase_model.Date.ilike((or_(f"%{Date_from }%",f"%{Date_to}%"))
        )).first()

    # -----------------
    # Search by amount Status
    # -----------------

    if amount_status:
        existing_purchase = query.filter(
            Purchase_model.Amount_status.ilike(f"%{amount_status}%")
        ).first()


    items = existing_purchase

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching purchase found"
        )
 
    # -------------------------
    # UPDATE EXISTING PURCHASE
    # -------------------------

    update_date = request.model_dump(exclude_unset=True)

    for key , value in update_date.items():

        if value == "string" or value is None:
            continue

        if (key in ["Rate","Discount","Taxable_amount","Total_amount","Tax_rate"]) and value == 0:
            continue

        setattr(existing_purchase,key,value)

    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(existing_purchase)

    return Purchase_output.model_validate(existing_purchase)

#-------------------
# DELETE MENU ITEM
#-------------------

@purchase_router.delete("/Drop_purchase",status_code=200)
def delete_purchase(
    Supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search supplier name"),
    Date: str = Query(default=None, max_length=50, min_length=1, description="search by date"),
    db:Session= Depends(get_db),user_id=Depends(verify_token)
    ):

    query = db.query(Purchase_model).filter(Purchase_model.User_id == user_id)

    # ----------------------
    # SEARCH BY SUPPLIER NAME and Date
    # ----------------------

    if Supplier_name and Date:
        existing_purchase = query.filter(or_(
            Purchase_model.Supplier_name == Supplier_name,
            Purchase_model.Date == Date
        )).first()
    else:
        raise HTTPException(
           status_code=404,
           detail="Provide Purchase Information in order"
        )
    if existing_purchase is None:
        raise HTTPException(
            status_code=400,
            detail="Purchase Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_purchase)
    db.commit()
    return "Purchase deleted Successfully"


# ==========================================
# FILE: routers/purchase_r.py
# ==========================================
from models.supplier_m import Supplier_model
from models.stock_m import Stock_model

@purchase_router.patch("/upgrade", response_model=Purchase_output, status_code=200)
def upgrade_purchase(
    request: Purchase_Input,
    supplier_name: str = Query(default=None, max_length=50, min_length=1, description="search by supplier name"),
    Date_from: str = Query(default=None, max_length=50, min_length=1, description="search by Date from"),
    Date_to: str = Query(default=None, max_length=50, min_length=1, description="search by Date to"),
    amount_status: str = Query(default=None, description="search by Amount status"),
    db: Session = Depends(get_db),
    user_id = Depends(verify_token)
):
    # 1. INITIALIZE BASE QUERY WITH USER TENANCY FILTER
    query = db.query(Purchase_model).filter(Purchase_model.User_id == user_id)

    # 2. CHAIN FILTERS SAFELY (No overwriting variables)
    if supplier_name:
        query = query.filter(Purchase_model.Supplier_name.ilike(f"%{supplier_name}%"))
    if Date_from:
        query = query.filter(Purchase_model.Date >= Date_from)
    if Date_to:
        query = query.filter(Purchase_model.Date <= Date_to)
    if amount_status:
        query = query.filter(Purchase_model.Amount_status.ilike(f"%{amount_status}%"))

    existing_purchase = query.first()

    if not existing_purchase:
        raise HTTPException(
            status_code=404,
            detail="No matching purchase invoice found to upgrade"
        )
 
    # Extract only explicitly sent update fields
    update_data = request.model_dump(exclude_unset=True)

    # ------------------------------------------------------------
    # 3. ADVANCED SYNC BALANCE & STOCK RE-CALCULATION LOGIC
    # ------------------------------------------------------------
    
    # Track changes to Quantity to sync Stock inventory levels
    if "Quantity" in update_data and update_data["Quantity"] not in ["string", None, 0]:
        new_qty = float(update_data["Quantity"])
        qty_difference = new_qty - existing_purchase.Quantity
        
        # Look up inventory stock card line item
        stock_record = db.query(Stock_model).filter(
            Stock_model.Raw_material.ilike(existing_purchase.Raw_material),
            Stock_model.User_id == user_id
        ).first()
        
        if stock_record:
            stock_record.Quantity += qty_difference
            stock_record.Status = "In Stock" if stock_record.Quantity > 0 else "Out of Stock"

    # Track changes to Total_amount or Amount_status to sync Supplier balances
    target_status = update_data.get("Amount_status", existing_purchase.Amount_status).lower()
    target_amount = float(update_data.get("Total_amount", existing_purchase.Total_amount))
    
    # Only run ledger re-balancing if values actually changed
    if (target_amount != existing_purchase.Total_amount) or ("Amount_status" in update_data):
        supplier_record = db.query(Supplier_model).filter(
            Supplier_model.Id == existing_purchase.supplier_id,
            Supplier_model.User_id == user_id
        ).first()
        
        if supplier_record:
            # Revert the old transaction numbers entirely first
            if existing_purchase.Amount_status.lower() == "paid":
                supplier_record.Paid -= existing_purchase.Total_amount
            elif existing_purchase.Amount_status.lower() == "unpaid":
                supplier_record.Unpaid -= existing_purchase.Total_amount
                
            # Apply the updated values dynamically
            if target_status == "paid":
                supplier_record.Paid += target_amount
            elif target_status == "unpaid":
                supplier_record.Unpaid += target_amount

    # ------------------------------------------------------------
    # 4. RUN SYSTEM ATTRIBUTE SETTERS & SAVE
    # ------------------------------------------------------------
    for key, value in update_data.items():
        if value == "string" or value is None:
            continue
        if (key in ["Rate", "Discount", "Taxable_amount", "Total_amount", "Tax_rate"]) and value == 0:
            continue

        setattr(existing_purchase, key, value)

    db.commit()
    db.refresh(existing_purchase)

    return Purchase_output.model_validate(existing_purchase)
