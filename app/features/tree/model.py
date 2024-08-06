from typing import Dict, List

from pydantic import BaseModel
from treelib import Tree as TreeLib

from app.features.brak.model import Brak, get_brak_by_user_id


class FamilyTree(BaseModel):
    tree: Dict[tuple, List[int]]

    def __init__(self, user_id: int):
        super().__init__(tree={})
        brak = get_brak_by_user_id(user_id)
        if brak:
            self.build_family_tree(brak)

    def build_family_tree(self, brak: Brak) -> None:
        key = (brak.first_user_id, brak.second_user_id)
        if key not in self.tree:
            self.tree[key] = []
        if brak.baby_user_id:
            self.tree[key].append(brak.baby_user_id)
            next_brak = get_brak_by_user_id(brak.baby_user_id)
            if next_brak:
                self.build_family_tree(next_brak)

    def to_treelib(self) -> TreeLib:
        tree_lib = TreeLib()
        root_id = None

        def add_nodes(parent_id, children):
            for child in children:
                if not tree_lib.get_node(child):
                    tree_lib.create_node(f"User {child}", child, parent=parent_id)
                next_brak = get_brak_by_user_id(child)
                if next_brak:
                    key = (next_brak.first_user_id, next_brak.second_user_id)
                    if key in self.tree:
                        add_nodes(child, self.tree[key])

        for key in self.tree:
            if root_id is None:
                root_id = key[0]
                tree_lib.create_node(f"User {key[0]}", key[0])
                tree_lib.create_node(f"User {key[1]}", key[1], parent=key[0])
            add_nodes(key[0], self.tree[key])

        return tree_lib
