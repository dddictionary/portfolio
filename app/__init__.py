import datetime
import os
import re

import requests
from dotenv import load_dotenv  # type: ignore
from flask import Flask, Response, jsonify, render_template, request  # type: ignore
from peewee import *
from playhouse.shortcuts import model_to_dict

load_dotenv()
app = Flask(__name__)

if os.getenv("TESTING") == "true":
    print("Running in test mode")
    mydb = SqliteDatabase("file:memory?mode=memory&cache=shared", uri=True)
else:
    mydb = MySQLDatabase(
        os.getenv("MYSQL_DATABASE"),
        user=os.getenv("MYSQL_USER"),
        password=os.getenv("MYSQL_PASSWORD"),
        host=os.getenv("MYSQL_HOST"),
        port=3306,
    )

print(mydb)


class TimelinePost(Model):
    name = CharField()
    email = CharField()
    content = TextField()
    created_at = DateTimeField(default=datetime.datetime.now)

    class Meta:
        database = mydb


mydb.connect()
mydb.create_tables([TimelinePost])


ASTRO_URL = os.environ.get("ASTRO_URL","http://localhost:1234")


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
def proxy(path):
    astro_target_url = f"{ASTRO_URL}/{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=astro_target_url,
            headers={
                key: value for (key, value) in request.headers if key.lower() != "host"
            },
            data=request.get_data(),
            params=request.args,
            allow_redirects=False,
            stream=True,
        )
        excluded_headers = [
            "content-encoding",
            "content-length",
            "transfer-encoding",
            "connection",
        ]
        headers = [
            (key, value)
            for (key, value) in resp.raw.headers.items()
            if key.lower() not in excluded_headers
        ]
        return Response(resp.content, resp.status_code, headers)
    except requests.exceptions.RequestException as e:
        return "error loading astro", 502


@app.context_processor
def nav_items():
    navitems = [
        {"href": "/experience", "caption": "Exp"},
        # {'href': '/aboutme', 'caption': 'About Me'},
        {"href": "/blog", "caption": "Blog"},
        {"href": "/hobbies", "caption": "Hobbies"},
        {"href": "/timeline", "caption": "Timeline"},
        {"href": "/travels", "caption": "Travels"},
    ]
    return {"navigation": navitems}


#
# @app.context_processor
# def hobby_items():
#     hobbyitems = [
#         {
#             'title': 'Roblox',
#             'description': 'I love playing roblox it is so fun and I do this all day',
#             'source': 'https://i.pinimg.com/originals/37/07/a7/3707a7cd7d384511c213b2a12dc3f0a7.jpg'
#         },
#         {
#             'title': 'Mountain Climbing',
#             'description': 'There is nothing like climbing up a cliff-side on a hot sunny day with my VR',
#             'source': 'https://i.ytimg.com/vi/xAYuh4NQVeE/maxresdefault.jpg'
#         },
#         {
#             'title': 'Lorem',
#             'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
#             'source': 'https://dummyimage.com/500x500/ffffff/000000'
#         },
#         {
#             'title': 'Lorem',
#             'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
#             'source': 'https://dummyimage.com/500x500/ffffff/000000'
#         },
#         {
#             'title': 'Lorem',
#             'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
#             'source': 'https://dummyimage.com/500x500/ffffff/000000'
#         },
#         {
#             'title': 'Lorem',
#             'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.',
#             'source': 'https://dummyimage.com/500x500/ffffff/000000'
#         },
#     ]
#     return {'hobbies': hobbyitems}
#
# @app.context_processor
# def work_experiences():
#     work_data = [
#         {
#             'title': 'Apple',
#             'role': 'Full-stack Developer',
#             'startdate': 'Jan 2023',
#             'enddate': 'Present',
#             'description': 'Ate apples all day and removed oranges from the restrooms every night. Blockchain bananas.'
#         },
#         {
#             'title': 'Google',
#             'role': 'Front-end Specialist',
#             'startdate': 'Jul 2021',
#             'enddate': 'Dec 2022',
#             'description': 'Used Google search 10000 times to search up how to create a website'
#         },
#         {
#             'title': 'Meta',
#             'role': 'Mobile App Intern',
#             'startdate': 'May 2021',
#             'enddate': 'Aug 2021',
#             'description': 'Assisted in the development of a mobile application for inventory management. Probably gained experience with mobile development frameworks and agile methodologies.'
#         }
#     ]
#     return {'work': work_data}
#
# @app.context_processor
# def education_experiences():
#     education_data = [
#         {
#             'title': 'Generic High School',
#             'startdate': 'Sep 2018',
#             'enddate': 'June 2022',
#             'description': 'Acted in a musical, you might have heard of it.'
#         },
#         {
#             'title': "Monster's University",
#             'startdate': 'Aug 2022',
#             'enddate': 'May 2026',
#             'description': "Learned to scare children and the effects of their fear on our world's ecosystem"
#         }
#     ]
#     return {'education': education_data}
#
@app.context_processor
def travel_experiences():
    locations = [
        # {"name": "Paris, France", "lat": 48.8566, "lng": 2.3522},
        # {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
        # {"name": "Tokyo, Japan", "lat": 35.6895, "lng": 139.6917},
        # {"name": "London, UK", "lat": 51.5074, "lng": -0.1278},
        {"name": "Los Angeles, USA", "lat": 34.0522, "lng": -118.2437},
        {"name": "Mountain View, USA", "lat": 37.3861, "lng": -122.0839},
        {"name": "San Diego, USA", "lat": 32.7157, "lng": -117.1611},
        {"name": "Merced, USA", "lat": 37.3022, "lng": -120.4830},
        {"name": "Tijuana, Mexico", "lat": 32.5149, "lng": -117.0382},
        {"name": "Boston, USA", "lat": 42.3601, "lng": -71.0589},
        {"name": "Guangdong, China", "lat": 23.1291, "lng": 113.2644},
        # {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333},
        # {"name": "Cairo, Egypt", "lat": 30.0444, "lng": 31.2357},
        # {"name": "Dubai, UAE", "lat": 25.2048, "lng": 55.2708},
        # {"name": "Istanbul, Turkey", "lat": 41.0082, "lng": 28.9784},
        # {"name": "Bangkok, Thailand", "lat": 13.7563, "lng": 100.5018},
        # {"name": "Seoul, South Korea", "lat": 37.5665, "lng": 126.9780},
        # {"name": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
        # {"name": "Mexico City, Mexico", "lat": 19.4326, "lng": -99.1332},
    ]
    return {"locations": locations}


#
# @app.route('/')
# def index():
#     return render_template('index.html', title="Aaron Wu", url=os.getenv("URL"))
#
# @app.route('/hobbies')
# def hobbies():
#     return render_template('hobbies.html', title="MLH Fellow - Hobbies", url=os.getenv("URL"))
#
# @app.route('/aboutme')
# def aboutme():
#     return render_template('aboutme.html', title="MLH Fellow - About Me", url=os.getenv("URL"))
#
# @app.route('/work')
# def work():
#     return render_template('work.html', title="MLH Fellow - Work Experiences", url=os.getenv("URL"))
#
# @app.route('/education')
# def education():
#     return render_template('education.html', title="MLH Fellow - Education", url=os.getenv("URL"))


if os.getenv("TESTING") == "true":
    @app.route("/timeline")
    def timeline():
        return render_template(
            "timeline.html", title="MLH Fellow - Timeline", url=os.getenv("URL")
        )

@app.route("/travels")
def travels():
    return render_template(
        "travel.html", title="Aaron Wu - Travels", url=os.getenv("URL")
    )

    content = request.form["content"]
    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return model_to_dict(timeline_post)


@app.route("/api/timeline_post", methods=["GET"])
def get_time_line_post():
    return {
        "timeline_posts": [
            model_to_dict(p)
            for p in TimelinePost.select().order_by(TimelinePost.created_at.desc())
        ]
    }



@app.context_processor
def timeline_posts_items():
    try:
        data = get_time_line_post()
        return {"timeline_posts": data.get("timeline_posts", [])}
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data, {e}")
        return {"timeline_posts": []}


@app.route("/api/timeline_post", methods=["POST"])
def post_time_line_post():
    name = request.form.get("name")
    email = request.form.get("email")
    content = request.form.get("content")
    if not name:
        return jsonify({"error": "Invalid name"}), 400

    if not email or "@" not in email:
        return jsonify({"error": "Invalid email"}), 400

    if not content:
        return jsonify({"error": "Invalid content"}), 400

    timeline_post = TimelinePost.create(name=name, email=email, content=content)
    return jsonify(model_to_dict(timeline_post))


@app.route("/api/delete_timeline_post/<int:post_id>", methods=["DELETE"])
def delete_time_line_post(post_id):
    try:
        with mydb.connection_context():
            post = TimelinePost.get_by_id(post_id)
            post.delete_instance()
        return "deleted that post"
    except TimelinePost.DoesNotExist:
        return "cant delete what doesnt exist"
    except Exception as e:
        return "error idk what went wrong"
