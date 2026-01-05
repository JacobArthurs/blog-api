from fastapi import APIRouter, Depends, Response
from sqlalchemy.orm import Session
import xml.etree.ElementTree as ET
from email.utils import format_datetime
from datetime import datetime, timezone

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


@router.get("/rss.xml")
def get_rss_feed(db: Session = Depends(get_db)):
    """Generate RSS 2.0 feed for all blog posts"""

    # Fetch all posts ordered by creation date
    posts = db.query(Post).order_by(Post.created_at.desc()).all()

    # Build RSS feed
    rss = ET.Element("rss", version="2.0", attrib={"xmlns:atom": "http://www.w3.org/2005/Atom"})
    channel = ET.SubElement(rss, "channel")

    # Channel metadata
    ET.SubElement(channel, "title").text = "Jacob Arthurs Blog"
    ET.SubElement(channel, "link").text = "https://blog.jacobarthurs.com/"
    ET.SubElement(channel, "description").text = "Latest posts from Jacob Arthurs Blog"
    ET.SubElement(channel, "language").text = "en-us"

    # Channel image
    image = ET.SubElement(channel, "image")
    ET.SubElement(image, "url").text = "https://blog.jacobarthurs.com/JA_logo.svg"
    ET.SubElement(image, "title").text = "Jacob Arthurs Blog"
    ET.SubElement(image, "link").text = "https://blog.jacobarthurs.com/"

    # Add atom:link for self-reference (RSS best practice)
    atom_link = ET.SubElement(channel, "{http://www.w3.org/2005/Atom}link")
    atom_link.set("href", "https://blog.jacobarthurs.com/rss.xml")
    atom_link.set("rel", "self")
    atom_link.set("type", "application/rss+xml")

    # Add lastBuildDate if posts exist
    if posts:
        most_recent = posts[0]
        last_build_date = format_datetime(most_recent.created_at.replace(tzinfo=timezone.utc))
        ET.SubElement(channel, "lastBuildDate").text = last_build_date

    # Add posts
    for post in posts:
        item = ET.SubElement(channel, "item")
        ET.SubElement(item, "title").text = post.title
        ET.SubElement(item, "link").text = f"https://blog.jacobarthurs.com/post/{post.slug}"
        ET.SubElement(item, "guid", isPermaLink="true").text = f"https://blog.jacobarthurs.com/post/{post.slug}"
        ET.SubElement(item, "description").text = post.tldr

        # Format pubDate according to RFC 822
        pub_date = format_datetime(post.created_at.replace(tzinfo=timezone.utc))
        ET.SubElement(item, "pubDate").text = pub_date

    xml_bytes = ET.tostring(rss, encoding="UTF-8", method="xml", xml_declaration=True)
    return Response(content=xml_bytes, media_type="application/rss+xml")
