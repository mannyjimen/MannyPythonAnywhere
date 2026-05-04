import os

from flask import Flask, render_template
from werkzeug.middleware.dispatcher import DispatcherMiddleware
from werkzeug.serving import run_simple

from lab8.flask_app import app as lab8_app
from lab10.app import app as lab10_app
from lab11.app import app as lab11_app
from WardrobeProject.app import app as wardrobe_app

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route("/")
def home():
    return render_template("index.html")

application = DispatcherMiddleware(app, {
    '/lab8': lab8_app,
    '/lab10': lab10_app,
    '/lab11': lab11_app,
    '/wardrobeProject': wardrobe_app,
})

if __name__ == "__main__":
    run_simple('localhost', 5000, application, use_reloader=True, use_debugger=True)