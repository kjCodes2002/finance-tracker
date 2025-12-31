from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
import db_models
from models import TransactionCreate, TransactionResponse
from dependencies import get_db, get_current_user_id

router = APIRouter(prefix="/transaction", tags=["Transaction"])


@router.post("", response_model=TransactionResponse)
def add_transaction(
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == transaction.wallet_id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    new_transaction = db_models.Transaction(
        **transaction.model_dump(),
        user_id=user_id,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)
    return new_transaction


@router.get("", response_model=List[TransactionResponse])
def get_all_transactions(
    wallet_id: Optional[str] = None,
    category_id: Optional[str] = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    query = (
        db.query(db_models.Transaction)
        .filter(db_models.Transaction.user_id == user_id)
    )

    if wallet_id:
        query = query.filter(db_models.Transaction.wallet_id == wallet_id)

    if category_id:
        query = query.filter(db_models.Transaction.category_id == category_id)

    return query.all()


@router.get("/{id}", response_model=TransactionResponse)
def get_transaction(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    transaction = (
        db.query(db_models.Transaction)
        .filter(
            db_models.Transaction.id == id,
            db_models.Transaction.user_id == user_id,
        )
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return transaction


@router.put("/{id}", response_model=TransactionResponse)
def update_transaction(
    id: str,
    transaction: TransactionCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == transaction.wallet_id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    if transaction.category_id:
        category = (
            db.query(db_models.Category)
            .filter(
                db_models.Category.id == transaction.category_id,
                db_models.Category.user_id == user_id,
            )
            .first()
        )
        if not category:
            raise HTTPException(status_code=404, detail="Category not found")

    db_transaction = (
        db.query(db_models.Transaction)
        .filter(
            db_models.Transaction.id == id,
            db_models.Transaction.user_id == user_id,
        )
        .first()
    )

    if not db_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db_transaction.wallet_id = transaction.wallet_id
    db_transaction.category_id = transaction.category_id
    db_transaction.amount = transaction.amount
    db_transaction.type = transaction.type
    db_transaction.description = transaction.description
    db_transaction.transaction_date = transaction.transaction_date

    db.commit()
    db.refresh(db_transaction)
    return db_transaction


@router.delete("/{id}")
def delete_transaction(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    transaction = (
        db.query(db_models.Transaction)
        .filter(
            db_models.Transaction.id == id,
            db_models.Transaction.user_id == user_id,
        )
        .first()
    )

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")

    db.delete(transaction)
    db.commit()
    return {"detail": "Transaction deleted successfully"}
