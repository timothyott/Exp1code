from contextlib import closing
import sqlite3

#function to connect to db
def connect_db():
    return sqlite3.connect(app.config['DATABASE'])

#define a fuction that sets up the database
def init_db():
    with closing(connect_db()) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
