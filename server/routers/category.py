from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import db_models
from models import CategoryCreate, CategoryResponse
from dependencies import get_db, get_current_user_id

router = APIRouter(prefix="/category", tags=["Category"])


@router.post("", response_model=CategoryResponse)
def add_category(
    category: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    db_category = db_models.Category(**category.model_dump(), user_id=user_id)
    db.add(db_category)

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists",
        )

    db.refresh(db_category)
    return db_category


@router.get("", response_model=list[CategoryResponse])
def get_all_categories(
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    return (
        db.query(db_models.Category)
        .filter(db_models.Category.user_id == user_id)
        .all()
    )


@router.get("/{id}", response_model=CategoryResponse)
def get_category(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    category = (
        db.query(db_models.Category)
        .filter(
            db_models.Category.id == id,
            db_models.Category.user_id == user_id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    return category


@router.put("/{id}", response_model=CategoryResponse)
def update_category(
    id: str,
    category: CategoryCreate,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    db_category = (
        db.query(db_models.Category)
        .filter(
            db_models.Category.id == id,
            db_models.Category.user_id == user_id,
        )
        .first()
    )

    if not db_category:
        raise HTTPException(status_code=404, detail="Category not found")

    db_category.name = category.name

    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=400,
            detail="Category with this name already exists",
        )

    db.refresh(db_category)
    return db_category


@router.delete("/{id}")
def delete_category(
    id: str,
    db: Session = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    category = (
        db.query(db_models.Category)
        .filter(
            db_models.Category.id == id,
            db_models.Category.user_id == user_id,
        )
        .first()
    )

    if not category:
        raise HTTPException(status_code=404, detail="Category not found")

    db.delete(category)
    db.commit()
    return {"detail": "Category deleted successfully"}
