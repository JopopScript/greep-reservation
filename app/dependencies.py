from fastapi import Depends
from sqlmodel.ext.asyncio.session import AsyncSession

from app.common.database import session
from app.service.account_service import AccountService
from app.service.schedule_service import ScheduleService
from app.service.schedule_slot_service import ScheduleSlotService
from app.storage.account_repository import AccountRepository
from app.storage.schedule_repository import ScheduleRepository
from app.storage.schedule_slot_repository import ScheduleSlotRepository


def account_service(sess: AsyncSession = Depends(session)):
    return AccountService(AccountRepository(sess), sess)


def schedule_service(sess: AsyncSession = Depends(session)):
    return ScheduleService(
        ScheduleRepository(sess), schedule_slot_service(sess), account_service(sess)
    )


def schedule_slot_service(sess: AsyncSession = Depends(session)):
    return ScheduleSlotService(ScheduleSlotRepository(sess))
