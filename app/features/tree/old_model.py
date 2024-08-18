from typing import Optional, List, Tuple

from app.database.mongo import braks
from app.features.brak.model import Brak
from app.features.user.model import User
import networkx as nx

# ROOT + PARTNER -> BABY + PARTNER -> BABY + PARTNER -> ...
class FamilyTree:
    user_id: int
    brak: Optional[Brak] = None
    first: Optional[User] = None
    second: Optional[User] = None
    next: Optional['FamilyTree'] = None

    def __init__(self, user_id: int):
        self.user_id = user_id
        pipeline = [
            {
                '$match': {
                    '$or': [
                        {
                            'first_user_id': user_id
                        }, {
                            'second_user_id': user_id
                        }
                    ]
                }
            }, {
                '$limit': 1
            }, {
                '$lookup': {
                    'from': 'users',
                    'localField': 'first_user_id',
                    'foreignField': 'id',
                    'as': 'first'
                }
            }, {
                '$lookup': {
                    'from': 'users',
                    'localField': 'second_user_id',
                    'foreignField': 'id',
                    'as': 'second'
                }
            },
            {
                '$unwind': {
                    'path': '$first',
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$unwind': {
                    'path': '$second',
                    'preserveNullAndEmptyArrays': True
                }
            },
        ]
        results = braks.aggregate(pipeline)
        for result in results:
            self.brak = Brak.from_mongo(result)
            if self.brak is None:
                continue
            if 'first' in result:
                first_data = result['first']
                if first_data:
                    self.first = User.from_mongo(first_data)
            if 'second' in result:
                second_data = result['second']
                if second_data:
                    self.second = User.from_mongo(second_data)
            if self.brak and self.brak.baby_user_id:
                self.next = FamilyTree(self.brak.baby_user_id)

    def to_treelib(self, kid_prefix, partner_prefix):
        from treelib import Tree
        tree_lib = Tree()
        if self.brak is None:
            tree_lib.create_node(f"Tree is empty", self.user_id)
            return tree_lib
        root_name, _ = self.root_data()
        # ROOT NODE
        tree_lib.create_node(f"{root_name} ❤️‍🔥", self.user_id)
        root_partner_name, root_partner_id = self.partner_data(self.user_id)
        # PARTNER NODE
        tree_lib.create_node(f"{root_partner_name} ❤️‍🔥", root_partner_id, parent=self.user_id)

        def add_nodes(tree: FamilyTree, root_id: int):
            if tree is None or tree.brak is None:
                return
            first_name, _ = tree.root_data()
            # BABY NODE
            tree_lib.create_node(f"{kid_prefix}{first_name}", tree.user_id, parent=root_id)
            partner_name, partner_id = tree.partner_data(tree.user_id)
            # BABY PARTNER NODE
            tree_lib.create_node(f"{partner_prefix}{partner_name}", partner_id, parent=tree.user_id)
            if tree.next:
                add_nodes(tree.next, tree.user_id)

        add_nodes(self.next, self.user_id)
        return tree_lib

    def to_graphviz(self):
        if self.brak is None:
            return None
        from graphviz import Digraph
        dot = Digraph(comment="Family Tree")

        def add_nodes(tree: FamilyTree, root_id: int):
            if tree is None or tree.brak is None:
                return
            root_name, _ = tree.root_data()
            partner_name, partner_id = tree.partner_data(tree.user_id)

            dot.node(str(tree.user_id), f"{root_name}", width="0.75", height="0.5")
            dot.node(str(partner_id), f"{partner_name}", width="0.75", height="0.5")
            dot.edge(str(tree.user_id), str(partner_id))

            if tree.next:
                dot.edge(str(root_id), str(tree.user_id))
                add_nodes(tree.next, tree.user_id)

        root_name, _ = self.root_data()
        partner_name, partner_id = self.partner_data(self.user_id)

        dot.node(str(self.user_id), f"{root_name}", width="0.75", height="0.5")
        dot.node(str(partner_id), f"{partner_name}", width="0.75", height="0.5")
        dot.edge(str(self.user_id), str(partner_id), constraint="false", label='♥️')

        add_nodes(self.next, self.user_id)
        return dot

    def to_anytree(self):
        if self.brak is None:
            return None
        from anytree import Node

        def build_tree(tree: FamilyTree, r_node: Node):
            if tree is None or tree.brak is None:
                return
            r_name, _ = tree.root_data()
            part_name, _ = tree.partner_data(tree.user_id)
            child_node = Node(f"{r_name}", parent=r_node)
            _ = Node(f"{part_name}", parent=child_node)
            if tree.next:
                build_tree(tree.next, child_node)

        root_name, _ = self.root_data()
        partner_name, partner_id = self.partner_data(self.user_id)

        root_node = Node(f"{root_name}")
        _ = Node(f"{partner_name}", parent=root_node)
        build_tree(self.next, root_node)
        return root_node

    def partner_data(self, root_id: int) -> (str, int):
        if self.brak.first_user_id == root_id:
            if self.second:
                return f"{self.second.first_name} {self.second.last_name}", self.brak.second_user_id
            else:
                return "?", self.brak.second_user_id
        else:
            if self.first:
                return f"{self.first.first_name} {self.first.last_name}", self.brak.first_user_id
            else:
                return "?", self.brak.first_user_id

    def root_data(self) -> (str, int):
        if self.user_id == self.brak.first_user_id:
            if self.first:
                return f"{self.first.first_name} {self.first.last_name}", self.brak.first_user_id
            else:
                return "?", self.brak.first_user_id
        else:
            if self.second:
                return f"{self.second.first_name} {self.second.last_name}", self.brak.second_user_id
            else:
                return "?", self.brak.second_user_id

    def to_ete3(self):
        if self.brak is None:
            return None, None
        from ete3 import AttrFace, Tree, TreeStyle, faces

        def add_nodes(tree: FamilyTree, parent_node):
            if tree is None or tree.brak is None:
                return

            root_name, _ = tree.root_data()
            partner_name, partner_id = tree.partner_data(tree.user_id)

            root_node = parent_node.add_child(name=f"👼 {root_name}")
            partner_node = root_node.add_child(name=f"🫂 {partner_name}")
            root_node.add_face(AttrFace("name", f"🫂 {root_name}"), column=0, position="branch-top")
            # partner_node.add_face(AttrFace("name", f"{partner_name}"), column=0, position="branch-top")
            if tree.next:
                add_nodes(tree.next, root_node)

        root_name, _ = self.root_data()
        tree = Tree(name=root_name)
        ts = TreeStyle()
        ts.title.add_face(faces.TextFace(f"🤔Семейное древо - {root_name}", fsize=20), column=0)
        ts.show_leaf_name = True
        ts.show_scale = False
        # tree.add_face(AttrFace("name", f"{root_name}"), column=0, position="branch-top")
        add_nodes(self.next, tree)
        return tree, ts

    def to_igraph(self, kid_prefix="👶 ", partner_prefix="💑 "):
        from igraph import Graph
        g = Graph(directed=True)
        labels = []
        edges = []

        # ROOT NODE
        root_name, root_id = self.root_data()
        labels.append(f"{root_name} ❤️‍🔥")
        g.add_vertex(name=str(self.user_id))

        # PARTNER NODE
        partner_name, partner_id = self.partner_data(self.user_id)
        if partner_id != -1:
            labels.append(f"{partner_name} ❤️‍🔥")
            g.add_vertex(name=str(partner_id))
            edges.append((str(self.user_id), str(partner_id)))

        def add_nodes(tree: FamilyTree, parent_id: int):
            if tree is None or tree.brak is None:
                return
            # BABY NODE
            first_name, user_id = tree.root_data()
            labels.append(f"{kid_prefix}{first_name}")
            g.add_vertex(name=str(user_id))
            edges.append((str(parent_id), str(user_id)))
            # BABY PARTNER NODE
            partner_name, partner_id = tree.partner_data(user_id)
            if partner_id != -1:
                labels.append(f"{partner_prefix}{partner_name}")
                g.add_vertex(name=str(partner_id))
                edges.append((str(user_id), str(partner_id)))
            if tree.next:
                add_nodes(tree.next, user_id)

        add_nodes(self.next, self.user_id)
        g.add_edges(edges)

        return g, labels

    def build_edges(self) -> List[Tuple[str, str]]:
        edges = []
        root_name, root_id = self.root_data()
        # PARTNER NODE
        partner_name, partner_id = self.partner_data(self.user_id)
        if partner_id != -1:
            edges.append((f"{root_name} ❤️‍🔥", f"{partner_name} ❤️‍🔥"))

        def add_edges(tree: FamilyTree, parent_name: str):
            if tree is None or tree.brak is None:
                return
            # BABY NODE
            first_name, user_id = tree.root_data()
            edges.append((parent_name, f"👶 {first_name}"))
            # BABY PARTNER NODE
            partner_name, partner_id = tree.partner_data(user_id)
            if partner_id != -1:
                edges.append((f"👶 {first_name}", f"💑 {partner_name}"))
            if tree.next:
                add_edges(tree.next, f"👶 {first_name}")

        add_edges(self.next, f"{root_name} ❤️‍🔥")
        return edges

    def to_plotly_treee(self):
        import plotly.graph_objects as go
        if self.brak is None:
            return None
        edges = self.build_edges()
        labels = {label for edge in edges for label in edge}
        labels = list(labels)
        positions = {label: idx for idx, label in enumerate(labels)}

        Xn = [positions[label] for label in labels]
        Yn = [len(labels) - positions[label] for label in labels]

        Xe = []
        Ye = []
        for edge in edges:
            Xe.extend([positions[edge[0]], positions[edge[1]], None])
            Ye.extend([len(labels) - positions[edge[0]], len(labels) - positions[edge[1]], None])

        fig = go.Figure()

        fig.add_trace(go.Scatter(x=Xe, y=Ye, mode='lines', line=dict(color='rgb(210, 210, 210)', width=2), hoverinfo='none'))

        fig.add_trace(go.Scatter(x=Xn, y=Yn, mode='markers+text',
                                 marker=dict(symbol='circle-dot', size=20, color='#6175c1',
                                             line=dict(color='rgb(50,50,50)', width=1)), text=labels, hoverinfo='text',
                                 textposition="bottom center"))

        fig.update_layout(
            title='Family Tree',
            showlegend=False,
            xaxis=dict(showline=False, zeroline=False),
            yaxis=dict(showline=False, zeroline=False),
            margin=dict(l=40, r=40, b=85, t=100),
            hovermode='closest',
            plot_bgcolor='rgb(248,248,248)'
        )
        return fig

    def to_plotly_tree(self):
        if self.brak is None:
            return None

        graph, labels = self.to_igraph()
        lay = graph.layout()
        nr_vertices = graph.vcount()

        position = {k: lay[k] for k in range(nr_vertices)}
        Y = [lay[k][1] for k in range(nr_vertices)]
        M = max(Y)

        E = [e.tuple for e in graph.es]  # list of edges

        L = len(position)
        Xn = [position[k][0] for k in range(L)]
        Yn = [2 * M - position[k][1] for k in range(L)]
        Xe = []
        Ye = []
        for edge in E:
            Xe += [position[edge[0]][0], position[edge[1]][0], None]
            Ye += [2 * M - position[edge[0]][1], 2 * M - position[edge[1]][1], None]

        import plotly.graph_objects as go
        fig = go.Figure()
        fig.add_trace(
            go.Scatter(
                x=Xe,
                y=Ye,
                mode='lines',
                line=dict(color='rgb(210,210,210)', width=1),
                hoverinfo='none'
                )
        )
        fig.add_trace(
            go.Scatter(
                x=Xn,
                y=Yn,
                mode='markers',
                name='bla',
                marker=dict(symbol='circle-dot',
                         size=18,
                         color='#6175c1',  # '#DB4551',
                         line=dict(color='rgb(50,50,50)', width=1)
                         ),
                text=labels,
                hoverinfo='none',
                opacity=0.8
                )
        )

        axis = dict(showline=False,  # hide axis line, grid, ticklabels and  title
                    zeroline=False,
                    showgrid=False,
                    showticklabels=False,
                    )
        L = len(position)
        annotations = []
        for k in range(L):
            annotations.append(
                dict(
                    text=labels[k],  # or replace labels with a different list for the text within the circle
                    x=position[k][0], y=2 * M - position[k][1],
                    xref='x1', yref='y1',
                    font=dict(color='rgb(250,250,250)', size=12),
                    showarrow=False)
            )
        fig.update_layout(
                font_size=12,
                annotations=annotations,
                showlegend=False,
                xaxis=axis,
                yaxis=axis,
                hovermode='closest',
                plot_bgcolor='rgb(248,248,248)'
              )
        return fig

    def to_networkx(self):
        if self.brak is None:
            return None

        G = nx.DiGraph()

        def add_nodes(tree: FamilyTree, root_id: int):
            if tree is None or tree.brak is None:
                return

            root_name, _ = tree.root_data()
            partner_name, partner_id = tree.partner_data(tree.user_id)

            G.add_node(tree.user_id, name=root_name)
            G.add_node(partner_id, name=partner_name)
            G.add_edge(tree.user_id, partner_id)

            if tree.next:
                G.add_edge(root_id, tree.user_id)
                add_nodes(tree.next, tree.user_id)

        root_name, root_id = self.root_data()
        partner_name, partner_id = self.partner_data(root_id)

        G.add_node(root_id, name=root_name)
        G.add_node(partner_id, name=partner_name)
        G.add_edge(root_id, partner_id)

        add_nodes(self.next, root_id)

        return G