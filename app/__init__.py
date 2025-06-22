import os

from dotenv import load_dotenv  # type: ignore
from flask import Flask, render_template, request  # type: ignore

load_dotenv()
app = Flask(__name__)

@app.context_processor
def nav_items():
    navitems = [
        {'href': '/', 'caption': 'About'},
        {'href': '/hobbies', 'caption': 'Hobbies'},
        {'href': '/test', 'caption': 'Test'},
        {'href': '/work', 'caption': 'Work Experiences'},
    ]
    return {'navigation': navitems}

@app.route('/')
def index():
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"))

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html', title="MLH Fellow - Hobbies", url=os.getenv("URL"))

@app.route('/work')
def work():
    return render_template('work.html', title="MLH Fellow - Work Experiences", url=os.getenv("URL"))


