from datetime import datetime, timedelta

import aiomysql


async def get_all_posts(pool: aiomysql.Pool) -> list[dict]:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT id, name, email, content, created_at FROM timelinepost ORDER BY created_at DESC"
            )
            rows = await cur.fetchall()
            for row in rows:
                row["created_at"] = row["created_at"].isoformat()
            return rows


async def create_post(pool: aiomysql.Pool, name: str, email: str, content: str) -> dict:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "INSERT INTO timelinepost (name, email, content) VALUES (%s, %s, %s)",
                (name, email, content),
            )
            post_id = cur.lastrowid
            await cur.execute(
                "SELECT id, name, email, content, created_at FROM timelinepost WHERE id = %s",
                (post_id,),
            )
            row = await cur.fetchone()
            row["created_at"] = row["created_at"].isoformat()
            return row


async def create_booking_request(
    pool: aiomysql.Pool,
    name: str,
    email: str,
    title: str,
    description: str,
    start_time: datetime,
    duration_min: int,
    timezone: str,
    ip: str,
) -> int:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                """
                INSERT INTO booking_requests
                    (name, email, title, description, start_time, duration_min, timezone, ip)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                """,
                (name, email, title, description, start_time, duration_min, timezone, ip),
            )
            return cur.lastrowid


async def get_booking_request(pool: aiomysql.Pool, booking_id: int) -> dict | None:
    async with pool.acquire() as conn:
        async with conn.cursor(aiomysql.DictCursor) as cur:
            await cur.execute(
                "SELECT * FROM booking_requests WHERE id = %s",
                (booking_id,),
            )
            return await cur.fetchone()


async def update_booking_status(
    pool: aiomysql.Pool,
    booking_id: int,
    status: str,
    calendar_event_id: str | None = None,
) -> None:
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            if calendar_event_id is not None:
                await cur.execute(
                    """
                    UPDATE booking_requests
                    SET status = %s, decided_at = %s, calendar_event_id = %s
                    WHERE id = %s
                    """,
                    (status, datetime.utcnow(), calendar_event_id, booking_id),
                )
            else:
                await cur.execute(
                    "UPDATE booking_requests SET status = %s, decided_at = %s WHERE id = %s",
                    (status, datetime.utcnow(), booking_id),
                )


async def count_recent_requests_by_ip(
    pool: aiomysql.Pool,
    ip: str,
    within_hours: int = 1,
) -> int:
    cutoff = datetime.utcnow() - timedelta(hours=within_hours)
    async with pool.acquire() as conn:
        async with conn.cursor() as cur:
            await cur.execute(
                "SELECT COUNT(*) FROM booking_requests WHERE ip = %s AND created_at >= %s",
                (ip, cutoff),
            )
            (count,) = await cur.fetchone()
            return count
