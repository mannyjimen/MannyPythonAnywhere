from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret Key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mydatabase.db")

class NameForm(FlaskForm):
    #input name and validates it
    name = StringField("What's your name?", validators=[DataRequired()])
    submit = SubmitField("Submit")

@app.route("/", methods=["GET", "POST"])
def index():
    form = NameForm()
    if form.validate_on_submit():
        name = form.name.data
        return redirect(url_for("success", name=name))
    return render_template("form.html", form=form)

@app.route("/success/<name>")
def success(name):
    return f"{name} was the name submitted."

if __name__ == "__main__":
    app.run(debug=True)