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

