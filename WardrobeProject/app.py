from flask import Flask, render_template, redirect, url_for
from flask import session, request
from flask_wtf import FlaskForm

import sqlite3
import os

from wtforms import SelectField, StringField, SubmitField, SelectMultipleField
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
                      user_username TEXT UNIQUE NOT NULL,
                      user_password TEXT NOT NULL,
                      user_first_name TEXT,
                      user_last_name TEXT
                      );

                      CREATE TABLE IF NOT EXISTS Wardrobe (
                      wardrobe_name TEXT PRIMARY KEY,
                      user_id INTEGER REFERENCES User(user_id)
                      );

                      CREATE TABLE IF NOT EXISTS Outfit (
                      outfit_name TEXT,
                      item_id INTEGER REFERENCES Item(item_id),
                      user_id INTEGER REFERENCES User(user_id)
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
    wardrobe_name = StringField("Enter name for your new Wardrobe!", validators=[DataRequired()])
    submit = SubmitField("Submit")

class MoveItemForm(FlaskForm):
    wardrobe_name = SelectField("Select new wardrobe for item", choices = [])
    submit = SubmitField("Submit")

class OutfitForm(FlaskForm):
    outfit_name = StringField("Enter name for your new outfit!", validators=[DataRequired()])
    items = SelectMultipleField("Pick items for this outfit", coerce=int, choices=[])
    submit = SubmitField("Submit")

class LoginForm(FlaskForm):
    username = StringField("Username", validators=[DataRequired()])
    password = StringField("Password", validators=[DataRequired()])
    submit = SubmitField("Login/Sign Up")

@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data

        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            username_password = cur.execute("SELECT user_id, user_password FROM User WHERE user_username = ?", (username,)).fetchone()

            if username_password:
                if username_password[1] == password:
                    session['user_id'] = username_password[0]
                    session['username'] = username
                    return redirect(url_for('home'))
                else:
                    return "Incorrect password!"
            else:
                cur.execute("INSERT INTO User(user_username, user_password) VALUES (?, ?)", (username, password))
                session['user_id'] = cur.lastrowid
                session['username'] = username
                return redirect(url_for('home'))

        return redirect(url_for('home'))
        
    return render_template("login.html", form=form)
    
@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route("/")
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    return render_template("home.html")

@app.route("/addItem", methods=["GET", "POST"])
def addItem():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    form = ItemForm()
    user_id = session['user_id']

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT wardrobe_name FROM Wardrobe WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()

    form.wardrobe_name.choices = [(row[0], row[0]) for row in rows]

    if form.validate_on_submit():
        try:
            with sqlite3.connect(DB_PATH) as conn:
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
        return redirect(url_for('allItems'))

    return render_template("form.html", form=form)


@app.route("/addWardrobe", methods=["GET", "POST"])
def addWardrobe():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    form = WardrobeForm()

    if form.validate_on_submit():
        wardrobe_name = form.wardrobe_name.data
        try:
            with sqlite3.connect(DB_PATH) as conn:
                cur = conn.cursor()
                cur.execute("""
                            INSERT INTO Wardrobe (wardrobe_name, user_id) 
                            VALUES (?, ?);
                            """, (wardrobe_name, user_id))
                print("added new wardrobe successfully")
        except sqlite3.IntegrityError:
            return "error: wardrobe with chosen name already exists"
        return redirect(url_for('home'))

    return render_template("wardrobe_form.html", form=form)

@app.route("/allItems", methods=["GET", "POST"])
def allItems():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        cur.execute("""
                    SELECT *
                    FROM Item
                    WHERE user_id = ?;
                    """, (user_id,))
        
        rows = cur.fetchall()
    return render_template("all_items.html", rows = rows)

#only route with parameter!
@app.route("/moveItem/<int:item_id>", methods=["GET", "POST"])
def moveItem(item_id):
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    form = MoveItemForm()

    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM Item WHERE item_id = ? AND user_id = ?", (item_id, user_id))
        #getting our item
        item = cur.fetchone()

        wardrobe_names = cur.execute("SELECT wardrobe_name FROM Wardrobe WHERE wardrobe_name != ? AND user_id = ?", (item['wardrobe_name'], user_id)).fetchall()

        form.wardrobe_name.choices = [(row[0], row[0]) for row in wardrobe_names]

    if form.validate_on_submit():
        new_wardrobe = form.wardrobe_name.data
        with sqlite3.connect(DB_PATH) as conn:
            cur = conn.cursor()
            cur.execute("UPDATE Item SET wardrobe_name = ? WHERE item_id = ?", (new_wardrobe, item_id))

        return redirect(url_for('allItems'))

    return render_template("move_form.html", item = item, form = form)

@app.route("/createOutfit", methods=["GET", "POST"])
def createOutfit():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']

    form = OutfitForm()

    with sqlite3.connect(DB_PATH) as conn:
        cur = conn.cursor()
        cur.execute("SELECT item_id, item_name FROM Item WHERE user_id = ?", (user_id,))
        rows = cur.fetchall()

    form.items.choices = [(row[0], row[1]) for row in rows]

    if form.validate_on_submit():
        try:
            with sqlite3.connect(DB_PATH) as conn:
                outfit_name = form.outfit_name.data
                item_ids = form.items.data

                cur = conn.cursor()
                for item_id in item_ids:
                    cur.execute("""
                                INSERT INTO Outfit
                                (outfit_name, item_id, user_id)
                                VALUES
                                (?, ?, ?);
                                """, (outfit_name, item_id, user_id))
                print("added outfit successfully")
        except sqlite3.IntegrityError as e:
            print(f"error: {e}")
            return "error: outfit with chosen name already exists"
        return redirect(url_for('home'))
    return render_template("outfit_form.html", form=form)

@app.route("/allOutfits")
def allOutfits():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    user_id = session['user_id']
    
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()

        outfit_names = cur.execute("SELECT DISTINCT outfit_name FROM Outfit WHERE user_id = ?", (user_id,)).fetchall()

        all_entries = cur.execute("""
                                  SELECT Outfit.outfit_name, Item.item_name
                                  FROM Outfit JOIN Item
                                  ON Outfit.item_id = Item.item_id
                                  WHERE Outfit.user_id = ?;
                                  """, (user_id,)).fetchall()
    return render_template("all_outfits.html", outfit_names = outfit_names, all_entries = all_entries)

if __name__ == "__main__":
    app.run(use_debugger=True)