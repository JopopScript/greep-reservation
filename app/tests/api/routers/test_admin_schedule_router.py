from datetime import datetime

import pytest
from fastapi import status
from httpx import AsyncClient

from app.tests.conftest import Tokens
from app.tests.fixture_util import (
    pending_schedule,
    canceled_schedule,
    confirmed_schedule,
    datetime_to_str,
)


@pytest.mark.anyio
async def test_admin_get_all_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    await pending_schedule(client, tokens.first_token(), start_at, 50_000)
    await pending_schedule(client, tokens.second_token(), start_at, 50_000)

    response = await client.get(
        "/admin/schedules",
        headers=tokens.admin_token(),
        params={"page": 0, "page-size": 5},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["page_number"] == 0
    assert json["page_size"] == 5
    assert json["total"] == 2

    items = json["items"]
    assert items[0]["applicants"] == 50000
    assert items[0]["profile"] == tokens.first_profile()
    assert items[1]["applicants"] == 50000
    assert items[1]["profile"] == tokens.second_profile()


@pytest.mark.anyio
async def test_admin_change_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    body = {
        "name": "modified_name",
        "start_at": datetime_to_str(datetime(2200, 1, 1, 10, 0, 0)),
        "end_at": datetime_to_str(datetime(2200, 1, 1, 11, 0, 0)),
        "applicants": 1,
    }
    response = await client.put(
        f"/admin/schedules/{schedule_id}", headers=tokens.admin_token(), json=body
    )

    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        "id": schedule_id,
        "name": "modified_name",
        "start_at": datetime_to_str(datetime(2200, 1, 1, 10, 0, 0)),
        "end_at": datetime_to_str(datetime(2200, 1, 1, 11, 0, 0)),
        "applicants": 1,
        "status": "PENDING",
        "profile": tokens.first_profile(),
    }
    assert response.json() == expected_response


@pytest.mark.anyio
async def test_admin_schedule_pending_to_confirmed(
    client: AsyncClient, tokens: Tokens
) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    response = await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CONFIRMED"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["status"] == "CONFIRMED"


@pytest.mark.anyio
async def test_admin_schedule_canceled_to_confirmed(
    client: AsyncClient, tokens: Tokens
) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await canceled_schedule(client, tokens, start_at, 50_000)

    response = await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CONFIRMED"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["status"] == "CONFIRMED"


@pytest.mark.anyio
async def test_admin_schedule_pending_to_canceled(
    client: AsyncClient, tokens: Tokens
) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    response = await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CANCELED"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["status"] == "CANCELED"


@pytest.mark.anyio
async def test_admin_schedule_confirmed_to_canceled(
    client: AsyncClient, tokens: Tokens
) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await confirmed_schedule(client, tokens, start_at, 50_000)

    response = await client.put(
        f"/admin/schedules/{schedule_id}/status",
        headers=tokens.admin_token(),
        json={"status": "CANCELED"},
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json["status"] == "CANCELED"
