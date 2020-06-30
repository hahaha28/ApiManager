import pymongo


class DBUtil:
    def __init__(self):
        self.client = pymongo.MongoClient(host='123.57.133.29', port=27017)
        self.db = self.client.api_manager
        self.user_table = self.db.user

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



c = DBUtil()
result = c.find_user('1234')
print(result)