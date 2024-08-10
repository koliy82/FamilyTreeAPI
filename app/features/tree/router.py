import os
import tempfile
from io import BytesIO

from fastapi import APIRouter, HTTPException
from starlette.responses import PlainTextResponse, StreamingResponse

from app.features.tree.model import FamilyTree

router = APIRouter(
    prefix="/tree",
    tags=["tree"]
)


@router.get("/")
async def root():
    return "tree"


@router.get("/text/{user_id}")
async def family_tree(user_id: int, reverse: bool = True, kid_prefix: str = "👼 ", partner_prefix: str = "🫂 "):
    tree = FamilyTree(user_id)
    tree_lib = tree.to_treelib(kid_prefix, partner_prefix)
    formatted_tree = tree_lib.show(stdout=False, reverse=reverse)
    return PlainTextResponse(formatted_tree)


@router.get("/image/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = FamilyTree(user_id)
    dot = tree.to_graphviz()
    if dot is None:
        raise HTTPException(status_code=404, detail="Family tree not found")
    image_stream = BytesIO(dot.pipe(format='png'))
    image_stream.seek(0)
    return StreamingResponse(image_stream, media_type="image/png")


@router.get("/image_ete3/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = FamilyTree(user_id)
    tree, style = tree.to_ete3()
    if tree is None:
        raise HTTPException(status_code=404, detail="Family tree not found")

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp_file:
        temp_file_path = tmp_file.name

    tree.render(temp_file_path, units="px", tree_style=style)
    img_stream = BytesIO()
    with open(temp_file_path, 'rb') as f:
        img_stream.write(f.read())
    os.remove(temp_file_path)
    img_stream.seek(0)
    return StreamingResponse(img_stream, media_type="image/png")
