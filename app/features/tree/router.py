from fastapi import APIRouter, HTTPException
from starlette.responses import PlainTextResponse

from app.features.brak.model import get_brak_by_user_id
from app.features.tree.model import FamilyTree

router = APIRouter(
    prefix="/tree",
    tags=["tree"]
)


@router.get("/")
async def root():
    return "tree"


@router.get("/text/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    brak = get_brak_by_user_id(user_id)
    if not brak:
        raise HTTPException(status_code=404, detail=f"Brak with user_id={user_id} not found")

    tree = FamilyTree(user_id)
    tree_lib = tree.to_treelib()
    formatted_tree = tree_lib.show(stdout=False)

    return PlainTextResponse(formatted_tree)


@router.get("/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    brak = get_brak_by_user_id(user_id)
    if not brak:
        raise HTTPException(status_code=404, detail=f"Brak with user_id={user_id} not found")

    tree = {}
    return tree.__str__()
