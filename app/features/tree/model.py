from typing import Optional

from app.database.mongo import braks
from app.features.brak.model import Brak
from app.features.user.model import User


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
