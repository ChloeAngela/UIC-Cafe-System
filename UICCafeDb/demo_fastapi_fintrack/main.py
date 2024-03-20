# main.py
from fastapi import FastAPI
from model.users import AccountRouter
from model.categories import ProductsRouter
from model.expenses import ExpensesRouter

app = FastAPI()

# Include CRUD routes from modules
app.include_router(AccountRouter, prefix="/api")
app.include_router(ProductsRouter, prefix="/api")
app.include_router(ExpensesRouter, prefix="/api")