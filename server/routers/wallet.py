from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case
import datetime
import db_models
from models import WalletCreate, WalletResponse, WalletBalance, WalletCategoryBalance
from dependencies import get_db, get_current_user_id

router = APIRouter(prefix="/wallet", tags=["Wallet"])


@router.post("", response_model=WalletResponse)
def add_wallet(
    wallet: WalletCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    new_wallet = db_models.Wallet(**wallet.model_dump(), user_id=user_id)
    db.add(new_wallet)
    db.commit()
    db.refresh(new_wallet)
    return new_wallet


@router.get("", response_model=list[WalletResponse])
def get_all_wallets(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return (
        db.query(db_models.Wallet)
        .filter(db_models.Wallet.user_id == user_id)
        .all()
    )


@router.get("/{id}", response_model=WalletResponse)
def get_wallet(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    return wallet


@router.put("/{id}", response_model=WalletResponse)
def update_wallet(
    id: str,
    wallet: WalletCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    db_wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not db_wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    db_wallet.name = wallet.name
    db.commit()
    db.refresh(db_wallet)
    return db_wallet


@router.delete("/{id}")
def delete_wallet(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    db.delete(wallet)
    db.commit()
    return {"detail": "Wallet deleted successfully"}


@router.get("/{id}/balance", response_model=WalletBalance)
def get_wallet_balance(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    balance = (
        db.query(
            func.coalesce(
                func.sum(
                    case(
                        (db_models.Transaction.type == "income", db_models.Transaction.amount),
                        (db_models.Transaction.type == "expense", -db_models.Transaction.amount),
                        else_=0,
                    )
                ),
                0,
            )
        )
        .filter(
            db_models.Transaction.wallet_id == id,
            db_models.Transaction.user_id == user_id,
        )
        .scalar()
    )

    return {"wallet_id": id, "balance": balance}


@router.get("/{id}/category-balance", response_model=WalletCategoryBalance)
def get_wallet_category_balance(
    id: str,
    from_date: datetime.datetime | None = None,
    to_date: datetime.datetime | None = None,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    wallet = (
        db.query(db_models.Wallet)
        .filter(
            db_models.Wallet.id == id,
            db_models.Wallet.user_id == user_id,
        )
        .first()
    )

    if not wallet:
        raise HTTPException(status_code=404, detail="Wallet not found")

    query = (
        db.query(
            db_models.Transaction.category_id.label("category_id"),
            db_models.Category.name.label("category_name"),
            func.coalesce(
                func.sum(
                    case(
                        (db_models.Transaction.type == "income", db_models.Transaction.amount),
                        (db_models.Transaction.type == "expense", -db_models.Transaction.amount),
                        else_=0,
                    )
                ),
                0,
            ).label("balance"),
        )
        .outerjoin(
            db_models.Category,
            db_models.Transaction.category_id == db_models.Category.id,
        )
        .filter(
            db_models.Transaction.wallet_id == id,
            db_models.Transaction.user_id == user_id,
        )
        .group_by(db_models.Transaction.category_id, db_models.Category.name)
    )

    if from_date:
        query = query.filter(db_models.Transaction.transaction_date >= from_date)

    if to_date:
        query = query.filter(db_models.Transaction.transaction_date <= to_date)

    rows = query.all()

    balances = [
        {
            "category_id": row.category_id,
            "category_name": row.category_name or "Uncategorized",
            "balance": row.balance,
        }
        for row in rows
    ]

    return {"wallet_id": id, "balances": balances}
