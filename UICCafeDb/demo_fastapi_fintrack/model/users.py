# model/users.py
from fastapi import Depends, HTTPException, APIRouter, Form
from .db import get_db
import bcrypt


AccountRouter = APIRouter(tags=["Accounts"])


#Get all
@AccountRouter.get("/accounts/", response_model=list)
async def read_users(
    db=Depends(get_db)
):
    query = "SELECT AccountTypeID, AccountID, FirstName, LastName FROM accounts"
    db[0].execute(query)
    accounts = [{
                    "AccountTypeID": accounts[0],
                    "AccountID": accounts[1],
                    "FirstName": accounts[2],
                    "LastName": accounts[3],
                } for accounts in db[0].fetchall()
                ]
    return accounts


#Get distinct from id
@AccountRouter.get("/accounts/{AccountID}", response_model=dict)
async def read_user(
    AccountID: int,
    db=Depends(get_db)
):
    query = "SELECT AccountID, FirstName, LastName FROM accounts WHERE AccountID = %s"
    db[0].execute(query, (AccountID,))
    accounts = db[0].fetchone()
    if accounts:
        return {"AccountID": accounts[0],
                "FirstName": accounts[1],
                "LastName": accounts[2],
               }
    raise HTTPException(status_code=404, detail="User not found")

#post
@AccountRouter.post("/accounts/", response_model=dict)
async def create_user(
    AccountTypeID: str = Form(...),
    Email: str = Form(...),
    FirstName: str = Form(...),
    LastName: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):  
# Hash the password using bcrypt
    hashed_password = password

    query = "INSERT INTO accounts (AccountTypeID, FirstName, LastName, password, Email) VALUES (%s, %s, %s, %s, %s)"
    db[0].execute(query, ( AccountTypeID, FirstName,  password, hashed_password, Email))




    # Retrieve the last inserted ID using LAST_INSERT_ID()
    db[0].execute("SELECT LAST_INSERT_ID()")
    new_user_id = db[0].fetchone()[0]
    db[1].commit()




    return {"AccountID": new_user_id, "FirstName": FirstName, "LastName": LastName}

#edit
@AccountRouter.put("/accounts/{AccountID}", response_model=dict)
async def update_user(
    AccountID: int,
    AccountTypeID: str = Form(...),
    Email: str = Form(...),
    FirstName: str = Form(...),
    LastName: str = Form(...),
    password: str = Form(...),
    db=Depends(get_db)
):
# Hash the password using bcrypt
    hashed_password = hash_password(password)




    # Update user information in the database
    query = "UPDATE accounts SET AccountTypeID = %s, Email = %s, FirstName = %s, LastName = %s, password = %s WHERE AccountID = %s"
    db[0].execute(query, (AccountTypeID, Email, FirstName, LastName, hashed_password, AccountID))




    # Check if the update was successful
    if db[0].rowcount > 0:
        db[1].commit()
        return {"message": "User updated successfully"}
   
    # If no rows were affected, user not found
    raise HTTPException(status_code=404, detail="User not found")


@AccountRouter.delete("/accounts/{AccountID}", response_model=dict)
async def delete_user(
    AccountID: int,
    db=Depends(get_db)
):
    try:
        # Check if the user exists
        query_check_user = "SELECT AccountID FROM accounts WHERE AccountID = %s"
        db[0].execute(query_check_user, (AccountID,))
        existing_user = db[0].fetchone()




        if not existing_user:
            raise HTTPException(status_code=404, detail="User not found")




        # Delete the user
        query_delete_user = "DELETE FROM accounts WHERE AccountID = %s"
        db[0].execute(query_delete_user, (AccountID,))
        db[1].commit()




        return {"message": "User deleted successfully"}
    except Exception as e:
        # Handle other exceptions if necessary
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
    finally:
        # Close the database cursor
        db[0].close()




# Password hashing function using bcrypt
def hash_password(password: str):
    # Generate a salt and hash the password
    salt = bcrypt.gensalt()
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_password.decode('utf-8')  # Decode bytes to string for storage