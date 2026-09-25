from fastapi  import FastAPI
from database import engine
from models import  users_m,menu_m, order_m, purchase_m, sales_m, stock_m,  supplier_m, users_m
from routers.menu import menu_router
from routers.sales import sale_router
from routers.purchase import purchase_router
from routers.stock import stock_router
from routers.supplier import supplier_router
from routers.user import user_router
app = FastAPI(title="GO Grocery")




@app.get("/")
def home():
    return {
        "message" :
          " Digital grocery shop for owner "
     }


def table_create(Table_name):
    for table in Table_name:
        table.Base.metadata.create_all(bind=engine)

table_list = [users_m,menu_m,purchase_m, sales_m, stock_m,  supplier_m]
table_create(table_list)




def router_call(router_name):
 for router in router_name:
  app.include_router(router)

routers_list = [user_router,menu_router,sale_router,purchase_router,stock_router,supplier_router]
router_call(routers_list)

