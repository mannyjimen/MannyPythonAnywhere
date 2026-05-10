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

                      CREATE TABLE IF NOT EXISTS User (
                      user_id INTEGER PRIMARY KEY,
                      user_first_name TEXT,
                      user_last_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Wardrobe (
                      wardrobe_name TEXT PRIMARY KEY
                      );

                      CREATE TABLE IF NOT EXISTS Item (
                      item_id INTEGER PRIMARY KEY,
                      user_id INTEGER REFERENCES User(user_id),
                      item_name TEXT NOT NULL UNIQUE,
                      wardrobe_name TEXT REFERENCES Wardrobe(wardrobe_name),
                      category_name TEXT,
                      brand_name TEXT,
                      color_name TEXT
                      );
                      """)

init_db()

class ItemForm(FlaskForm):
    user_id = 0
    item_name = StringField("Item Name", validators=[DataRequired()])

    #this select field neeeds a query
    wardrobe_name = SelectField("Select Wardrobe", choices = [])
    
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
    submit = SubmitField("Submit")

class MoveItemForm(FlaskForm):
    wardrobe_name = SelectField("Select new wardrobe for item", choices = [])
    submit = SubmitField("Submit")

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    form = ItemForm()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT wardrobe_name FROM Wardrobe")
        rows = cur.fetchall()

    form.wardrobe_name.choices = [(row[0], row[0]) for row in rows]

    if form.validate_on_submit():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                user_id = 0
                item_name = form.item_name.data
                wardrobe_name = form.wardrobe_name.data
                category_name = form.category_name.data
                brand_name = form.brand_name.data
                color_name = form.color_name.data

                cur = conn.cursor()
                cur.execute("""
                            INSERT INTO Item 
                            (user_id, item_name, wardrobe_name, category_name, brand_name, color_name)
                            VALUES (?, ?, ?, ?, ?, ?);""", (user_id, item_name, wardrobe_name, category_name, brand_name, color_name))
                print("added new item successfully")
        except sqlite3.IntegrityError:
            return "error: item with chosen name already exists"
    return render_template("form.html", form=form)


@app.route("/addWardrobe", methods=["GET", "POST"])
def addWardrobe():
    form = WardrobeForm()

    if form.validate_on_submit():
        wardrobe_name = form.wardrobe_name.data
        user_id = 0
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("""
                            INSERT INTO Wardrobe (wardrobe_name) 
                            VALUES (?);
                            """, (wardrobe_name,))
                print("added new wardrobe successfully")
        except sqlite3.IntegrityError:
            return "error: wardrobe with chosen name already exists"

    return render_template("wardrobe_form.html", form=form)

@app.route("/allItems", methods=["GET", "POST"])
def allItems():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
                    SELECT *
                    FROM Item;
                    """)
        
        rows = cur.fetchall()
    return render_template("all_items.html", rows = rows)

#only route with parameter!
@app.route("/moveItem/<int:item_id>", methods=["GET", "POST"])
def moveItem(item_id):
    form = MoveItemForm()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Item WHERE item_id = ?", (item_id,))
        #getting our item
        item = cur.fetchone()

        wardrobe_names = cur.execute("SELECT wardrobe_name FROM Wardrobe WHERE wardrobe_name != ?", (item['wardrobe_name'],)).fetchall()

        form.wardrobe_name.choices = [(row[0], row[0]) for row in wardrobe_names]

    if form.validate_on_submit():
        new_wardrobe = form.wardrobe_name.data
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Item SET wardrobe_name = ? WHERE item_id = ?", (new_wardrobe, item_id))

        return redirect(url_for('allItems'))

    return render_template("move_form.html", item = item, form = form)

def getAllWardrobes():
    cur.execute("SELECT * FROM Wardrobe;")
    return cur.fetchall()

if __name__ == "__main__":
    app.run(use_debugger=True)