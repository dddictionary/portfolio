import os

from dotenv import load_dotenv  # type: ignore
from flask import Flask, render_template, request  # type: ignore

load_dotenv()
app = Flask(__name__)

@app.context_processor
def nav_items():
    navitems = [
        {'href': '/', 'caption': 'About'},
        # {'href': '/aboutme', 'caption': 'About Me'},
        {'href': '/work', 'caption': 'Work Experiences'},
        {'href': '/hobbies', 'caption': 'Hobbies'},
        {'href': '/education', 'caption': 'Education'},
        {'href': '/travels', 'caption': 'Travels'},
    ]
    return {'navigation': navitems}

@app.context_processor
def hobby_items():
    hobbyitems = [
        {
            'title': 'Roblox',
            'description': 'I love playing roblox it is so fun and I do this all day',
            'source': 'https://i.pinimg.com/originals/37/07/a7/3707a7cd7d384511c213b2a12dc3f0a7.jpg'
        },
        {
            'title': 'Mountain Climbing', 
            'description': 'There is nothing like climbing up a cliff-side on a hot sunny day with my VR', 
            'source': 'https://i.ytimg.com/vi/xAYuh4NQVeE/maxresdefault.jpg'
        },
        {
            'title': 'Lorem', 
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.', 
            'source': 'https://dummyimage.com/500x500/ffffff/000000'
        },
        {
            'title': 'Lorem', 
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.', 
            'source': 'https://dummyimage.com/500x500/ffffff/000000'
        },
        {
            'title': 'Lorem', 
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.', 
            'source': 'https://dummyimage.com/500x500/ffffff/000000'
        },
        {
            'title': 'Lorem', 
            'description': 'Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua. Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat. Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla pariatur.', 
            'source': 'https://dummyimage.com/500x500/ffffff/000000'
        },
    ]
    return {'hobbies': hobbyitems}

@app.context_processor
def work_experiences():
    work_data = [
        {
            'title': 'Apple',
            'role': 'Full-stack Developer',
            'startdate': 'Jan 2023',
            'enddate': 'Present',
            'description': 'Ate apples all day and removed oranges from the restrooms every night. Blockchain bananas.'
        },
        {
            'title': 'Google',
            'role': 'Front-end Specialist',
            'startdate': 'Jul 2021',
            'enddate': 'Dec 2022',
            'description': 'Used Google search 10000 times to search up how to create a website'
        },
        {
            'title': 'Meta',
            'role': 'Mobile App Intern',
            'startdate': 'May 2021',
            'enddate': 'Aug 2021',
            'description': 'Assisted in the development of a mobile application for inventory management. Probably gained experience with mobile development frameworks and agile methodologies.'
        }
    ]
    return {'work': work_data}

@app.context_processor
def education_experiences():
    education_data = [
        {
            'title': 'Generic High School',
            'startdate': 'Sep 2018',
            'enddate': 'June 2022',
            'description': 'Acted in a musical, you might have heard of it.'
        },        
        {
            'title': "Monster's University",
            'startdate': 'Aug 2022',
            'enddate': 'May 2026',
            'description': "Learned to scare children and the effects of their fear on our world's ecosystem" 
        }        
    ]
    return {'education': education_data}

@app.context_processor
def travel_experiences():
    locations = [
        {"name": "Paris, France", "lat": 48.8566, "lng": 2.3522},
        {"name": "New York, USA", "lat": 40.7128, "lng": -74.0060},
        {"name": "Tokyo, Japan", "lat": 35.6895, "lng": 139.6917},
        {"name": "London, UK", "lat": 51.5074, "lng": -0.1278},
        {"name": "Los Angeles, USA", "lat": 34.0522, "lng": -118.2437},
        {"name": "São Paulo, Brazil", "lat": -23.5505, "lng": -46.6333},
        {"name": "Cairo, Egypt", "lat": 30.0444, "lng": 31.2357},
        {"name": "Dubai, UAE", "lat": 25.2048, "lng": 55.2708},
        {"name": "Istanbul, Turkey", "lat": 41.0082, "lng": 28.9784},
        {"name": "Bangkok, Thailand", "lat": 13.7563, "lng": 100.5018},
        {"name": "Seoul, South Korea", "lat": 37.5665, "lng": 126.9780},
        {"name": "Sydney, Australia", "lat": -33.8688, "lng": 151.2093},
        {"name": "Mexico City, Mexico", "lat": 19.4326, "lng": -99.1332}
    ]
    return {'locations': locations}

@app.route('/')
def index():
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"))

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html', title="MLH Fellow - Hobbies", url=os.getenv("URL"))

@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html', title="MLH Fellow - About Me", url=os.getenv("URL"))

@app.route('/work')
def work():
    return render_template('work.html', title="MLH Fellow - Work Experiences", url=os.getenv("URL"))

@app.route('/education')
def education():
    return render_template('education.html', title="MLH Fellow - Education", url=os.getenv("URL"))

@app.route('/travels')
def travels():
    return render_template('travel.html', title="MLH Fellow - Travels", url=os.getenv("URL"))

