from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.stock_s import Stock_output,Stocks_Input
from sqlalchemy.orm import Session
from database import get_db
from models.stock_m import Stock_model
from auth import verify_token

#-----------------
# CREATE APIROUTER
#-----------------
stock_router = APIRouter(prefix="/Stock",tags=["Stock"])

#--------------
# CREATE Stock
#--------------
# ==========================================
# FILE: routers/stock_r.py
# ==========================================
@stock_router.patch("/Add_inventory", response_model=Stock_output)
def add_inventory(menu_id: str, incoming_quantity: float, db: Session = Depends(get_db), user_id = Depends(verify_token)):
    # Look up the unique stock record belonging to this menu item
    stock_record = db.query(Stock_model).filter(
        Stock_model.Menu_id == menu_id,
        Stock_model.User_id == user_id
    ).first()
    
    if not stock_record:
        raise HTTPException(status_code=404, detail="Stock row for this menu item not found.")
        
    # Increase the quantity balance
    stock_record.Quantity += incoming_quantity
    
    # Automatically toggle status based on availability
    if stock_record.Quantity > 0:
        stock_record.Status = "In Stock"
        
    db.commit()
    db.refresh(stock_record)
    return stock_record

# --------------------
# VIEW ALL stocks
# --------------------
@stock_router.get("/stocks_view",response_model=list[Stock_output],status_code=200)
def view_stocks(db:Session =Depends(get_db),user_id=Depends(verify_token)):
    return db.query(Stock_model).filter(Stock_model.User_id == user_id).all()


#---------------
# SEARCH stock
# --------------

@stock_router.get("/search_stock",response_model=list[Stock_output])
def search_stock(
    Raw_material: str = Query(default=None, max_length=50, min_length=1, description="search by Raw Material"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Stock_model).filter(Stock_model.User_id == user_id)

    # ---------------- 
    # Search by Raw material
    # ----------------

    if Raw_material:
        query = query.filter(
            Stock_model.Raw_material.ilike(f"%{Raw_material}%")
        )
    items = query.all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching Raw Material found"
        )

    return items

# ----------------
# upgrade data
# ----------------

@stock_router.patch("/upgrade",response_model=Stock_output,status_code=200)
def upgrade_stock(
    request : Stocks_Input,
    Raw_material: str = Query(default=None, max_length=50, min_length=1, description="search by Raw Material"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Stock_model).filter(Stock_model.User_id == user_id)

    # ---------------- 
    # Search by Raw material
    # ----------------

    if Raw_material:
        existing_stock = query.filter(
            Stock_model.Raw_material.ilike(f"%{Raw_material}%")
        ).first()

    items = existing_stock

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching Raw Material found"
        )

 
    # -------------------------
    # UPDATE EXISTING PURCHASE
    # -------------------------
    existing_stock.Adjust = request.Adjust


    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(existing_stock)

    return Stock_output.model_validate(existing_stock)

#-------------------
# DELETE stock item
#-------------------

@stock_router.delete("/Drop_stock",status_code=200)
def delete_stock(
    Raw_material: str = Query(default=None, max_length=50, min_length=1, description="search by Raw Material"),
    db:Session =Depends(get_db),user=Depends(verify_token)
  ):

    query = db.query(Stock_model)

    # ----------------------
    # SEARCH BY Raw materials
    # ----------------------

    if Raw_material:
        existing_stock = query.filter(
            Stock_model.Raw_material == Raw_material
        ).first()

    else:
        raise HTTPException(
           status_code=404,
           detail="Provide Purchase Information in order"
        )
    if existing_stock is None:
        raise HTTPException(
            status_code=400,
            detail="Purchase Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_stock)
    db.commit()
    return "stock deleted Successfully"
