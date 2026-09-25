from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.sales_s import Sales_Input , Sales_Output
from sqlalchemy.orm import Session
from database import get_db
from models.sales_m import Sale_model
from models.menu_m import Menu_model
from models.stock_m import Stock_model
from auth import verify_token
from generator.user_id import generate_unique_id
#-----------------
# CREATE APIROUTER
#-----------------
sale_router = APIRouter(prefix="/sale",tags=["Sale"])

# ==========================================
# FILE: routers/sale_r.py
# ==========================================
@sale_router.post("/Add_sale", response_model=Sales_Output, status_code=201)
def create_sale(request: Sales_Input, db: Session = Depends(get_db), user_id = Depends(verify_token)):
    # 1. Locate the item being sold in the Menu table
    menu_item = db.query(Menu_model).filter(
        Menu_model.Item_name == request.Item_name,
        Menu_model.User_id == user_id
    ).first()
    
    if not menu_item:
        raise HTTPException(status_code=404, detail="Item not found on your menu.")

    # 2. FIXED BUG: Look up using Stock_model.Menu_id instead of Stock_model.Id
    stock_record = db.query(Stock_model).filter(
        Stock_model.Menu_id == menu_item.Id,
        Stock_model.User_id == user_id
    ).first()
    
    if not stock_record:
        raise HTTPException(status_code=404, detail="No inventory tracking record exists for this item.")

    # 3. Verify stock availability
    if stock_record.Quantity < request.Quantity:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient inventory! Only {stock_record.Quantity} items remaining."
        )
    
    # 4. Deduct stock balance
    stock_record.Quantity -= request.Quantity
    if stock_record.Quantity == 0:
        stock_record.Status = "Out of Stock"

    # 5. Generate safe transaction tracking IDs
    auto_invoice = generate_unique_id(db, Sale_model, prefix="INV")
    auto_pk_id = generate_unique_id(db, Sale_model, prefix="SALE")

    new_sales = Sale_model(
        Id=auto_pk_id,
        menu_item_id=menu_item.Id, # Save structural key association
        User_id=user_id,
        Invoice=auto_invoice,
        Order_type=request.Order_type,
        Customer_name=request.Customer_name,
        Phone_number=request.Phone_number,
        Address=request.Address,
        Gst_number=request.Gst_number,
        Item_name=request.Item_name,
        Hsn_code=request.Hsn_code,
        Quantity=request.Quantity,
        Price=request.Price,
        Tax_type=request.Tax_type,
        Tax_Apply=request.Tax_Apply,
        Tax_rate=request.Tax_rate,
        Tax_amount=request.Tax_amount,
        Discount=request.Discount,
        Total_amount=request.Total_amount,
        Payment_mode=request.Payment_mode
    ) 
    
    db.add(new_sales)
    db.commit()
    db.refresh(new_sales)

    return Sales_Output.model_validate(new_sales)


# --------------------
# VIEW ALL SALES
# --------------------
@sale_router.get("/sale_view",response_model=list[Sales_Output],status_code=200)
def view_sales(db:Session =Depends(get_db),user_id=Depends(verify_token)):
    return db.query(Sale_model).filter(Sale_model.User_id == user_id).all()


#---------------
# SEARCH SALES
# --------------

@sale_router.get("/search_sale_bill",response_model=list [Sales_Output])
def search_sale_bill(
    Invoice: str = Query(default=None, max_length=50, min_length=1, description="search supplier name"),
    Amount: str = Query(default=None, max_length=50, min_length=1, description="search by date"),
    Payment_mode :str =Query(default=None ,description="Search by payment mode"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Sale_model).filter(Sale_model.User_id == user_id)

    # ---------------- 
    # Search by Invoice
    # ----------------

    if Invoice:
        existing_Sale = query.filter(
            Sale_model.Invoice.ilike(f"%{Invoice}%")
        )
    # --------------------
    # Search by Amount
    # --------------------
    if Amount :
        existing_Sale = query.filter(
            Sale_model.Total_amount.ilike((f"%{Amount}%"))
        )

    # -----------------
    # Search by payment Mode
    # -----------------

    if Payment_mode:
        existing_Sale = query.filter(
            Sale_model.Payment_mode.ilike(f"%{Payment_mode}%")
        )

    items = existing_Sale.all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching Sale found"
        )
 

    return items

# ----------------
# upgrade data
# ----------------

@sale_router.patch("/upgrade",response_model=Sales_Output,status_code=200)
def upgrade_sale(
    request : Sales_Input,
    Invoice: str = Query(default=None, max_length=50, min_length=1, description="search supplier name"),
    Amount: str = Query(default=None, max_length=50, min_length=1, description="search by date"),
    Payment_mode :str =Query(default=None ,description="Search by payment mode"),
    db:Session =Depends(get_db),user_id = Depends(verify_token)
  ):
    query = db.query(Sale_model).filter(Sale_model.User_id == user_id)

    # ---------------- 
    # Search by Invoice
    # ----------------

    if Invoice:
        existing_Sale = query.filter(
            Sale_model.Invoice.ilike(f"%{Invoice}%")
        )
    # --------------------
    # Search by Amount
    # --------------------
    if Amount :
        existing_Sale = query.filter(
            Sale_model.Total_amount.ilike((f"%{Amount}%"))
        )

    # -----------------
    # Search by payment Mode
    # -----------------

    if Payment_mode:
        existing_Sale = query.filter(
            Sale_model.Payment_mode.ilike(f"%{Payment_mode}%")
        )


    items = existing_Sale.first()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching purchase found"
        )
 
    # -------------------------
    # UPDATE EXISTING SALES
    # -------------------------
    update_data = request.model_dump(exclude_unset= True)
    
    for key , value in update_data.items():
        if value == "string" or value == 0 :
            continue
        if (key in ["Price","Tax_rate","Tax_amount","Discount","Total_amount"]) and value == 0:
            continue
        setattr(existing_Sale,key,value)

    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(existing_Sale)

    return Sales_Output.model_validate(existing_Sale)

#-------------------
# DELETE SALES
#-------------------

@sale_router.delete("/Drop_Sale_bill",status_code=200)
def delete_sale(
    Invoice: str = Query(default=None, max_length=50, min_length=1, description="search supplier name"),
    Amount: str = Query(default=None, max_length=50, min_length=1, description="search by date"),
    Payment_mode :str =Query(default=None ,description="Search by payment mode"),
    db:Session= Depends(get_db),user_id=Depends(verify_token)
    ):

    query = db.query(Sale_model).filter(Sale_model.User_id == user_id)

    # ----------------------
    # SEARCH BY INVOICE , AMOUNT AND PAYMENT MODE
    # ----------------------

    if Invoice :
        existing_sale= query.filter(Sale_model.Invoice == Invoice)
        
    if Amount:
        existing_sale=query.filter(Sale_model.Total_amount == f"%{Amount}%")

    if Payment_mode:
        existing_sale =query.filter(Sale_model.Payment_mode == Payment_mode)

    
    if existing_sale is None:
        raise HTTPException(
            status_code=400,
            detail="Sale Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_sale)
    db.commit()
    return "Sale deleted Successfully"
