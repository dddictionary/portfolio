import unittest
import os
os.environ['TESTING'] = 'true'

from app import app

class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()
    
    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "<title>MLH Fellow</title>" in html

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        # assert len(json["timeline_posts"]) == 0

    def test_timeline_page(self):
        response = self.client.get("/timeline")
        html = response.get_data(as_text=True)
        assert "name" in html
        assert "type=\"email\"" in html
        #check if there is a submit button
        assert "type=\"submit\"" in html
    
    def test_correct_timeline_post(self):
        response = self.client.post("/api/timeline_post", data={"name":"john", "email": "john@example.com", "content": "Hello World, I'm John!"})
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "john" in html
        assert "Hello World, I'm John!" in html

    def test_malformed_timeline_post(self):
        # missing name in POST
        response = self.client.post("/api/timeline_post", data={"email": "john@example.com", "content": "Hello World, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html
        
        #empty content in POST
        response = self.client.post("/api/timeline_post", data={"name":"john", "email": "john@example.com", "content": ""})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html

        # malformed email in POST
        response = self.client.post("/api/timeline_post", data={"name":"john", "email": "not-an-email", "content": "Hello World, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html
        