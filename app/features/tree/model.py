from typing import Optional

from treelib import Tree as TreeLib

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
            print(result)
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

    def to_treelib(self):
        tree_lib = TreeLib()
        if self.brak is None or self.next is None:
            tree_lib.create_node(f"Tree is empty", self.user_id)
            return tree_lib
        print(f"self={self.user_id} {self.brak.first_user_id} {self.brak.second_user_id} {self.brak.baby_user_id}")
        root_name, _ = self.root_data()
        # ROOT NODE
        tree_lib.create_node(f"{root_name} ❤️‍🔥", self.user_id)
        root_partner_name, root_partner_id = self.partner_data(self.user_id)
        # PARTNER NODE
        tree_lib.create_node(f"{root_partner_name} ❤️‍🔥", root_partner_id, parent=self.user_id)

        def add_nodes(tree: FamilyTree, root_id: int):
            if tree is None or tree.brak is None:
                return
            print(f"tree={tree.user_id} {tree.brak.first_user_id} {tree.brak.second_user_id} {tree.brak.baby_user_id}")
            first_name, _ = tree.root_data()
            # BABY NODE
            tree_lib.create_node(f"👼 {first_name}", tree.user_id, parent=root_id)
            partner_name, partner_id = tree.partner_data(tree.user_id)
            # BABY PARTNER NODE
            tree_lib.create_node(f"🫂 {partner_name}", partner_id, parent=tree.user_id)
            if tree.next:
                add_nodes(tree.next, tree.user_id)

        add_nodes(self.next, self.user_id)
        return tree_lib

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
