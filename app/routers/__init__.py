from fastapi import APIRouter

from app.routers.attendance import router as attendance_router
from app.routers.shifts import router as shifts_router
from app.routers.roster import router as roster_router
from app.routers.auth import router as auth_router

router = APIRouter()


router.include_router(attendance_router, prefix = '/v1/attendance')
router.include_router(shifts_router, prefix = '/v1/shifts')
router.include_router(roster_router, prefix = '/v1/rosters')
router.include_router(auth_router, prefix="/v1/user")