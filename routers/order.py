from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.order_s import Order_Input,Order_output
from sqlalchemy.orm import Session
from database import get_db
from models.order_m import Order_model
from auth import verify_token


#-----------------
# CREATE APIROUTER
#-----------------
order_router = APIRouter(prefix="/order",tags=["Order"])

#--------------
# CREATE ORDER
#--------------
@order_router.post("/Add_order",response_model=Order_output,status_code=201)
def create_order(request:Order_Input,db:Session =Depends(get_db),user=Depends(verify_token)):
    new_order = Order_model(
    Id = request.Id,
    Order_id= request.Order_id,
    Customer_name= request.Customer_name,
    Price = request.Price,
    Slot = request.Slot,
    Created_at = request.Created_at,
    Status =request.Status,
    Action = request.Action,
    Items = request.Items,
    Quantity = request.Quantity,
    Payment_mode = request.Payment_mode
    ) 
    db.add(new_order)
    db.commit()
    db.refresh(new_order)

    return Order_output.model_validate(new_order)

# --------------------
# VIEW ALL ORDERS
# --------------------
@order_router.get("/order_view",response_model=list[Order_output],status_code=200)
def view_orders(db:Session =Depends(get_db),user=Depends(verify_token)):
    return db.query(Order_model).all()


#---------------
# SEARCH ORDER
# --------------

@order_router.get("/search_order",response_model=list [Order_output])
def search_order(
    order_id: str = Query(default=None, max_length=50, min_length=1, description="search by order Id"),
    amount: str = Query(default=None, max_length=50, min_length=1, description="search by Amount"),
    customer_name:str = Query(default= None ,max_length=50 , min_length=1 , description="search by Customer Name"),
    payment_mode : str =Query(default=None ,description="search by payment mode"),
    db:Session =Depends(get_db),user=Depends(verify_token)
  ):
    query = db.query(Order_model)

    # ---------------- 
    # Search by Order ID
    # ----------------

    if order_id:
        query = query.filter(
            Order_model.Order_id.ilike(f"%{order_id}%")
        )
    # --------------------
    # Search by Amount
    # --------------------
    if amount:
        query = query.filter(
            Order_model.Price.ilike(f"%{amount}%")
        )

    # -----------------
    # Search by Customer Name
    # -----------------

    if customer_name:
        query = query.filter(
            Order_model.Customer_name.ilike(f"%{customer_name}%")
        )

    # -----------------
    # Search by Payment mode
    # -----------------

    if payment_mode:
        query = query.filter(
            Order_model.Payment_mode.ilike(f"%{payment_mode}%")
        )

    items = query.all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching Order found"
        )

    return items

# ----------------
# upgrade data
# ----------------

@order_router.patch("/upgrade",response_model=Order_output,status_code=200)
def upgrade_order(
    request:Order_model,
    order_id: str = Query(default=None, max_length=50, min_length=1, description="search by order Id"),
    amount: str = Query(default=None, max_length=50, min_length=1, description="search by Amount"),
    customer_name:str = Query(default= None ,max_length=50 , min_length=1 , description="search by Customer Name"),
    payment_mode : str =Query(default=None ,description="search by payment mode"),
    db:Session =Depends(get_db),user=Depends(verify_token)
  ):
    query = db.query(Order_model)

    # ---------------- 
    # Search by ordr id
    # ----------------

    if order_id:
        existing_order = query.filter(
            Order_model.Order_id == order_id
        ).first()
        
    # --------------------
    # Search by amount
    # --------------------
    if amount:
        existing_order = query.filter(
            Order_model.Price == amount
        ).first()

    # -----------------
    # Search by customer name
    # -----------------

    if customer_name:
        existing_order = query.filter(
            Order_model.Customer_name == customer_name
        ).first()
        
    # -----------------
    # Search by Payment mode
    # -----------------

    if payment_mode:
        existing_order = query.filter(
            Order_model.Payment_mode == payment_mode
        ).first()

    items = existing_order

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching order found"
        )

    
    # -------------------------
    # UPDATE EXISTING ITEM
    # -------------------------

    existing_order.Id = request.Id
    existing_order.Order_id = request.Order_id
    existing_order.Customer_name = request.Customer_name
    existing_order.Price = request.Price
    existing_order.Slot = request.Slot
    existing_order.Created_at = request.Created_at
    existing_order.Status= request.Status
    existing_order.Action = request.Action
    existing_order.Items = request.Items
    existing_order.Quantity = request.Quantity
    existing_order.Payment_mode = request.Payment_mode

    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(existing_order)

    return Order_output.model_validate(existing_order)

#-------------------
# DELETE MENU ITEM
#-------------------

@order_router.delete("/Drop_Order",status_code=200)
def delete_order(
    order_id: str = Query(default=None, max_length=50, min_length=1, description="search by order Id"),
    db:Session= Depends(get_db),user=Depends(verify_token)
    ):

    query = db.query(Order_model)

    # ----------------------
    # SEARCH BY NAME
    # ----------------------

    if order_id:
        existing_order = query.filter(
            Order_model.Order_id == order_id
        ).first()
        
    else:
        raise HTTPException(
           status_code=404,
           detail="Provide Order Id"
        )
    if existing_order is None:
        raise HTTPException(
            status_code=400,
            detail="Order Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_order)
    db.commit
    return "Order deleted Successfully"
