from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.utils.auth import verify_admin

from ..db import get_db
from ..models import Tag
from ..schemas import TagResponse, TagCreate, TagUpdate
from ..utils import slugify, validate_unique_slug

router = APIRouter(
    prefix="/tags",
    tags=["tags"]
)

@router.get("/", response_model=List[TagResponse])
def get_tags(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Get all tags with pagination"""
    tags = db.query(Tag).offset(skip).limit(limit).all()
    return tags

@router.get("/{tag_id}", response_model=TagResponse)
def get_tag(tag_id: int, db: Session = Depends(get_db)):
    """Get a tag by ID"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.get("/slug/{slug}", response_model=TagResponse)
def get_tag_by_slug(slug: str, db: Session = Depends(get_db)):
    """Get a tag by slug"""
    tag = db.query(Tag).filter(Tag.slug == slug).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")
    return tag

@router.post("/", response_model=TagResponse, status_code=201)
def create_tag(tag_data: TagCreate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Create a tag"""
    if tag_data.slug:
        slug = tag_data.slug
    else:
        slug = slugify(tag_data.name)

    validate_unique_slug(slug, Tag, db)

    new_tag = Tag(
        name=tag_data.name,
        slug=slug
    )

    db.add(new_tag)
    db.commit()
    db.refresh(new_tag)

    return new_tag

@router.patch("/{tag_id}", response_model=TagResponse)
def update_tag(tag_id: int, tag_data: TagUpdate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Update a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag_data.name is not None:
        tag.name = tag_data.name

    if tag_data.slug is not None:
        if tag_data.slug != tag.slug:
            validate_unique_slug(tag_data.slug, Tag, db)
        tag.slug = tag_data.slug
    elif tag_data.name is not None:
        new_slug = slugify(tag_data.name)
        if new_slug != tag.slug:
            validate_unique_slug(new_slug, Tag, db)
        tag.slug = new_slug

    db.commit()
    db.refresh(tag)

    return tag

@router.delete("/{tag_id}", status_code=204)
def delete_tag(tag_id: int, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Delete a tag"""
    tag = db.query(Tag).filter(Tag.id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    db.delete(tag)
    db.commit()

    return None
