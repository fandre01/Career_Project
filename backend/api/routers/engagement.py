import hashlib
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, Request, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from backend.db.database import get_db
from backend.models.engagement import Comment, PageView
from backend.schemas.engagement import (
    CommentCreate, CommentResponse, PaginatedComments,
    ViewCountResponse, ViewTrackRequest,
)

router = APIRouter(prefix="/api/engagement", tags=["engagement"])


def _hash_ip(ip: str) -> str:
    return hashlib.sha256(ip.encode()).hexdigest()


def _visitor_hash(request: Request) -> str:
    ip = request.client.host if request.client else "unknown"
    ua = request.headers.get("user-agent", "")
    return hashlib.sha256(f"{ip}:{ua}".encode()).hexdigest()


@router.post("/comments", response_model=CommentResponse)
def create_comment(body: CommentCreate, request: Request, db: Session = Depends(get_db)):
    ip = request.client.host if request.client else "unknown"
    ip_h = _hash_ip(ip)

    # Rate limit: 1 comment per 60 seconds per IP
    cutoff = datetime.now(timezone.utc) - timedelta(seconds=60)
    recent = db.query(Comment).filter(
        Comment.ip_hash == ip_h,
        Comment.created_at >= cutoff,
    ).first()
    if recent:
        raise HTTPException(status_code=429, detail="Please wait before posting another comment.")

    comment = Comment(
        name=body.name.strip(),
        message=body.message.strip(),
        ip_hash=ip_h,
    )
    db.add(comment)
    db.commit()
    db.refresh(comment)
    return comment


@router.get("/comments", response_model=PaginatedComments)
def list_comments(page: int = 1, page_size: int = 20, db: Session = Depends(get_db)):
    total = db.query(func.count(Comment.id)).scalar() or 0
    items = (
        db.query(Comment)
        .order_by(Comment.created_at.desc())
        .offset((page - 1) * page_size)
        .limit(page_size)
        .all()
    )
    return PaginatedComments(items=items, total=total, page=page, page_size=page_size)


@router.post("/views/track")
def track_view(body: ViewTrackRequest, request: Request, db: Session = Depends(get_db)):
    vh = _visitor_hash(request)
    view = PageView(visitor_hash=vh, page=body.page)
    db.add(view)
    db.commit()
    return {"status": "ok"}


@router.get("/views/stats", response_model=ViewCountResponse)
def view_stats(db: Session = Depends(get_db)):
    total_views = db.query(func.count(PageView.id)).scalar() or 0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    today_views = db.query(func.count(PageView.id)).filter(
        PageView.created_at >= today_start,
    ).scalar() or 0

    unique_visitors = db.query(func.count(distinct(PageView.visitor_hash))).scalar() or 0

    return ViewCountResponse(
        total_views=total_views,
        today_views=today_views,
        unique_visitors=unique_visitors,
    )
