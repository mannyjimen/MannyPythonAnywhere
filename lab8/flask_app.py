#MANUEL JIMENEZ
#Database Design Maryash
#Lab 08

import os
import sqlite3 
from flask import Flask, render_template

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "mydatabase.db")

conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()

def init_db():
    cur.executescript("""
DROP TABLE IF EXISTS ClubA;
DROP TABLE IF EXISTS ClubB;

CREATE TABLE IF NOT EXISTS ClubA (
                           cluba_id INTEGER PRIMARY KEY,
                           cluba_last_name TEXT,
                           cluba_first_name TEXT,
                           cluba_handicap INTEGER,
                           cluba_member_type TEXT);

CREATE TABLE IF NOT EXISTS ClubB (
                           clubb_id INTEGER PRIMARY KEY,
                           clubb_family_name TEXT,
                           clubb_name TEXT,
                           clubb_handicap INTEGER,
                           clubb_grade TEXT
);
                           
INSERT INTO ClubA (cluba_id, cluba_last_name, cluba_first_name, cluba_handicap, cluba_member_type) VALUES
(176, 'Branch', 'Helen', NULL, 'Social'),
(178, 'Beck', 'Sarah', NULL, 'Social'),
(228, 'Burton', 'Sandra', 26, 'Junior'),
(235, 'Cooper', 'William', 14, 'Senior'),
(239, 'Spence', 'Thomas', 10, 'Senior'),
(258, 'Olson', 'Barbara', 16, 'Senior'),
(286, 'Pollard', 'Robert', 19, 'Junior'),
(290, 'Sexton', 'Thomas', 26, 'Senior');

INSERT INTO ClubB (clubb_id, clubb_family_name, clubb_name, clubb_handicap, clubb_grade) VALUES
(239, 'Spence', 'Thomas', 10, 'Senior'),
(258, 'Olson', 'Barbara', 16, 'Senior'),
(286, 'Pollard', 'Robert', 19, 'Junior'),
(290, 'Sexton', 'Thomas', 26, 'Senior'),
(323, 'Wilcox', 'Daniel', 3, 'Senior'),
(331, 'Schmidt', 'Thomas', 25, 'Senior'),
(332, 'Bridges', 'Deborah', 12, 'Senior'),
(339, 'Young', 'Betty', 21, 'Senior');
                           
-- foreign key enforcement
PRAGMA foreign_keys = ON;

-- clean tables
DROP TABLE IF EXISTS Tournament;
DROP TABLE IF EXISTS Entry;
DROP TABLE IF EXISTS Member;

CREATE TABLE Member (
    member_id INTEGER PRIMARY KEY,
    member_last_name TEXT,
    member_first_name TEXT
);

INSERT INTO Member (member_id, member_last_name, member_first_name) VALUES
(118, 'McKenzie', 'Melissa'),
(138, 'Stone', 'Michael'),
(153, 'Nolan', 'Brenda'),
(176, 'Branch', 'Helen'),
(178, 'Beck', 'Sarah'),
(228, 'Burton', 'Sandra'),
(235, 'Cooper', 'William'),
(239, 'Spence', 'Thomas'),
(258, 'Olson', 'Barbara'),
(286, 'Pollard', 'Robert'),
(290, 'Sexton', 'Thomas'),
(323, 'Wilcox', 'Daniel'),
(331, 'Schmidt', 'Thomas'),
(332, 'Bridges', 'Deborah'),
(339, 'Young', 'Betty'),
(414, 'Gilmore', 'Jane'),
(415, 'Taylor', 'William'),
(461, 'Reed', 'Robert'),
(469, 'Willis', 'Carolyn'),
(487, 'Kent', 'Susan');

CREATE TABLE Entry (
    entry_member_id INTEGER,
    entry_tournament_id INTEGER,
    entry_year INTEGER
);

INSERT INTO Entry (entry_member_id, entry_tournament_id, entry_year) VALUES
(118, 24, 2014),
(228, 24, 2015),
(228, 25, 2015),
(228, 36, 2015),
(235, 38, 2013),
(235, 38, 2015),
(235, 40, 2014),
(235, 40, 2015),
(239, 25, 2015),
(239, 40, 2013),
(258, 24, 2014),
(258, 38, 2014),
(286, 24, 2013),
(286, 24, 2014),
(286, 24, 2015),
(415, 24, 2015),
(415, 25, 2013),
(415, 36, 2014),
(415, 36, 2015),
(415, 38, 2013),
(415, 38, 2015),
(415, 40, 2013),
(415, 40, 2014),
(415, 40, 2015);

CREATE TABLE Tournament (
    tournament_id INTEGER NOT NULL PRIMARY KEY,
    tournament_name TEXT(50) NOT NULL,
    tournament_type TEXT(20) NOT NULL
);

INSERT INTO Tournament (tournament_id, tournament_name, tournament_type) 
VALUES
(24, 'Leeston', 'Social'),
(25, 'Kaiapoi', 'Social'),
(36, 'WestCoast', 'Open'),
(38, 'Canterbury', 'Open'),
(40, 'Otago', 'Open');
                      
                      
                      """)
    
init_db()

@app.route("/") 
def home(): # instead of selfjoin, let's call it home
    return render_template("home.html") 
    # we are not passing data, so we don't need the rows==rows

@app.route("/union") #routes union and not the home page
def union():
    # connect it to the database
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        #execute query
        cur.execute("""
            SELECT * FROM ClubA
            UNION
            SELECT * FROM ClubB;
        """)
        rows = cur.fetchall() #fetch the data
    # returns the data to the template
    return render_template("union.html", rows=rows)

@app.route("/intersection") #routes intersection
def intersection():
    # connect it to the database
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        #execute query
        cur.execute("""
            SELECT * FROM ClubA
            INTERSECT
            SELECT * FROM ClubB;
        """)
        rows = cur.fetchall() #fetch the data
    # returns the data to the template
    return render_template("intersection.html", rows=rows)

@app.route("/difference") #routes difference
def difference():
    # connect it to the database
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        #execute query
        cur.execute("""
            SELECT * FROM ClubA
            EXCEPT
            SELECT * FROM ClubB;
        """)
        rows = cur.fetchall() #fetch the data
    # returns the data to the template
    return render_template("difference.html", rows=rows)

@app.route("/division") #routes division
def division():
    with sqlite3.connect(DB_PATH) as conn:
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("""
            SELECT m.member_last_name, m.member_first_name
            FROM Member m
            WHERE NOT EXISTS (
                SELECT *
                FROM Tournament t
                WHERE NOT EXISTS (
                    SELECT *
                    FROM Entry e
                    WHERE e.entry_member_id = m.member_id
                      AND e.entry_tournament_id = t.tournament_id
                )
            );
        """)
        rows = cur.fetchall()
        print(f"there are {len(rows)} rows in fetchall")
    return render_template("division.html", rows=rows)

if __name__ == "__main__":
    app.run(debug=True)