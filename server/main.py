from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import TransactionCreate, TransactionResponse
from database import engine, session
import db_models
app = FastAPI()

def get_db():
    db = session()
    try:
        yield db
    finally: 
        db.close()

def get_current_user_id():
    # TEMPORARY mock
    return "test-user-123"


@app.get('/')
def greet():
    return "welcome!"

@app.post('/transaction', response_model = TransactionResponse)
def add_transaction(transaction: TransactionCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
        wallet = db.query(db_models.Wallet).filter(db_models.Wallet.id == transaction.wallet_id, db_models.Wallet.user_id == user_id).first()
        if not wallet:
             raise HTTPException(status_code=404, detail="Wallet not found")
        new_transaction = db_models.Transaction(**transaction.model_dump(), user_id = user_id)
        db.add(new_transaction)
        db.commit()
        db.refresh(new_transaction)
        return new_transaction