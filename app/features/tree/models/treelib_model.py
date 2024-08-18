from treelib import Tree

from app.features.tree.models.base_model import BaseFamilyTree, T


class TreeLib(BaseFamilyTree):
    def __new__(cls, *args, **kwargs):
        cls.tree = Tree()
        return super().__new__(cls)


    def empty_node(self):
        self.tree.create_node("Empty", 0)

    def add_pair(self, tree: T, root_data: tuple[str, int | None], partner_data: tuple[str, int], root_prefix:str, root_suffix:str, partner_prefix:str, partner_suffix:str):
        root_name, root_id = root_data
        partner_name, partner_id = partner_data
        print(f"{root_prefix}{root_name}{root_suffix}")
        print(f"{partner_prefix}{partner_name}{partner_suffix}")
        self.tree.create_node(f"{root_prefix}{root_name}{root_suffix}", tree.user_id, parent=root_id)
        self.tree.create_node(f"{partner_prefix}{partner_name}{partner_suffix}", partner_id, parent=tree.user_id)
