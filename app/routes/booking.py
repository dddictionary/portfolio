import logging
import os
from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import HTMLResponse

from app.database import get_pool
from app.models import (
    count_recent_requests_by_ip,
    create_booking_request,
    get_booking_request,
    update_booking_status,
)
from app.services import email as email_service
from app.services import google_calendar, turnstile
from app.services.tokens import (
    make_decide_token,
    make_verify_token,
    read_decide_token,
    read_verify_token,
)

logger = logging.getLogger("backend")
router = APIRouter()

ALLOWED_DURATIONS = {15, 30, 60}
RATE_LIMIT_PER_HOUR = 5


def _enabled() -> bool:
    return os.environ.get("BOOKING_ENABLED", "true").lower() == "true"


def _base_url() -> str:
    return os.environ.get("URL", "http://localhost:5000").rstrip("/")


def _client_ip(request: Request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "unknown"


def _format_local(dt: datetime, tz: str) -> str:
    try:
        return dt.astimezone(ZoneInfo(tz)).strftime("%A, %B %d %Y at %I:%M %p %Z")
    except ZoneInfoNotFoundError:
        return dt.isoformat()


@router.post("/api/booking")
async def submit_booking(
    request: Request,
    name: str = Form(...),
    email: str = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    start_time: str = Form(...),
    duration_min: int = Form(...),
    timezone: str = Form(...),
    honeypot: str = Form(default=""),
    turnstile_token: str = Form(default="", alias="cf-turnstile-response"),
):
    if not _enabled():
        raise HTTPException(status_code=503, detail="Booking is temporarily disabled")
    if honeypot:
        logger.info("Booking honeypot triggered ip=%s", _client_ip(request))
        return {"status": "ok"}

    name = name.strip()
    email = email.strip().lower()
    title = title.strip()
    description = description.strip()

    if not name or not title or not description:
        raise HTTPException(status_code=400, detail="Missing required fields")
    if "@" not in email or "." not in email.split("@")[-1]:
        raise HTTPException(status_code=400, detail="Invalid email")
    if duration_min not in ALLOWED_DURATIONS:
        raise HTTPException(status_code=400, detail="Invalid duration")
    try:
        start_dt = datetime.fromisoformat(start_time)
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid datetime")
    if start_dt < datetime.now():
        raise HTTPException(status_code=400, detail="Start time must be in the future")
    try:
        ZoneInfo(timezone)
    except ZoneInfoNotFoundError:
        raise HTTPException(status_code=400, detail="Invalid timezone")

    ip = _client_ip(request)
    if not await turnstile.verify(turnstile_token, ip):
        raise HTTPException(status_code=400, detail="Captcha failed")

    pool = await get_pool()
    recent = await count_recent_requests_by_ip(pool, ip)
    if recent >= RATE_LIMIT_PER_HOUR:
        raise HTTPException(status_code=429, detail="Too many requests")

    booking_id = await create_booking_request(
        pool, name, email, title, description, start_dt, duration_min, timezone, ip,
    )

    verify_url = f"{_base_url()}/booking/verify?token={make_verify_token(booking_id)}"
    email_service.send(
        to=email,
        subject="Confirm your booking request",
        html=email_service.render(
            "verify.html",
            name=name,
            title=title,
            duration_min=duration_min,
            start_local=_format_local(start_dt, timezone),
            verify_url=verify_url,
        ),
    )
    return {"status": "ok", "message": "Check your email to confirm."}


@router.get("/booking/verify", response_class=HTMLResponse)
async def verify_booking(token: str):
    booking_id = read_verify_token(token)
    if booking_id is None:
        return HTMLResponse("<h1>Link expired or invalid.</h1>", status_code=400)

    pool = await get_pool()
    booking = await get_booking_request(pool, booking_id)
    if booking is None:
        return HTMLResponse("<h1>Not found.</h1>", status_code=404)
    if booking["status"] != "pending_verification":
        return HTMLResponse("<h1>Already confirmed. We'll be in touch.</h1>")

    await update_booking_status(pool, booking_id, "pending_approval")

    approve_url = f"{_base_url()}/booking/decide?token={make_decide_token(booking_id, 'approve')}"
    reject_url = f"{_base_url()}/booking/decide?token={make_decide_token(booking_id, 'reject')}"
    email_service.send(
        to=os.environ["OWNER_EMAIL"],
        subject=f"Booking request from {booking['name']}",
        html=email_service.render(
            "approval_request.html",
            name=booking["name"],
            email=booking["email"],
            title=booking["title"],
            description=booking["description"],
            start_local=_format_local(booking["start_time"], booking["timezone"]),
            duration_min=booking["duration_min"],
            timezone=booking["timezone"],
            ip=booking["ip"],
            approve_url=approve_url,
            reject_url=reject_url,
        ),
    )
    return HTMLResponse("<h1>Confirmed. Abrar will review and reply.</h1>")


@router.get("/booking/decide", response_class=HTMLResponse)
async def decide_booking(token: str):
    parsed = read_decide_token(token)
    if parsed is None:
        return HTMLResponse("<h1>Link expired or invalid.</h1>", status_code=400)
    booking_id, action = parsed
    if action not in {"approve", "reject"}:
        return HTMLResponse("<h1>Invalid action.</h1>", status_code=400)

    pool = await get_pool()
    booking = await get_booking_request(pool, booking_id)
    if booking is None:
        return HTMLResponse("<h1>Not found.</h1>", status_code=404)
    if booking["status"] not in {"pending_approval", "pending_verification"}:
        return HTMLResponse(f"<h1>Already {booking['status']}.</h1>")

    if action == "reject":
        await update_booking_status(pool, booking_id, "rejected")
        email_service.send(
            to=booking["email"],
            subject="Re: your booking request",
            html=email_service.render(
                "rejected.html", name=booking["name"], title=booking["title"]
            ),
        )
        return HTMLResponse("<h1>Rejected. Requester notified.</h1>")

    event_id = google_calendar.create_event(
        summary=f"{booking['title']} (with {booking['name']})",
        description=f"From {booking['name']} <{booking['email']}>\n\n{booking['description']}",
        start=booking["start_time"],
        duration_min=booking["duration_min"],
        timezone=booking["timezone"],
        attendee_email=booking["email"],
        attendee_name=booking["name"],
    )
    await update_booking_status(pool, booking_id, "approved", calendar_event_id=event_id)
    email_service.send(
        to=booking["email"],
        subject="Booking confirmed",
        html=email_service.render(
            "approved.html",
            name=booking["name"],
            title=booking["title"],
            duration_min=booking["duration_min"],
            start_local=_format_local(booking["start_time"], booking["timezone"]),
        ),
    )
    return HTMLResponse("<h1>Approved. Calendar invite sent.</h1>")
