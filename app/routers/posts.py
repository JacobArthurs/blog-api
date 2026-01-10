from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_
from typing import List
from slowapi.util import get_remote_address
from cachetools import TTLCache

from app.utils.auth import verify_admin

from ..db import get_db
from ..models import Post, Tag
from ..schemas import PostResponse, PostCreate, PostUpdate
from ..utils import slugify, validate_unique_slug, calculate_read_time

view_cache = TTLCache(maxsize=10000, ttl=3600)

router = APIRouter(
    prefix="/posts",
    tags=["posts"]
)

@router.get("/", response_model=List[PostResponse])
def get_posts(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all posts with pagination, excluding featured post"""
    posts = db.query(Post).options(joinedload(Post.tags)).filter(Post.featured == False).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/featured", response_model=PostResponse)
def get_featured_post(db: Session = Depends(get_db)):
    """Get the featured post"""
    post = db.query(Post).options(joinedload(Post.tags)).filter(Post.featured == True).first()
    if not post:
        raise HTTPException(status_code=404, detail="No featured post found")
    return post

@router.get("/tag/{tag_slug}", response_model=List[PostResponse])
def get_posts_by_tag(tag_slug: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get all posts for a specific tag"""
    tag = db.query(Tag).filter(Tag.slug == tag_slug).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    posts = db.query(Post).options(joinedload(Post.tags)).join(Post.tags).filter(Tag.id == tag.id).order_by(Post.created_at.desc()).offset(skip).limit(limit).all()
    return posts

@router.get("/{post_id}", response_model=PostResponse)
def get_post(post_id: int, db: Session = Depends(get_db)):
    """Get a post by ID"""
    post = db.query(Post).options(joinedload(Post.tags)).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    return post

@router.get("/slug/{slug}", response_model=PostResponse)
def get_post_by_slug(request: Request, slug: str, db: Session = Depends(get_db)):
    """Get a post by slug and increment view count"""
    post = db.query(Post).options(joinedload(Post.tags)).filter(Post.slug == slug).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    client_ip = get_remote_address(request)
    cache_key = f"{post.id}:{client_ip}"

    if cache_key not in view_cache:
        post.view_count += 1
        db.commit()
        db.refresh(post)
        view_cache[cache_key] = True

    return post

@router.post("/", response_model=PostResponse, status_code=201)
def create_post(post_data: PostCreate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Create a post"""
    if post_data.slug:
        slug = post_data.slug
    else:
        slug = slugify(post_data.title)

    validate_unique_slug(slug, Post, db)

    if post_data.featured:
        db.query(Post).filter(Post.featured == True).update({Post.featured: False})

    read_time = calculate_read_time(post_data.content)

    new_post = Post(
        title=post_data.title,
        slug=slug,
        summary=post_data.summary,
        content=post_data.content,
        read_time_minutes=read_time,
        featured=post_data.featured
    )

    if post_data.tag_ids:
        tags = db.query(Tag).filter(Tag.id.in_(post_data.tag_ids)).all()
        if len(tags) != len(post_data.tag_ids):
            raise HTTPException(status_code=404, detail="One or more tags not found")
        new_post.tags = tags

    db.add(new_post)
    db.commit()
    db.refresh(new_post)

    return new_post

@router.patch("/{post_id}", response_model=PostResponse)
def update_post(post_id: int, post_data: PostUpdate, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Update a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    if post_data.title is not None:
        post.title = post_data.title

    if post_data.slug is not None:
        if post_data.slug != post.slug:
            validate_unique_slug(post_data.slug, Post, db)
            post.slug = post_data.slug
    elif post_data.title is not None:
        new_slug = slugify(post_data.title)
        if new_slug != post.slug:
            validate_unique_slug(new_slug, Post, db)
            post.slug = new_slug

    if post_data.summary is not None:
        post.summary = post_data.summary

    if post_data.content is not None:
        post.content = post_data.content
        post.read_time_minutes = calculate_read_time(post_data.content)

    if post_data.view_count is not None:
        post.view_count = post_data.view_count

    if post_data.featured is not None:
        if post_data.featured:
            db.query(Post).filter(
                and_(
                    Post.featured == True,
                    Post.id != post_id
                )
            ).update({Post.featured: False})
        post.featured = post_data.featured

    if post_data.tag_ids is not None:
        if post_data.tag_ids:
            tags = db.query(Tag).filter(Tag.id.in_(post_data.tag_ids)).all()
            if len(tags) != len(post_data.tag_ids):
                raise HTTPException(status_code=404, detail="One or more tags not found")
            post.tags = tags
        else:
            post.tags = []

    db.commit()
    db.refresh(post)

    return post

@router.delete("/{post_id}", status_code=204)
def delete_post(post_id: int, db: Session = Depends(get_db), _ = Depends(verify_admin)):
    """Delete a post"""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    db.delete(post)
    db.commit()

    return None
