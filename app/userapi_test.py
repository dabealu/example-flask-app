import unittest
from userapi import app

class TestApp(unittest.TestCase):

    def setUp(self):
        self.app = app.test_client()

    def test_index(self):
        response = self.app.get('/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, b'Hi :D ')

    def test_create_table(self):
        response = self.app.get('/create_table')
        self.assertEqual(response.status_code, 200)

    def test_add_user(self):
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'pwd': 'testpwd'
        }
        response = self.app.post('/create', json=data)
        self.assertEqual(response.status_code, 200)

    def test_get_users(self):
        response = self.app.get('/users')
        self.assertEqual(response.status_code, 200)

    def test_get_user(self):
        response = self.app.get('/user/1')
        self.assertEqual(response.status_code, 200)

    def test_update_user(self):
        data = {
            'user_id': 1,
            'name': 'Updated User',
            'email': 'updated@example.com',
            'pwd': 'updatedpwd'
        }
        response = self.app.post('/update', json=data)
        self.assertEqual(response.status_code, 200)

    def test_delete_user(self):
        response = self.app.get('/delete/1')
        self.assertEqual(response.status_code, 200)

if __name__ == '__main__':
    unittest.main()
