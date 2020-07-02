import pymongo
import time

from bson import ObjectId


class DBUtil:
    def __init__(self):
        self.client = pymongo.MongoClient(host='123.57.133.29', port=27017)
        self.db = self.client.api_manager
        self.user_table = self.db.user
        self.project_table = self.db.project

    def insert_user(self, account: str, password: str, name: str) -> bool:
        """
        向user表插入一个用户数据

        :return 成功返回True，失败返回False
        """

        # 先检查账号是否存在
        if self.find_user(account) is not None:
            return False
        # 账号不存在则插入
        self.user_table.insert_one({
            'account': account,
            'password': password,
            'name': name
        })
        return True

    def find_user(self, account: str) -> dict:
        """
        根据账号查找用户

        :param account: 账号
        :return: 存在则返回字典数据，不存在返回None
        """
        return self.user_table.find_one({'account': account})

    def create_project(self, creator: str, name: str, members: list) -> ObjectId:
        """
        创建项目，其中members是一个列表，每个元素都必须有userId和permission
        两个属性，userId为用户的id,permission只有两个取值，0代表只读，1代表可读可写

        :param creator: 创建者的id
        :param name: 项目名
        :param members: 项目成员，每个列表的元素必须有userId和permission两个属性
        :return: 返回项目的ObjectId
        """
        return self.project_table.insert_one({
            "name": name,
            "createTime": time.time(),
            "creator": creator,
            "members": members,
            "apis": []
        }).inserted_id

    def find_project(self, project_id: str) -> dict:
        """
        根据项目id查找项目

        :param project_id: 项目id，字符串形式
        :return: 返回字典形式的数据，不存在则返回None
        """
        return self.project_table.find_one({
            "_id": ObjectId(project_id)
        })

    def add_project_member(self, project_id: str, member_id: str, permission: int):
        """
        添加项目成员

        :param project_id: 项目的id，str类型
        :param member_id: 成员的id，str类型
        :param permission: 成员权限，0代表只读，1代表可读可写
        :return:
        """
        self.project_table.update_one(
            {
                "_id": ObjectId(project_id)
            },
            {
                "$addToSet": {
                    "members": {
                        "userId": member_id,
                        "permission": permission
                    }
                }
            }
        )


c = DBUtil()

