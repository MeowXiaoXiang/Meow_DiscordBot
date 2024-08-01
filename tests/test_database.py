import unittest
import os
import sys

# 動態add專案根目錄到 sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# import 資料庫
from module import connect_db, set_key, get_key, get_all_emoji_info, delete_all

class TestDatabaseOperations(unittest.TestCase):

    def setUp(self):
        # 在每個測試之前建立資料庫session
        self.Session = connect_db()
        self.session = self.Session()
        delete_all(self.session)  # 清空資料庫

    def tearDown(self):
        # 每個測試之後都關閉資料庫session
        self.session.close()

    def test_set_and_get_key(self):
        # 測試設定和取得key:value
        set_key(self.session, 123456789012345678, 10)
        value = get_key(self.session, 123456789012345678)
        self.assertEqual(value, 10)

    def test_get_non_existent_key(self):
        # 測試取得不存在的key
        value = get_key(self.session, 999999999999999999)
        self.assertIsNone(value)

    def test_get_all_emoji_info(self):
        # 測試get所有emoji_info
        set_key(self.session, 123456789012345678, 10)
        set_key(self.session, 876543210987654321, 20)
        all_emoji_info = get_all_emoji_info(self.session)
        self.assertEqual(len(all_emoji_info), 2)
        self.assertIn((123456789012345678, 10), all_emoji_info)
        self.assertIn((876543210987654321, 20), all_emoji_info)

    def test_delete_all(self):
        # 測試刪除所有資料
        set_key(self.session, 123456789012345678, 10)
        set_key(self.session, 876543210987654321, 20)
        delete_all(self.session)
        all_emoji_info = get_all_emoji_info(self.session)
        self.assertEqual(len(all_emoji_info), 0)

if __name__ == '__main__':
    unittest.main()
