from io import BytesIO

import networkx as nx
import matplotlib.pyplot as plt
from anytree.exporter import UniqueDotExporter
from fastapi import APIRouter, HTTPException
from igraph import plot
from starlette.responses import PlainTextResponse, StreamingResponse

from app.features.tree.models.ete3_model import Ete3Lib
from app.features.tree.models.graphviz_model import GraphvizLib
from app.features.tree.old_model import FamilyTree
from app.features.tree.models.treelib_model import TreeLib
from app.utils.temp_file import TempFile

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
    tree.build_tree()
    formatted_tree = tree.tree.show(stdout=False, reverse=reverse)
    return PlainTextResponse(formatted_tree)


@router.get("/image_graphviz/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, kid_prefix = '', kid_suffix = '', partner_prefix = '', partner_suffix = '', root_prefix = '', root_suffix = ''):
    tree = GraphvizLib(user_id, kid_prefix=kid_prefix, kid_suffix=kid_suffix, partner_prefix=partner_prefix, partner_suffix=partner_suffix, root_prefix=root_prefix, root_suffix=root_suffix)
    tree.build_tree()
    image_stream = BytesIO(tree.graph.pipe(format="png"))
    image_stream.seek(0)
    return StreamingResponse(image_stream, media_type="image/png")


@router.get("/image_ete3/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, kid_prefix = '', kid_suffix = '', partner_prefix = '', partner_suffix = '', root_prefix = '', root_suffix = ''):
    tree = Ete3Lib(user_id, kid_prefix=kid_prefix, kid_suffix=kid_suffix, partner_prefix=partner_prefix, partner_suffix=partner_suffix, root_prefix=root_prefix, root_suffix=root_suffix)
    tree.build_tree()
    image_stream = tree.render()
    if image_stream is None:
        return {"error": "Family tree not found"}
    return StreamingResponse(image_stream, media_type="image/png")


@router.get("/image_anytree/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = FamilyTree(user_id)
    tree = tree.to_anytree()
    if tree is None:
        raise HTTPException(status_code=404, detail="Family tree not found")

    with TempFile(suffix=".png") as file:
        UniqueDotExporter(tree).to_picture(file.temp_file.name)
        img_stream = BytesIO(file.read())
        img_stream.seek(0)
        if img_stream is None:
            return {"error": "Family tree not found"}
    return StreamingResponse(img_stream, media_type="image/png")


@router.get("/image_igraph/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = FamilyTree(user_id)
    g, labels = tree.to_igraph()
    layout = g.layout_reingold_tilford(root=[0])
    visual_style = {
        "vertex_label": labels,
        "vertex_size": 20,
        "margin": 40,
        "layout": layout,
        "vertex_color": "lightblue",
        "vertex_label_dist": -2,
        "edge_width": 2
    }

    with TempFile(suffix=".png") as file:
        plot(g, target=file.path, **visual_style)
        img_stream = BytesIO(file.read())
        img_stream.seek(0)
        if img_stream is None:
            return {"error": "Family tree not found"}

    return StreamingResponse(img_stream, media_type="image/png")


@router.get("/image_v2/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int):
    tree = FamilyTree(user_id)
    fig = tree.to_plotly_tree()
    if fig is None:
        return {"error": "Family tree not found"}
    img_data = fig.to_image(format="png")
    img_stream = BytesIO(img_data)

    return StreamingResponse(img_stream, media_type="image/png")

@router.get("/image_v3/{user_id}", responses={404: {"description": "Family tree not found"}})
async def family_tree(user_id: int, prog = "dot"):
    tree = FamilyTree(user_id)
    graph = tree.to_networkx()
    if graph is None:
        return {"error": "Family tree not found"}
    # # pos = nx.spring_layout(graph)
    # pos = hierarchy_pos(graph, list(graph.nodes)[0])
    # plt.figure(figsize=(12, 10))
    labels = nx.get_node_attributes(graph, 'name')
    pos = nx.nx_agraph.graphviz_layout(graph, prog=prog, args="")
    # plt.figure(figsize=(8, 8))
    nx.draw(
        graph, pos, node_size=20, alpha=0.5, node_color="blue",
        with_labels=True, labels=labels, arrows=True,
        width=2, font_size=10, font_color="black", linewidths=1.0, node_shape="s",
        font_family=['Sawasdee', 'Gentium Book Basic', 'FreeMono', ]
    )
    plt.axis("equal")

    with TempFile(suffix=".png") as file:
        plt.savefig(file.path, format='png')
        img_stream = BytesIO(file.read())
        img_stream.seek(0)
        plt.close()
        if img_stream is None:
            return {"error": "Family tree not found"}

    return StreamingResponse(img_stream, media_type="image/png")