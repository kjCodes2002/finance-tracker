from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from models import TransactionCreate, TransactionResponse, WalletCreate, WalletResponse
from database import engine, session
from typing import List
from pydantic import Optional
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

@app.get('/transaction', response_model = List[TransactionResponse])
def get_all_transactions(wallet_id: Optional[str] = None, category_id: Optional[str] = None, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
     query = db.query(db_models.Transaction).filter(db_models.Transaction.user_id == user_id)
     if wallet_id:
          query = query.filter(db_models.Transaction.wallet_id == wallet_id)
    
     if category_id:
          query = query.filter(db_models.Transaction.category_id == category_id)

     return query.all()
     

@app.get('/transaction/{id}', response_model = TransactionResponse)
def get_transaction(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     db_transaction = db.query(db_models.Transaction).filter(db_models.Transaction.id == id, db_models.Transaction.user_id == user_id).first()
     if not db_transaction:
          raise HTTPException(status_code=404, detail="Transaction not found")
     return db_transaction

@app.delete('/transaction/{id}')
def delete_transaction(id: str, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
     db_transactioin = db.query(db_models.Transaction).filter(db_models.Transaction.id == id, db_models.Transaction.user_id == user_id).first()
     if not db_transactioin:
          raise HTTPException(status_code = 404, detail= "Transaction not found")
     db.delete(db_transactioin)
     db.commit()
     return {"detail": "Transaction deleted successfully"}

@app.put('/transaction/{id}', response_model = TransactionResponse)
def update_transaction(id: str, transaction: TransactionCreate, user_id: str = Depends(get_current_user_id), db: Session = Depends(get_db)):
     wallet = db.query(db_models.Wallet).filter(db_models.Wallet.id == transaction.wallet_id, db_models.Wallet.user_id == user_id).first()
     if not wallet:
          raise HTTPException(status_code = 404, detail = "Wallet not found")
     if transaction.category_id:
          category = db.query(db_models.Category).filter(db_models.Category.id == transaction.category_id, db_models.Category.user_id == user_id).first()
          if not category:
               raise HTTPException(status_code = 404, detail= "Category not found")
     db_transaction = db.query(db_models.Transaction).filter(db_models.Transaction.id == id, db_models.Transaction.user_id == user_id).first()
     if not db_transaction:
          raise HTTPException(status_code = 404, detail="Transaction not found")
     db_transaction.wallet_id = transaction.wallet_id
     db_transaction.category_id = transaction.category_id
     db_transaction.amount = transaction.amount
     db_transaction.type = transaction.type
     db_transaction.description = transaction.description
     db_transaction.transaction_date = transaction.transaction_date
     db.commit()
     db.refresh(db_transaction)
     return db_transaction

@app.post('/wallet', response_model = WalletResponse)
def add_wallet(wallet: WalletCreate, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     new_wallet = db_models.Wallet(**wallet.model_dump(), user_id = user_id)
     db.add(new_wallet)
     db.commit()
     db.refresh(new_wallet)
     return new_wallet

@app.get('/wallet', response_model = List[WalletResponse])
def get_all_wallets(db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     query = db.query(db_models.Wallet).filter(db_models.Wallet.user_id == user_id)
     return query.all()

@app.get('/wallet/{id}', response_model = WalletResponse)
def get_wallet(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     db_wallet = db.query(db_models.Wallet).filter(db_models.Wallet.id == id, db_models.Wallet.user_id == user_id).first()
     if not db_wallet:
          raise HTTPException(status_code = 404, detail="Wallet not found")
     return db_wallet

@app.put('/wallet/{id}', response_model = WalletResponse)
def update_wallet(wallet: WalletCreate, id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     db_wallet = db.query(db_models.Wallet).filter(db_models.Wallet.id == id, db_models.Wallet.user_id == user_id).first()
     if not db_wallet:
          raise HTTPException(status_code = 404, detail="Wallet not found")
     db_wallet.name = wallet.name
     db.commit()
     db.refresh(db_wallet)
     return db_wallet

@app.delete('/wallet/{id}')
def delete_wallet(id: str, db: Session = Depends(get_db), user_id: str = Depends(get_current_user_id)):
     db_wallet = db.query(db_models.Wallet).filter(db_models.Wallet.id == id, db_models.Wallet.user_id == user_id).first()
     if not db_wallet:
          raise HTTPException(status_code = 404, detail="Wallet not found")
     db.delete(db_wallet)
     db.commit()
     return {"detail": "Wallet deleted successfully"}



