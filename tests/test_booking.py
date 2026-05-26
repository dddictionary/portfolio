import os
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch

import pytest

os.environ.setdefault("BOOKING_TOKEN_SECRET", "test-secret-do-not-use-in-prod")
os.environ.setdefault("OWNER_EMAIL", "owner@example.com")
os.environ.setdefault("URL", "http://test")

from app.services.tokens import (  # noqa: E402
    make_decide_token,
    make_verify_token,
    read_decide_token,
    read_verify_token,
)


def _future_iso(hours: int = 48) -> str:
    return (datetime.now() + timedelta(hours=hours)).strftime("%Y-%m-%dT%H:%M")


def _valid_form() -> dict:
    return {
        "name": "Jane Doe",
        "email": "jane@example.com",
        "title": "Quick chat",
        "description": "Wanted to catch up",
        "start_time": _future_iso(),
        "duration_min": "30",
        "timezone": "America/New_York",
    }


def test_token_roundtrip():
    assert read_verify_token(make_verify_token(42)) == 42
    assert read_decide_token(make_decide_token(42, "approve")) == (42, "approve")
    assert read_verify_token("garbage") is None
    assert read_decide_token("garbage") is None


@pytest.mark.asyncio
async def test_submit_booking_happy_path(client):
    with patch("app.routes.booking.turnstile.verify", new_callable=AsyncMock, return_value=True), \
         patch("app.routes.booking.count_recent_requests_by_ip", new_callable=AsyncMock, return_value=0), \
         patch("app.routes.booking.create_booking_request", new_callable=AsyncMock, return_value=123), \
         patch("app.routes.booking.email_service.send") as mock_send:
        resp = await client.post("/api/booking", data=_valid_form())
    assert resp.status_code == 200, resp.text
    assert resp.json()["status"] == "ok"
    mock_send.assert_called_once()
    assert mock_send.call_args.kwargs["to"] == "jane@example.com"


@pytest.mark.asyncio
async def test_submit_booking_honeypot_silently_drops(client):
    form = _valid_form()
    form["honeypot"] = "bot was here"
    with patch("app.routes.booking.email_service.send") as mock_send:
        resp = await client.post("/api/booking", data=form)
    assert resp.status_code == 200
    mock_send.assert_not_called()


@pytest.mark.asyncio
async def test_submit_booking_invalid_email(client):
    form = _valid_form()
    form["email"] = "not-an-email"
    resp = await client.post("/api/booking", data=form)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_submit_booking_invalid_duration(client):
    form = _valid_form()
    form["duration_min"] = "45"
    resp = await client.post("/api/booking", data=form)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_submit_booking_past_datetime(client):
    form = _valid_form()
    form["start_time"] = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%dT%H:%M")
    resp = await client.post("/api/booking", data=form)
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_submit_booking_rate_limited(client):
    with patch("app.routes.booking.turnstile.verify", new_callable=AsyncMock, return_value=True), \
         patch("app.routes.booking.count_recent_requests_by_ip", new_callable=AsyncMock, return_value=99):
        resp = await client.post("/api/booking", data=_valid_form())
    assert resp.status_code == 429


@pytest.mark.asyncio
async def test_submit_booking_turnstile_fails(client):
    with patch("app.routes.booking.turnstile.verify", new_callable=AsyncMock, return_value=False):
        resp = await client.post("/api/booking", data=_valid_form())
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_submit_booking_kill_switch(client):
    with patch.dict(os.environ, {"BOOKING_ENABLED": "false"}):
        resp = await client.post("/api/booking", data=_valid_form())
    assert resp.status_code == 503


@pytest.mark.asyncio
async def test_verify_booking_happy_path(client):
    booking = {
        "id": 7, "name": "Jane", "email": "j@x.com", "title": "Chat",
        "description": "hi", "start_time": datetime.now() + timedelta(days=1),
        "duration_min": 30, "timezone": "America/New_York", "ip": "1.2.3.4",
        "status": "pending_verification", "calendar_event_id": None,
    }
    token = make_verify_token(7)
    with patch("app.routes.booking.get_booking_request", new_callable=AsyncMock, return_value=booking), \
         patch("app.routes.booking.update_booking_status", new_callable=AsyncMock) as mock_upd, \
         patch("app.routes.booking.email_service.send") as mock_send:
        resp = await client.get(f"/booking/verify?token={token}")
    assert resp.status_code == 200
    mock_upd.assert_called_once_with(mock_upd.call_args.args[0], 7, "pending_approval")
    assert mock_send.call_args.kwargs["to"] == "owner@example.com"


@pytest.mark.asyncio
async def test_verify_booking_bad_token(client):
    resp = await client.get("/booking/verify?token=junk")
    assert resp.status_code == 400


@pytest.mark.asyncio
async def test_decide_approve_creates_event(client):
    booking = {
        "id": 9, "name": "Jane", "email": "j@x.com", "title": "Chat",
        "description": "hi", "start_time": datetime.now() + timedelta(days=1),
        "duration_min": 30, "timezone": "America/New_York", "ip": "1.2.3.4",
        "status": "pending_approval", "calendar_event_id": None,
    }
    token = make_decide_token(9, "approve")
    with patch("app.routes.booking.get_booking_request", new_callable=AsyncMock, return_value=booking), \
         patch("app.routes.booking.update_booking_status", new_callable=AsyncMock) as mock_upd, \
         patch("app.routes.booking.google_calendar.create_event", return_value="evt-123"), \
         patch("app.routes.booking.email_service.send") as mock_send:
        resp = await client.get(f"/booking/decide?token={token}")
    assert resp.status_code == 200
    assert mock_upd.call_args.kwargs["calendar_event_id"] == "evt-123"
    assert mock_send.call_args.kwargs["to"] == "j@x.com"


@pytest.mark.asyncio
async def test_decide_reject_notifies_requester(client):
    booking = {
        "id": 10, "name": "Jane", "email": "j@x.com", "title": "Chat",
        "description": "hi", "start_time": datetime.now() + timedelta(days=1),
        "duration_min": 30, "timezone": "America/New_York", "ip": "1.2.3.4",
        "status": "pending_approval", "calendar_event_id": None,
    }
    token = make_decide_token(10, "reject")
    with patch("app.routes.booking.get_booking_request", new_callable=AsyncMock, return_value=booking), \
         patch("app.routes.booking.update_booking_status", new_callable=AsyncMock), \
         patch("app.routes.booking.google_calendar.create_event") as mock_event, \
         patch("app.routes.booking.email_service.send") as mock_send:
        resp = await client.get(f"/booking/decide?token={token}")
    assert resp.status_code == 200
    mock_event.assert_not_called()
    assert mock_send.call_args.kwargs["to"] == "j@x.com"


@pytest.mark.asyncio
async def test_decide_already_decided(client):
    booking = {
        "id": 11, "name": "Jane", "email": "j@x.com", "title": "Chat",
        "description": "hi", "start_time": datetime.now() + timedelta(days=1),
        "duration_min": 30, "timezone": "America/New_York", "ip": "1.2.3.4",
        "status": "approved", "calendar_event_id": "evt-prev",
    }
    token = make_decide_token(11, "approve")
    with patch("app.routes.booking.get_booking_request", new_callable=AsyncMock, return_value=booking), \
         patch("app.routes.booking.google_calendar.create_event") as mock_event:
        resp = await client.get(f"/booking/decide?token={token}")
    assert resp.status_code == 200
    mock_event.assert_not_called()


@pytest.mark.asyncio
async def test_book_page_renders(client):
    resp = await client.get("/book")
    assert resp.status_code == 200
    assert "Book time" in resp.text
