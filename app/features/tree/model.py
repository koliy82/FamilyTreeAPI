from typing import Dict, Optional

from treelib import Tree as TreeLib

from app.database.mongo import braks
from app.features.brak.model import Brak, get_brak_by_user_id
from app.features.user.model import User


class UsersBrak:
    brak: Optional[Brak] = None
    first: Optional[User] = None
    second: Optional[User] = None
    baby: Optional[User] = None

    def __init__(self, user_id: int):
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
            }, {
                '$lookup': {
                    'from': 'users',
                    'localField': 'baby_user_id',
                    'foreignField': 'id',
                    'as': 'baby'
                }
            }, {
                '$unwind': {
                    'path': '$first',
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$unwind': {
                    'path': '$second',
                    'preserveNullAndEmptyArrays': True
                }
            }, {
                '$unwind': {
                    'path': '$baby',
                    'preserveNullAndEmptyArrays': True
                }
            }
        ]
        results = braks.aggregate(pipeline)
        for result in results:
            self.brak = Brak.from_mongo(result)
            if 'first' in result:
                first_data = result['first']
                if first_data:
                    self.first = User.from_mongo(first_data)
            if 'second' in result:
                second_data = result['second']
                if second_data:
                    self.second = User.from_mongo(second_data)
            if 'baby' in result:
                baby_data = result['baby']
                if baby_data:
                    self.baby = User.from_mongo(baby_data)

    def partner_data(self, root_id: int) -> (str, int):
        if self.brak.first_user_id == root_id:
            if self.second:
                return f"{self.second.first_name} {self.second.last_name}", self.brak.second_user_id
            else:
                return self.brak.second_user_id.__str__(), self.brak.second_user_id
        else:
            if self.first:
                return f"{self.first.first_name} {self.first.last_name}", self.brak.first_user_id
            else:
                return self.brak.first_user_id.__str__(), self.brak.first_user_id


class FamilyTree:
    def __init__(self, root_user_id: int):
        self.root_user_id = root_user_id
        self.tree: Dict[int, UsersBrak] = {}
        self.build_tree(root_user_id)

    def build_tree(self, user_id: int):
        model = UsersBrak(user_id)
        if model.brak:
            self.tree[user_id] = model
            if model.brak and model.brak.baby_user_id:
                self.build_tree(model.brak.baby_user_id)

    def to_treelib(self):
        tree_lib = TreeLib()
        root_id = self.root_user_id
        if root_id not in self.tree:
            tree_lib.create_node(f"Tree is empty", root_id)
            return tree_lib

        root_model = self.tree[root_id]
        if root_model.brak.first_user_id == root_id:
            if root_model.first:
                root_name = f"{root_model.first.first_name} {root_model.first.last_name}"
            else:
                root_name = root_model.brak.first_user_id.__str__()
        else:
            if root_model.second:
                root_name = f"{root_model.second.first_name} {root_model.second.last_name}"
            else:
                root_name = root_model.brak.first_user_id.__str__()
        tree_lib.create_node(root_name, root_id)

        def add_nodes(parent_id: int):
            if parent_id not in self.tree:
                return
            model = self.tree[parent_id]
            partner_name, partner_id = model.partner_data(parent_id)
            tree_lib.create_node(f"{partner_name}", partner_id, parent=parent_id)
            if model.brak.baby_user_id:
                if model.baby:
                    tree_lib.create_node(f"{model.baby.first_name} {model.baby.last_name}",
                                         model.brak.baby_user_id, parent=parent_id)
                else:
                    tree_lib.create_node(f"{model.baby.id}", model.brak.baby_user_id, parent=parent_id)
                add_nodes(model.brak.baby_user_id)

        add_nodes(root_id)
        return tree_lib
