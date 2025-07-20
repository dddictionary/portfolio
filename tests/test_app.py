import os
import unittest

os.environ["TESTING"] = "true"

from app import app


class AppTestCase(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_home(self):
        response = self.client.get("/")
        # print(f"Home page status code: {response.status_code}")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "airwu.dev" in html
        # TODO: Add more tests relating to the home page
        assert (
            'He is the result of a kid who fell down a long long rabbit hole when he tried to "hack" Club Penguin that one time many years ago.'
            in html
        )

    def test_timeline(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json
        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        # use the /api/timeline_post endpoint to push a new post then use the get to verify that the len went up by 1
        # TODO: Add more tests relating to the /api/timeline_post GET and POST apis
        post_data = {
            "name": "Test User 1",
            "email": "testuser1@gmail.com",
            "content": "Hey is this thing on?!",
        }
        post_response = self.client.post("/api/timeline_post", data=post_data)
        assert response.status_code == 200
        assert response.is_json
        post_json = post_response.get_json()
        assert "id" in post_json

        # verify that the content is correct and the length went up by 1
        api_response = self.client.get("/api/timeline_post")
        assert api_response.status_code == 200
        assert api_response.is_json
        post_json = api_response.get_json()
        assert "timeline_posts" in post_json
        assert len(post_json["timeline_posts"]) == 1
        timeline_posts = post_json["timeline_posts"]
        fetched_post = {
            "name": timeline_posts[0]["name"],
            "email": timeline_posts[0]["email"],
            "content": timeline_posts[0]["content"],
        }
        assert fetched_post == post_data
        # get the html of the timeline page and assert certain things exist in there
        # TODO: Add more tests relating to the timeline page
        timeline_response = self.client.get("/timeline")
        html = timeline_response.get_data(as_text=True)
        # print(html)

        # TODO: change this as needed. Currently, the timeline page get's post data from the hosted web app on the droplet. If you can change this, I think this test can be reworked better.
        assert post_data["content"] in html

    def test_malformed_timeline_post(self):
        response = self.client.post(
            "/api/timeline_post",
            data={"email": "john@example.com", "content": "Hello world, I'm John!"},
        )
        assert response.status_code == 400
        assert response.is_json
        json = response.get_json()
        print(json)
        assert "Invalid name" in json["error"]

        response = self.client.post(
            "/api/timeline_post",
            data={"name": "John Doe", "email": "john@example.com", "content": ""},
        )
        assert response.status_code == 400
        json = response.get_json()
        assert "Invalid content" in json["error"]

        response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "John Doe",
                "email": "not-an-email",
                "content": "Hello world, I'm John!",
            },
        )
        assert response.status_code == 400
        json = response.get_json()
        assert "Invalid email" in json["error"]
