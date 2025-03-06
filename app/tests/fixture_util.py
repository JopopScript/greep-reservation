from datetime import datetime, timedelta
from typing import Any

from httpx import AsyncClient

from app.tests.conftest import Tokens


async def confirmed_schedule(
    client: AsyncClient, tokens: Tokens, start_at: datetime, applicants: int
) -> str:
    schedule_id = await pending_schedule(
        client, tokens.first_token(), start_at, applicants
    )
    await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CONFIRMED"},
    )
    return schedule_id


async def canceled_schedule(
    client: AsyncClient, tokens: Tokens, start_at: datetime, applicants: int
) -> str:
    schedule_id = await pending_schedule(
        client, tokens.first_token(), start_at, applicants
    )
    await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CANCELED"},
    )
    return schedule_id


async def pending_schedule(
    client: AsyncClient, token: dict[str, str], start_at: datetime, applicants: int
) -> str:
    response = await client.post(
        "/schedules", headers=token, json=schedule_create_request(start_at, applicants)
    )
    return response.json()["id"]


def schedule_create_request(start_at: datetime, applicants: int) -> dict[str, Any]:
    end_at = start_at + timedelta(hours=1)
    return {
        "name": "test",
        "start_at": datetime_to_str(start_at),
        "end_at": datetime_to_str(end_at),
        "applicants": applicants,
    }


def three_after_time() -> datetime:
    three_after_days = datetime.now() + timedelta(days=3)
    return three_after_days.replace(minute=0, second=0, microsecond=0)


def datetime_to_str(d: datetime) -> str:
    return d.strftime("%Y-%m-%dT%H:%M:%S")
