import unittest
from app import app, db
from flask import json

class TestApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
        self.app.testing = True
        with app.app_context():
            db.create_all()

    def tearDown(self):
        with app.app_context():
            db.session.remove()
            db.drop_all()


    def test_create_test_case(self):
        response = self.app.post('/test_cases', json={
            'name': 'Test Case  1',
            'description': 'This is a test case'
        })
        self.assertEqual(response.status_code,  201)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], 'Test case created')


    def test_get_all_test_cases(self):
        self.app.post('/test_cases', json={
            'name': 'Test Case  1',
            'description': 'This is a test case'
        })
        response = self.app.get('/test_cases')
        self.assertEqual(response.status_code,  200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data),  1)


    def test_update_test_case(self):
        self.app.post('/test_cases', json={
            'name': 'Test Case  1',
            'description': 'This is a test case'
        })
        response = self.app.put('/test_cases/1', json={
            'name': 'Updated Test Case',
            'description': 'Updated description'
        })
        self.assertEqual(response.status_code,  200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], 'Test case updated')

    def test_delete_test_case(self):
        self.app.post('/test_cases', json={
            'name': 'Test Case  1',
            'description': 'This is a test case'
        })
        response = self.app.delete('/test_cases/1')
        self.assertEqual(response.status_code,  200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], 'Test case deleted')

    def test_create_execution_result(self):
        self.app.post('/test_cases', json={
            'name': 'Test Case   1',
            'description': 'This is a test case'
        })
        response = self.app.post('/execution_results', json={
            'test_case_id':   1,
            'asset_name': 'Asset   1',
            'result': 'Passed'
        })
        self.assertEqual(response.status_code,   200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(data['message'], 'ExecutionResult created successfully')
