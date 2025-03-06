from fastapi import APIRouter, status
from fastapi.responses import Response

router = APIRouter(tags=['health-check'])


@router.get('/health-check', status_code=status.HTTP_200_OK)
async def health_check() -> Response:
    return Response(status_code=status.HTTP_200_OK)
