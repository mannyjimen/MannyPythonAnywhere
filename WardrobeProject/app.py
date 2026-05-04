from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm

import sqlite3
import os

from wtforms import StringField, SubmitField, BooleanField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'wardrobeProject_secret_key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "myWardrobe.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def init_db():
    cur.executescript("""
                      PRAGMA foreign_keys = ON;

                      CREATE TABLE IF NOT EXISTS User (
                      user_id INTEGER PRIMARY KEY,
                      user_first_name TEXT,
                      user_last_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Category (
                      category_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Brand (
                      brand_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Color (
                      color_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Item (
                      item_id INTEGER PRIMARY KEY,
                      user_id INTEGER REFERENCES User(user_id),
                      item_name TEXT NOT NULL UNIQUE,
                      category_name TEXT REFERENCES Category(category_name),
                      brand_name TEXT REFERENCES Brand(brand_name),
                      color_name TEXT REFERENCES Color(color_name),
                      item_is_special BOOLEAN,
                      item_is_dirty BOOLEAN
                      );
                      """)

init_db()

class ItemForm(FlaskForm):
    user_id = 0
    item_name = StringField("Item Name", validators=[DataRequired()])
    category_name = StringField("Category Name")
    brand_name = StringField("Brand Name")
    color_name = StringField("Item Color")
    item_is_special = BooleanField("Is Item Special?")
    item_is_dirty = BooleanField("Is Item Dirty?")
    submit = SubmitField("Submit")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    form = ItemForm()

    # if form.validate_on_submit():
    #     return redirect(url_for("/"))
    return render_template("form.html", form=form)

# @app.route("/allClothing")
# def 

if __name__ == "__main__":
    app.run(use_debugger=True)