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
        {'href': '/aboutme', 'caption': 'About Me'},
        {'href': '/test', 'caption': 'Test'},
    ]
    return {'navigation': navitems}

@app.route('/')
def index():
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"))

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html', title="MLH Fellow - Hobbies", url=os.getenv("URL"))

@app.route('/aboutme')
def aboutme():
    return render_template('aboutme.html', title="MLH Fellow - About Me", url=os.getenv("URL"))
