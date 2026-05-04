from flask import Flask, render_template, redirect, url_for
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, Email
import sqlite3
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Secret Key'

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mydatabase.db")

conn = sqlite3.connect("mydatabase.db")
cur = conn.cursor()

def init_db():
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS Users (
            users_id INTEGER PRIMARY KEY,
            users_first_name TEXT NOT NULL,
            users_last_name TEXT NOT NULL,
            users_email TEXT NOT NULL UNIQUE,
            users_college TEXT
        );
        """)
    
init_db()
print("just execed script")

class UserForm(FlaskForm):
    users_first_name = StringField("First Name", validators=[DataRequired()])
    users_last_name = StringField("Last Name", validators=[DataRequired()])
    users_email = StringField("Email", validators=[DataRequired(), Email()])
    users_college = StringField("College Name")
    submit = SubmitField("Submit")


@app.route("/", methods=["GET", "POST"])
def index():
    form = UserForm()

    if form.validate_on_submit():

        users_first_name = form.users_first_name.data
        users_last_name = form.users_last_name.data
        users_email = form.users_email.data
        users_college = form.users_college.data

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        try:
            cursor.execute('''
                INSERT INTO Users (
                    users_first_name,
                    users_last_name,
                    users_email,
                    users_college
                )
                VALUES (?, ?, ?, ?)
            ''', (users_first_name, users_last_name, users_email, users_college))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.close()
            return "Error: This email is already registered."
        conn.close()
        return redirect(url_for("success", name=users_first_name))
    return render_template("form.html", form=form)


@app.route("/users")
def users():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    users = conn.execute("SELECT * FROM Users").fetchall()
    conn.close()

    return "<br>".join([
        f"""{u['users_first_name']} {u['users_last_name']} -
        {u['users_email']} ({u['users_college']})"""
        for u in users
    ])

@app.route("/success/<name>")
def success(name):
    return f"{name} was added to the database."

if __name__ == "__main__":
    app.run(debug=True)
