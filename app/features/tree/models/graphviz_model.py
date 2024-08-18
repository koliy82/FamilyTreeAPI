from graphviz import Digraph

from app.features.tree.models.base_model import BaseFamilyTree, T


class GraphvizLib(BaseFamilyTree):
    def __new__(cls, *args, **kwargs):
        cls.graph = Digraph(comment="Family Tree")
        return super().__new__(cls)

    def empty_node(self):
        self.graph.node("0", "Empty")
        pass

    def add_pair(self, tree: T, root_data: tuple[str, int | None], partner_data: tuple[str, int], root_prefix:str, root_suffix:str, partner_prefix:str, partner_suffix:str):
        root_name, root_id = root_data
        partner_name, partner_id = partner_data
        self.graph.node(str(tree.user_id), f"{root_prefix}{root_name}{root_suffix}")
        self.graph.node(str(partner_id), f"{partner_prefix}{partner_name}{partner_suffix}")
        if self.user_id == tree.user_id:
            self.graph.edge(str(self.user_id), str(partner_id), constraint="false", label='♥️')
        else:
            self.graph.edge(str(root_id), str(tree.user_id), label='♥️')
            self.graph.edge(str(tree.user_id), str(partner_id))