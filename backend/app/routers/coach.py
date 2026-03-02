from fastapi import APIRouter
from app.db.schemas.coach import CoachInput, CoachOutput
from app.service.coach import build_coach_output

router = APIRouter(prefix="/api/coach", tags=["coach"])


@router.post("/", response_model=CoachOutput)
async def coach(payload: CoachInput) -> CoachOutput:
    return build_coach_output(payload)
