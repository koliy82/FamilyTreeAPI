from io import BytesIO

from familytreelib import TreeLib, GraphvizLib, IgraphLib, Ete3Lib, NetworkxLib
from fastapi import APIRouter
from starlette.responses import PlainTextResponse, StreamingResponse

from app.database.mongo import braks

router = APIRouter(
    prefix="/tree",
    tags=["tree"]
)


@router.get("/")
async def root():
    return "tree"


@router.get("/text/{user_id}")
async def family_tree(user_id: int, reverse: bool = True, kid_prefix = '👼 ', kid_suffix = '', partner_prefix = '🫂 ', partner_suffix = '', root_prefix = '', root_suffix = '❤️‍🔥'):
    tree = TreeLib(user_id=user_id, kid_prefix=kid_prefix, kid_suffix=kid_suffix, partner_prefix=partner_prefix, partner_suffix=partner_suffix, root_prefix=root_prefix, root_suffix=root_suffix)
    tree.build_tree(braks)
    formatted_tree = tree.tree.show(stdout=False, reverse=reverse)
    return PlainTextResponse(formatted_tree)


@router.get("/image_graphviz/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, kid_prefix = '', kid_suffix = '', partner_prefix = '', partner_suffix = '', root_prefix = '', root_suffix = '', max_duplicate: int = 1):
    tree = GraphvizLib(user_id, kid_prefix=kid_prefix, kid_suffix=kid_suffix, partner_prefix=partner_prefix, partner_suffix=partner_suffix, root_prefix=root_prefix, root_suffix=root_suffix, max_duplicate=max_duplicate)
    tree.build_tree(braks)
    image_stream = BytesIO(tree.graph.pipe(format="png"))
    image_stream.seek(0)
    return StreamingResponse(image_stream, media_type="image/png")


@router.get("/image_ete3/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, kid_prefix = '', kid_suffix = '', partner_prefix = '', partner_suffix = '', root_prefix = '', root_suffix = ''):
    tree = Ete3Lib(user_id, kid_prefix=kid_prefix, kid_suffix=kid_suffix, partner_prefix=partner_prefix, partner_suffix=partner_suffix, root_prefix=root_prefix, root_suffix=root_suffix)
    tree.build_tree(braks)
    image_stream = tree.render()
    if image_stream is None:
        return {"error": "Family tree not found"}
    return StreamingResponse(image_stream, media_type="image/png")

@router.get("/image_igraph/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = IgraphLib(user_id)
    tree.build_tree(braks)
    image_stream = tree.render()
    return StreamingResponse(image_stream, media_type="image/png")

@router.get("/image_networkx/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, prog = "dot"):
    tree = NetworkxLib(user_id)
    tree.build_tree(braks)
    img_stream = tree.render(prog)
    return StreamingResponse(img_stream, media_type="image/png")