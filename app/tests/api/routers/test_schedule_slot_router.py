from datetime import datetime, timedelta

import pytest
from httpx import AsyncClient

from app.tests.conftest import Tokens
from app.tests.fixture_util import datetime_to_str


@pytest.mark.anyio
async def test_get_schedule_slot(client: AsyncClient, tokens: Tokens) -> None:
    start_at = datetime(2100, 1, 1, 0, 0, 0)
    end_at = start_at + timedelta(hours=2)
    query_param = {'start-at': datetime_to_str(start_at), 'end-at': datetime_to_str(end_at)}

    response = await client.get(
        '/schedule-slot',
        headers=tokens.first_token(),
        params=query_param
    )

    assert response.status_code == 200
    expected_response = {
        'start_at': '2100-01-01T00:00:00',
        'end_at': '2100-01-01T02:00:00',
        'items': [
            {
                'start_at': '2100-01-01T00:00:00',
                'end_at': '2100-01-01T01:00:00',
                'max_applicants': 50000,
                'confirmed_applicants': 0
            },
            {
                'start_at': '2100-01-01T01:00:00',
                'end_at': '2100-01-01T02:00:00',
                'max_applicants': 50000,
                'confirmed_applicants': 0
            },
        ]
    }
    assert response.json() == expected_response
