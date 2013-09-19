import sqlite3
from contextlib import closing
from flask import Flask, request, render_template, redirect, url_for, session, g, abort, flash
import csv
import codecs

#function to connect to db
def connect_db(app):
    return sqlite3.connect(app.config['DATABASE'])

#define a fuction that sets up the database
def init_db(app):
    with closing(connect_db(app)) as db:
        with app.open_resource('schema.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
        with app.open_resource('data.sql') as f:
            db.cursor().executescript(f.read())
        db.commit()
        #put in choices
        with app.open_resource('csv_choices.csv') as f:
            dr = csv.DictReader(f) # comma is default delimiter
            to_db = [(unicode(i['title'], encoding='utf_8'), unicode(i['text'], encoding='utf_8')) for i in dr]        
        db.cursor().executemany("INSERT INTO choices (title, text) VALUES (?, ?);", to_db)
        db.commit()
        #put in attributes
        with app.open_resource('csv_attributes.csv') as f:
            dr = csv.DictReader(f) # comma is default delimiter
            to_db = [(unicode(i['type'], encoding='utf_8'), unicode(i['label'], encoding='utf_8'), unicode(i['level'], encoding='utf_8'), unicode(i['observable'], encoding='utf_8')) for i in dr]        
        db.cursor().executemany("INSERT INTO attributes (type, label, level, observable) VALUES (?, ?, ?, ?);", to_db)
        db.commit()
        #put in choice/attr xref
        with app.open_resource('csv_choice_attribute.csv') as f:
            dr = csv.DictReader(f) # comma is default delimiter
            to_db = [(unicode(i['choice_id'], encoding='utf_8'), unicode(i['attribute_id'], encoding='utf_8')) for i in dr]        
        db.cursor().executemany("INSERT INTO choice_attribute (choice_id, attribute_id) VALUES (?, ?);", to_db)
        db.commit()
        #put in features
        with app.open_resource('csv_features.csv') as f:
            dr = csv.DictReader(f) # comma is default delimiter
            to_db = [(unicode(i['label'], encoding='utf_8'), unicode(i['desc'], encoding='utf_8')) for i in dr]        
        db.cursor().executemany("INSERT INTO features (label, desc) VALUES (?, ?);", to_db)
        db.commit()
        #put in choice/feature xref
        with app.open_resource('csv_choice_feature.csv') as f:
            dr = csv.DictReader(f) # comma is default delimiter
            to_db = [(unicode(i['choice_id'], encoding='utf_8'), unicode(i['feature_id'], encoding='utf_8')) for i in dr]        
        db.cursor().executemany("INSERT INTO choice_feature (choice_id, feature_id) VALUES (?, ?);", to_db)
        db.commit()

def query_db(query, args=(), one=False):
    cur = g.db.execute(query, args)
    rv = [dict((cur.description[idx][0], value)
               for idx, value in enumerate(row)) for row in cur.fetchall()]
    return (rv[0] if rv else None) if one else rv
