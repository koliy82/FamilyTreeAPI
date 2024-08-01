from fastapi import APIRouter

router = APIRouter(
    prefix="/tree"
)


@router.get("/")
async def root():
    return "tree"
