import os
from flask import Flask, render_template, request # type: ignore
from dotenv import load_dotenv # type: ignore

load_dotenv()
app = Flask(__name__)

@app.context_processor
def nav_items():
    navitems = [
        {'href': '/', 'caption': 'About'},
        {'href': '/hobbies', 'caption': 'Hobbies'},
        {'href': '/test', 'caption': 'Test'},
        {'href': '/test', 'caption': 'Test'},
    ]
    return {'navigation': navitems}

@app.route('/')
def index():
    return render_template('index.html', title="MLH Fellow", url=os.getenv("URL"))

@app.route('/hobbies')
def hobbies():
    return render_template('hobbies.html', title="MLH Fellow - Hobbies", url=os.getenv("URL"))