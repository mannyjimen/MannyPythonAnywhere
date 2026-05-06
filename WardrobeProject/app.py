from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm

import sqlite3
import os

from wtforms import SelectField, StringField, SubmitField, BooleanField
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

                      DROP TABLE IF EXISTS Item;
                      DROP TABLE IF EXISTS Wardrobe;
                      DROP TABLE IF EXISTS User;
                      DROP TABLE IF EXISTS Category;
                      DROP TABLE IF EXISTS Brand;
                      DROP TABLE IF EXISTS Color;

                      CREATE TABLE User (
                      user_id INTEGER PRIMARY KEY,
                      user_first_name TEXT,
                      user_last_name TEXT
                      );

                      CREATE TABLE Category (
                      category_name TEXT PRIMARY KEY
                      );

                      INSERT INTO Category (category_name)
                      VALUES
                      ('Shirt'),
                      ('Hoodie'),
                      ('Sweater'),
                      ('Pants'),
                      ('Shorts'),
                      ('Socks'),
                      ('Other');

                      CREATE TABLE Brand (
                      brand_name TEXT PRIMARY KEY
                      );

                      INSERT INTO Brand (brand_name)
                      VALUES
                      ('Nike'),
                      ('Adidas'),
                      ('Reebok'),
                      ('H&M'),
                      ('Hollister'),
                      ('Uniqlo'),
                      ('Other');

                      CREATE TABLE Color (
                      color_name TEXT PRIMARY KEY
                      );

                      INSERT INTO Color (color_name)
                      VALUES
                      ('Black'),
                      ('White'),
                      ('Grey'),
                      ('Red'),
                      ('Blue'),
                      ('Green'),
                      ('Brown'),
                      ('Other');

                      CREATE TABLE Wardrobe (
                      wardrobe_name VARCHAR PRIMARY KEY
                      );

                      CREATE TABLE Item (
                      item_id INTEGER PRIMARY KEY,
                      user_id INTEGER REFERENCES User(user_id),
                      item_name TEXT NOT NULL UNIQUE,
                      wardrobe_name TEXT REFERENCES Wardrobe(wardrobe_name),
                      category_name TEXT REFERENCES Category(category_name),
                      brand_name TEXT REFERENCES Brand(brand_name),
                      color_name TEXT REFERENCES Color(color_name)
                      );
                      """)

init_db()

class ItemForm(FlaskForm):
    user_id = 0
    item_name = StringField("Item Name", validators=[DataRequired()])

    #this select field neeeds a query
    wardrobe_name = StringField("Select Wardrobe")
    
    #these can get away without query since constant list always
    category_name = SelectField("Select Category", choices=[('Shirt', 'Shirt'), \
                                                            ('Hoodie', 'Hoodie'), \
                                                            ('Sweater', 'Sweater'), \
                                                            ('Pants', 'Pants'), \
                                                            ('Shorts', 'Shorts'), \
                                                            ('Socks', 'Socks'), \
                                                            ('Other', 'Other')])
    
    brand_name = SelectField("Select Brand", choices=[('Nike', 'Nike'), \
                                                            ('Adidas', 'Adidas'), \
                                                            ('Reebok', 'Reebok'), \
                                                            ('H&M', 'H&M'), \
                                                            ('Hollister', 'Hollister'), \
                                                            ('Uniqlo', 'Uniqlo'), \
                                                            ('Other', 'Other')])
    
    color_name = SelectField("Select Color", choices=[('Black', 'Black'), \
                                                            ('White', 'White'), \
                                                            ('Grey', 'Grey'), \
                                                            ('Red', 'Red'), \
                                                            ('Blue', 'Blue'), \
                                                            ('Green', 'Green'), \
                                                            ('Brown', 'Brown'), \
                                                            ('Other', 'Other')])

    submit = SubmitField("Submit")

class WardrobeForm(FlaskForm):
    wardrobe_name = StringField("Enter name for your new Wardrobe!")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    form = ItemForm()

    # if form.validate_on_submit():
    #     return redirect(url_for("/"))
    return render_template("form.html", form=form)

if __name__ == "__main__":
    app.run(use_debugger=True)