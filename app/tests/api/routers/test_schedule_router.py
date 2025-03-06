from datetime import datetime, timedelta

import pytest
from fastapi import status
from httpx import AsyncClient

from app.tests.conftest import Tokens
from app.tests.fixture_util import pending_schedule, schedule_create_request, confirmed_schedule, \
    datetime_to_str


@pytest.mark.anyio
async def test_customer_get_own_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    await pending_schedule(client, tokens.first_token(), start_at, 50_000)
    await pending_schedule(client, tokens.second_token(), start_at, 50_000)

    response = await client.get(
        '/schedules',
        headers=tokens.first_token(),
        params={
            'page': 0,
            'page-size': 5
        }
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['page_number'] == 0
    assert json['page_size'] == 5
    assert json['total'] == 1

    items = json['items']
    assert items[0]['applicants'] == 50000
    assert items[0]['profile'] == tokens.first_profile()


@pytest.mark.anyio
async def test_create_schedule_success(client: AsyncClient, tokens: Tokens) -> None:
    body = schedule_create_request(datetime(2101, 1, 1, 0, 0, 0), 1)
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert 'id' in json
    assert 'name' in json
    assert json['start_at'] == body['start_at']
    assert json['end_at'] == body['end_at']
    assert json['applicants'] == body['applicants']
    assert json['status'] == 'PENDING'
    assert 'profile' in json


@pytest.mark.anyio
async def test_create_schedule_before_3days(client: AsyncClient, tokens: Tokens) -> None:
    body = schedule_create_request(datetime(2000, 1, 1, 0, 0, 0), 1)
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json = response.json()
    assert json['code'] == 'INVALID_ARGUMENT'
    assert 'message' in json


@pytest.mark.anyio
async def test_create_schedule_50k_applicant(client: AsyncClient, tokens: Tokens) -> None:
    body = schedule_create_request(
        datetime(2103, 1, 1, 0, 0, 0),
        50_000
    )
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['applicants'] == 50_000


@pytest.mark.anyio
async def test_create_schedule_decreased_applicant_over(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2104, 1, 1, 0, 0, 0)
    await confirmed_schedule(client, tokens, start_at, 10_000)
    body = schedule_create_request(start_at, 40_001)
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.json()['code'] == 'INVALID_ARGUMENT'


@pytest.mark.anyio
async def test_create_schedule_decreased_applicant_under(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2104, 1, 1, 0, 0, 0)
    await confirmed_schedule(client, tokens, start_at, 10_000)

    body = schedule_create_request(start_at, 40_000)
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_200_OK
    assert response.json()['applicants'] == 40_000


@pytest.mark.anyio
async def test_create_multi_pending_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2104, 1, 1, 0, 0, 0)
    await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    body = schedule_create_request(start_at, 50_000)
    response = await client.post(
        '/schedules',
        headers=tokens.first_token(),
        json=body
    )
    assert response.status_code == status.HTTP_200_OK
    assert response.json()['applicants'] == 50_000


@pytest.mark.anyio
async def test_change_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    body = {
        'name': 'modified_name',
        'start_at': datetime_to_str(datetime(2200, 1, 1, 10, 0, 0)),
        'end_at': datetime_to_str(datetime(2200, 1, 1, 11, 0, 0)),
        'applicants': 1
    }
    response = await client.put(
        f'/schedules/{schedule_id}',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_200_OK
    expected_response = {
        'id': schedule_id,
        'name': 'modified_name',
        'start_at': datetime_to_str(datetime(2200, 1, 1, 10, 0, 0)),
        'end_at': datetime_to_str(datetime(2200, 1, 1, 11, 0, 0)),
        'applicants': 1,
        'status': 'PENDING',
        'profile': tokens.first_profile()
    }
    assert response.json() == expected_response


@pytest.mark.anyio
async def test_change_schedule_time_full(client: AsyncClient, tokens: Tokens) -> None:
    full_start_at = datetime(2100, 1, 1, 0, 0, 0)
    await confirmed_schedule(client, tokens, full_start_at, 50_000)
    late_start_at = datetime(2100, 1, 10, 0, 0, 0)
    schedule_id = await confirmed_schedule(client, tokens, late_start_at, 1)

    body = {
        'name': 'modified_name',
        'start_at': datetime_to_str(full_start_at),
        'end_at': datetime_to_str(full_start_at + timedelta(hours=1)),
        'applicants': 1
    }
    response = await client.put(
        f'/schedules/{schedule_id}',
        headers=tokens.first_token(),
        json=body
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json = response.json()
    assert json['code'] == 'INVALID_ARGUMENT'


@pytest.mark.anyio
async def test_cancel_schedule(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await pending_schedule(client, tokens.first_token(), start_at, 50_000)

    response = await client.put(
        f'/schedules/{schedule_id}/status',
        headers=tokens.first_token(),
        json={'status': 'CANCELED'}
    )

    assert response.status_code == status.HTTP_200_OK
    json = response.json()
    assert json['status'] == 'CANCELED'


@pytest.mark.anyio
async def test_cancel_schedule_fail(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    schedule_id = await confirmed_schedule(client, tokens, start_at, 50_000)

    response = await client.put(
        f'/schedules/{schedule_id}/status',
        headers=tokens.first_token(),
        json={'status': 'CANCELED'}
    )

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    json = response.json()
    assert json['code'] == 'INVALID_STATE'
