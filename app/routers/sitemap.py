from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET

from ..db import get_db
from ..models import Post, Tag

router = APIRouter(
    tags=["sitemap"]
)

@router.get("/sitemap.xml")
def get_sitemap(db: Session = Depends(get_db)):
    """Generate XML sitemap for all posts and tags"""
    
    # Fetch all posts and tags
    posts = db.query(Post).all()
    tags = db.query(Tag).all()
    
    # Build XML sitemap
    urlset = ET.Element("urlset", xmlns="http://www.sitemaps.org/schemas/sitemap/0.9")
    
    # Homepage
    url = ET.SubElement(urlset, "url")
    ET.SubElement(url, "loc").text = "https://blog.jacobarthurs.com/"
    if posts:
        most_recent = max(posts, key=lambda p: p.created_at)
        ET.SubElement(url, "lastmod").text = most_recent.created_at.strftime("%Y-%m-%d")
    ET.SubElement(url, "changefreq").text = "weekly"
    ET.SubElement(url, "priority").text = "1.0"
    
    # Add posts
    for post in posts:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"https://blog.jacobarthurs.com/post/{post.slug}"
        ET.SubElement(url, "lastmod").text = post.updated_at.strftime("%Y-%m-%d")
        ET.SubElement(url, "changefreq").text = "monthly"
        ET.SubElement(url, "priority").text = "0.8"
    
    # Add tags
    for tag in tags:
        url = ET.SubElement(urlset, "url")
        ET.SubElement(url, "loc").text = f"https://blog.jacobarthurs.com/tag/{tag.slug}"
        ET.SubElement(url, "lastmod").text = tag.updated_at.strftime("%Y-%m-%d")
        ET.SubElement(url, "changefreq").text = "monthly"
        ET.SubElement(url, "priority").text = "0.6"
    
    xml_bytes = ET.tostring(urlset, encoding="UTF-8", method="xml", xml_declaration=True)
    return Response(content=xml_bytes, media_type="application/xml")
