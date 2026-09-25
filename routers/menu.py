from fastapi import APIRouter,Depends,HTTPException,Query
from schemas.menu_s import Menu_Input, Menu_output
from sqlalchemy.orm import Session
from database import get_db
from models.menu_m import Menu_model
from models.stock_m import Stock_model
from sqlalchemy import or_ 
from generator.user_id import generate_unique_id
from auth import verify_token

#-----------------
# CREATE APIROUTER
#-----------------
menu_router = APIRouter(prefix="/menu",tags=["Menu"])

#--------------
# CREATE ITEMS 
#--------------
@menu_router.post("/Add_item",response_model=Menu_output,status_code=201)
def create_menu(request:Menu_Input,db:Session =Depends(get_db),user_id=Depends(verify_token)):
        # 1. Automatically generate a unique supplier ID (e.g., SUP-0001)
    auto_id = generate_unique_id(db, Menu_model, prefix="Menu")

    new_item = Menu_model(
        Id =auto_id,
        User_id = user_id,
        Item_name = request.Item_name,
        Alte_name = request.Alte_name,
        Price = request.Price,
        Alte_price = request.Alte_price,
        Short_code = request.Short_code,
        Alte_short_code = request.Alte_short_code,
        Category = request.category,
        Tax_rate = request.Tax_rate,
        Discount = request.Discount,
        Hsn_code = request.Hsn_code,
        Recipe = [ recipe.model_dump() for recipe in request.Recipes] #Recipe is a Pydantic model, convert it to a dictionary before saving.
        )
    db.add(new_item)
    
    # 2. AUTO-CREATE AN EMPTY STOCK RECORD FOR THIS NEW MENU ITEM
    auto_stock_id = generate_unique_id(db, Stock_model, prefix="STK")
    new_stock_entry = Stock_model(
        Id=auto_stock_id,
        User_id=user_id,
        Menu_id=auto_id,     # Link directly to our newly generated Menu ID
        Quantity=0.0,        # Initial stock balance is zero
        Status="Out of Stock"
    )
    db.add(new_stock_entry)
    db.commit()
    db.refresh(new_item)

    return Menu_output.model_validate(new_item)

# --------------------
# VIEW ALL MENU ITEMS
# --------------------
@menu_router.get("/menu_view",response_model=list[Menu_output],status_code=200)
def view_menu(db:Session =Depends(get_db),user_id=Depends(verify_token)):
    return db.query(Menu_model).filter(Menu_model.User_id == user_id).all()


#---------------
# SEARCH ITEMS 
# --------------

@menu_router.get("/search_item",response_model=list [Menu_output])
def menu_search_item(
    name: str = Query(default=None, max_length=50, min_length=1, description="search by product name"),
    short_code: str = Query(default=None, max_length=50, min_length=1, description="search by product short code"),
    category:str = Query(default= None ,max_length=50 , min_length=1 , description="search by product category"),
    db:Session =Depends(get_db),user_id=Depends(verify_token)
  ):
    query = db.query(Menu_model).filter(Menu_model.User_id == user_id)

    # ---------------- 
    # Search by name
    # ----------------

    if name:
        query = query.filter(
            Menu_model.Item_name.ilike(f"%{name}%")
        )
    # --------------------
    # Search by short code
    # --------------------
    if short_code:
        query = query.filter(
            Menu_model.Short_code.ilike(f"%{short_code}%")
        )

    # -----------------
    # Search by category
    # -----------------

    if category:
        query = query.filter(
            Menu_model.Category.ilike(f"%{category}%")
        )

    items = query.all()

    if not items:
        raise HTTPException(
            status_code=404,
            detail="No matching items found"
        )

    return items

# ----------------
# upgrade data
# ----------------

@menu_router.patch("/upgrade",response_model=Menu_output,status_code=200)
def menu_upgrade_item(
    request:Menu_Input,
    name: str = Query(default=None, max_length=50, min_length=1, description="search by product name"),
    short_code: str = Query(default=None, max_length=50, min_length=1, description="search by product short code"),
    category:str = Query(default= None ,max_length=50 , min_length=1 , description="search by product category"),
    db:Session= Depends(get_db),user_id=Depends(verify_token)
    ):

    query = db.query(Menu_model).filter(Menu_model.User_id == user_id)

    # ----------------------
    # SEARCH BY NAME
    # ----------------------

    if name:
        existing_value = query.filter(or_ (
            Menu_model.Item_name == name ,
            Menu_model.Alte_name == name)
            ).first()
        
    # -------------------------
    # SEARCH BY SHORT CODE
    # -------------------------        

    elif short_code:
        
        existing_value = query.filter(or_(
            Menu_model.Short_code == short_code,
            Menu_model.Alte_short_code == short_code
            )
            ).first()
        
        
    # -------------------------
    # SEARCH BY CATEGORY
    # -------------------------
    elif category:

        existing_value = query.filter(Menu_model.Category == category).first()

    else:
        raise HTTPException(
           status_code=404,
           detail="Provide Name ,Short code or Catagory"
        )


    # -------------------------
    # ITEM NOT FOUND
    # -------------------------
    if existing_value is None:

        raise HTTPException(
            status_code=404,
            detail="Item not found"
        )
    
    # -------------------------
    # UPDATE EXISTING ITEM
    # -------------------------
    Update_data = request.model_dump(exclude_unset=True)

    if "Recipes" in Update_data and Update_data["Recipes"] is not None:
        existing_value.Recipe = [recipe.model_dump() for recipe in request.Recipes]
        del Update_data["Recipes"]
        
    for key ,value in Update_data.items():

        if value == "string" or value is None:
            continue

        if (key in ["Price","Alte_price","Tax_rate","Discount","Hsn_code"]) and value == 0.0:
            continue



        setattr(existing_value,key,value)
        
    # -------------------------
    # SAVE
    # -------------------------


    db.commit()
    db.refresh(existing_value)

    return Menu_output.model_validate(existing_value)

#-------------------
# DELETE MENU ITEM
#-------------------

@menu_router.delete("/Drop_Item",status_code=200)
def menu_item_delete(
    name: str = Query(default=None, max_length=50, min_length=1, description="search by product name"),
    short_code: str = Query(default=None, max_length=50, min_length=1, description="search by product short code"),
    db:Session= Depends(get_db),user_id=Depends(verify_token)
    ):

    query = db.query(Menu_model).filter(Menu_model.User_id == user_id)

    # ----------------------
    # SEARCH BY NAME
    # ----------------------

    if name:
        existing_value = query.filter(or_ (
            Menu_model.Item_name == name ,
            Menu_model.Alte_name == name)
            ).first()
        
    # -------------------------
    # SEARCH BY SHORT CODE
    # -------------------------        

    elif short_code:
        
        existing_value = query.filter(or_(
            Menu_model.Short_code == short_code,
            Menu_model.Alte_short_code == short_code
            )
            ).first()

    else:
        raise HTTPException(
           status_code=404,
           detail="Provide Name ,Short code or Catagory"
        )
    if existing_value is None:
        raise HTTPException(
            status_code=400,
            detail="Item Not Found"
        )
    #-------------
    # DELETE ITEM
    #-------------

    db.delete(existing_value)
    db.commit()
    return "Item deleted Successfully"
