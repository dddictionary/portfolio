import os
import unittest

os.environ["TESTING"] = "true"

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        print(f"Home page status code: {response.status_code}")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "airwu.dev" in html
        # TODO: Add more tests relating to the home page

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        # use the /api/timeline_post endpoint to push a new post then use the get to verify that the len went up by 1
        # TODO: Add more tests relating to the /api/timeline_post GET and POST apis
        # get the html of the timeline page and assert certain things exist in there
        # TODO: Add more tests relating to the timeline page
