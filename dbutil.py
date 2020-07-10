import pymongo
import time

from bson import ObjectId


class DBUtil:
    def __init__(self):
        self.client = pymongo.MongoClient(host='123.57.133.29', port=27017)
        self.db = self.client.api_manager
        self.user_table = self.db.user
        self.project_table = self.db.project
        self.api_table = self.db.api

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

    def find_user_by_id(self, user_id: str) -> dict:
        """
        根据id查找用户信息

        :param user_id: 用户id
        :return: 字典形式数据，不存在则返回None
        """
        return self.user_table.find_one({"_id": ObjectId(user_id)})

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

    def update_member_permission(self, project_id: str, member_id: str, permission: int):
        """
        修改项目成员权限

        :param project_id: 项目id
        :param member_id:  成员id
        :param permission: 新权限
        :return:
        """
        self.project_table.update_one(
            {
                "$and": [
                    {
                        "_id": ObjectId(project_id)
                    },
                    {
                        "members.userId": member_id
                    }
                ]
            },
            {
                "$set": {
                    "members.$.permission": permission
                }
            }
        )

    def find_user_created_project(self, user_id: str) -> list:
        """
        查找用户创建的项目

        :param user_id: 用户id
        :return:
        """
        data = self.project_table.find({"creator": user_id})
        result = []
        for i in data:
            result.append(i)
        return result

    def find_user_joined_project(self, user_id: str) -> list:
        """
        查找用户参加的项目（不包括创建的）

        :param user_id: 用户id
        :return:
        """
        data = self.project_table.find({"members.userId": user_id})
        result = []
        for i in data:
            result.append(i)
        return result

    def add_project_api(self, project_id: str, group_name: str, api_id: str, api_name: str):
        """
        向项目中添加api

        :param project_id: 项目id
        :param group_name: api分组名
        :param api_id: api的id
        :param api_name api的名称
        :return:
        """
        # 先查看该分组是否存在
        project_data = self.project_table.find_one(
            {
                "$and": [
                    {
                        '_id': ObjectId(project_id)
                    },
                    {
                        'apis.groupName': group_name
                    }
                ]
            }
        )
        if project_data is None:
            self.project_table.update_one(
                {
                    "_id": ObjectId(project_id)
                },
                {
                    "$addToSet": {
                        'apis': {
                            'groupName': group_name,
                            'apiIds': [
                                {
                                    'apiId': api_id,
                                    'name': api_name
                                }
                            ]
                        }
                    }
                }
            )
        else:
            # 先查找位置
            index = 0
            for group in project_data['apis']:
                if group['groupName'] == group_name:
                    break
                index = index + 1
            # 然后添加
            self.project_table.update_one(
                {
                    "_id": ObjectId(project_id),
                    "apis.groupName": group_name
                }, {
                    "$addToSet": {
                        f'apis.{index}.apiIds': {
                            'apiId': api_id,
                            'name': api_name
                        }
                    }
                }

            )

    def delete_project_api(self, project_id: str, api_id: str):
        """
        删除project表中的api

        :param project_id: 项目id
        :param api_id: api id
        :return:
        """
        project_data = self.project_table.find_one({'_id': ObjectId(project_id)})
        index = -1
        exist = False
        for api in project_data['apis']:
            index = index + 1
            for api_data in api['apiIds']:
                if api_data['apiId'] == api_id:
                    exist = True
                    break
            if exist is True:
                break
        if exist is True:
            self.project_table.update_one(
                {
                    "_id": ObjectId(project_id)
                }, {
                    "$pull": {
                        f'apis.{index}.apiIds': {
                            'apiId': api_id
                        }
                    }
                }
            )

    def create_api(self, create_user_id: str, api_data: dict) -> ObjectId:
        """
        新建接口

        :param create_user_id 创建者的id，字符串形式
        :param api_data: 这个数据有严格的格式，请参照api.md文档中创建接口的请求参数
        :return: 返回ObjectId
        """
        api_data['createUser'] = create_user_id
        api_data['createTime'] = time.time()
        api_data['updateTime'] = api_data['createTime']
        api_data['updateUser'] = create_user_id
        return self.api_table.insert_one(api_data).inserted_id

    def find_api(self, api_id: str) -> dict:
        """
        根据id查找api

        :param api_id: id
        :return: 字典形式的数据，如果不存在返回None
        """
        return self.api_table.find_one({"_id": ObjectId(api_id)})

    def delete_api(self, api_id: str):
        """
        在api表中删除api

        :param api_id: api id
        :return:
        """
        self.api_table.delete_one({'_id': ObjectId(api_id)})


db = DBUtil()

