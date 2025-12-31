from fastapi import FastAPI
from routers import transaction, wallet, category

app = FastAPI()

@app.get("/")
def greet():
    return "welcome!"

app.include_router(transaction.router)
app.include_router(wallet.router)
app.include_router(category.router)
