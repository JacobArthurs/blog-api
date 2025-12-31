import re
from fastapi import HTTPException
from sqlalchemy.orm import Session

def slugify(text: str) -> str:
    """
    Convert a string to a URL-friendly slug.

    - Converts to lowercase
    - Replaces spaces and special characters with hyphens
    - Removes consecutive hyphens
    - Strips leading/trailing hyphens
    """
    text = text.lower()

    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_-]+', '-', text)

    text = text.strip('-')
    return text

def validate_unique_slug(slug: str, model, db: Session) -> None:
    """
    Validate that a slug is unique for a given model.

    Args:
        slug: The slug to validate
        model: The SQLAlchemy model to check against
        db: Database session

    Raises:
        HTTPException: 400 error if slug already exists
    """
    existing = db.query(model).filter(model.slug == slug).first()
    if existing:
        model_name = model.__name__
        raise HTTPException(
            status_code=400,
            detail=f"{model_name} with this slug already exists"
        )
