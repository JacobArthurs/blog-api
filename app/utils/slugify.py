import re
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


def generate_unique_slug(base_slug: str, model, db: Session) -> str:
    """
    Generate a unique slug by appending a number if the slug already exists.

    Args:
        base_slug: The base slug to use
        model: The SQLAlchemy model to check against
        db: Database session

    Returns:
        A unique slug
    """
    slug = base_slug
    counter = 1

    while db.query(model).filter(model.slug == slug).first():
        slug = f"{base_slug}-{counter}"
        counter += 1

    return slug
