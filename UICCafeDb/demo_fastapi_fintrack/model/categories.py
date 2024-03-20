# model/categories.py
from fastapi import Depends, HTTPException, APIRouter, Form
from .db import get_db
import bcrypt


ProductsRouter = APIRouter(tags=["Products"])


#Get all
@ProductsRouter.get("/products/", response_model=list)
async def read_products(
    db=Depends(get_db)
):
    query = "SELECT ProductID, ProductName, Stock, UnitPrice, TakeoutFee FROM products"
    db[0].execute(query)
    products = [{
                    "ProductID": products[0],
                    "ProductName": products[1],
                    "Stock": products[2],
                    "UnitPrice": products[3],
                    "TakeoutFee": products[4],

                } for products in db[0].fetchall()
                ]
    return products

#Get distinct
@ProductsRouter.get("/products/{ProductID}", response_model=dict)
async def read_product(
    ProductID: int,
    db=Depends(get_db)
):
    query = "SELECT ProductID, ProductName, Stock, UnitPrice, TakeoutFee FROM products WHERE ProductID = %s"
    db[0].execute(query, (ProductID,))
    products = db[0].fetchone()
    if products:
        return {
                    "ProductID": products[0],
                    "ProductName": products[1],
                    "Stock": products[2],
                    "UnitPrice": products[3],
                    "TakeoutFee": products[4],
               }
    raise HTTPException(status_code=404, detail="Products not found")

#post
@ProductsRouter.post("/products/", response_model=dict)
async def create_product(
        SubCateID: str = Form(...),
        ProductName: str = Form(...),
        Stock: str = Form(...),
        UnitPrice: str = Form(...),
        TakeoutFee: str = Form(...),
    db=Depends(get_db)
): 
    query = "INSERT INTO products (SubCateID, ProductName, Stock, UnitPrice, TakeoutFee) VALUES (%s, %s, %s, %s, %s)"
    db[0].execute(query, ( SubCateID, ProductName,  Stock, UnitPrice, TakeoutFee))

     # Retrieve the last inserted ID using LAST_INSERT_ID()
    db[0].execute("SELECT LAST_INSERT_ID()")
    new_product_id = db[0].fetchone()[0]
    db[1].commit()




    return {
        "AccountID": new_product_id, 
        "SubCateID": SubCateID, 
        "ProductName": ProductName,
        "Stock": Stock,
        "UnitPrice": UnitPrice,
        "TakeoutFee": TakeoutFee}

#edit
@ProductsRouter.put("/products/{ProductID}", response_model=dict)
async def update_product(
    ProductID: int,     
        SubCateID: str = Form(...),
        ProductName: str = Form(...),
        Stock: str = Form(...),
        UnitPrice: str = Form(...),
        TakeoutFee: str = Form(...),
    db=Depends(get_db)
):

    # Update user information in the database
    query = "UPDATE products SET SubCateID = %s, ProductName = %s, Stock = %s, UnitPrice = %s, TakeoutFee = %s WHERE ProductID = %s"
    db[0].execute(query, ( SubCateID, ProductName,  Stock, UnitPrice, TakeoutFee, ProductID))




    # Check if the update was successful
    if db[0].rowcount > 0:
        db[1].commit()
        return {"message": "Product updated successfully"}
   
    # If no rows were affected, user not found
    raise HTTPException(status_code=404, detail="Product not found")






@ProductsRouter.delete("/products/{ProductID}", response_model=dict)
async def delete_product(
    ProductID: int,
    db=Depends(get_db)
):
    try:
        # Check if the product exists
        query_check_product = "SELECT ProductID FROM products WHERE ProductID = %s"
        db[0].execute(query_check_product, (ProductID,))
        existing_product = db[0].fetchone()




        if not existing_product:
            raise HTTPException(status_code=404, detail="Product not found")




        # Delete the Product
        query_delete_product = "DELETE FROM products WHERE ProductID = %s"
        db[0].execute(query_delete_product, (ProductID,))
        db[1].commit()




        return {"message": "Product deleted successfully"}
    except Exception as e:
        # Handle other exceptions if necessary
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database cursor
        db[0].close()


