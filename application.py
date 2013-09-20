# Notes on where I am
#imports
import sqlite3 
from contextlib import closing
from processing import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask import Flask, request, render_template, redirect, url_for, session, g, abort, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)
from database import *
from user import *
from choice import *

# create our little application :)
#adding a comment to make sure this changes take.
application = Flask(__name__)
application.config.from_pyfile('config.py')
application.secret_key = application.config['SECRET_KEY']

#Set the debug mode
application.debug = True

#function to connect to db
        
#db functions from example
@application.before_request
def before_request():
    g.db = connect_db(application)

@application.teardown_request
def teardown_request(exception):
    g.db.close()

login_manager = LoginManager()
login_manager.init_app(application)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    user = query_db('select user_id, password, active_flag from users where user_id = ?', [user_id], one=True)
    if user:
        return User(user['user_id'])
    else:
        return None

# The actual app 
@application.route('/')
def index():
    return redirect(url_for('login'))

@application.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    user_hash = None
    if request.method == 'POST':
        user = User(request.form['userID'])
        user_hash = generate_password_hash(request.form['password'])
        if not user.exists:
            error = 'Invalid User ID'
        elif not check_password_hash(user.password,request.form['password']):
            error = 'Invalid User ID / Password combination'
        else:
            if login_user(user):
                session['round'] = 1
                #flash('You were logged in')
                return redirect(url_for('instructions'))
    return render_template('login.html', error=error, user_hash=user_hash)

@application.route('/logout')
def logout():
    logout_user()
    flash('You were logged out')
    return redirect(url_for('login'))

@application.route('/instructions', methods=['GET','POST'])
@login_required
def instructions():
    flash('Welcome user ' + str(current_user.id) + '!')
    prior_choice = current_user.get_last_choice()
    if prior_choice:
        flash('You have already made some decisions. Your last decision was in round ' + str(prior_choice.round) + '. You chose ' + prior_choice.title)
        session['round'] = prior_choice.round + 1
    #Get proc infor for instructions.
    proc_type = query_db('select distinct type from procedures')
    proc_name = dict()
    for proc in proc_type:
        proc_option = query_db('select id, type, label, desc from procedures WHERE type = ? order by id asc',
                                   [proc['type']])
        proc_name[proc['type']] =  proc_option
    return render_template('intro.html', proc_name=proc_name)

@application.route('/choices', methods=['GET','POST'])
@login_required
def display_choices():
    choices = choose_options()
    proc_type = query_db('select distinct type from procedures')
    proc_name = dict()
    for proc in proc_type:
        proc_option = query_db('select id, type, label, desc from procedures WHERE type = ? order by id asc',
                                   [proc['type']])
        proc_name[proc['type']] =  proc_option
    return render_template('choices.html', choices=choices, proc_name=proc_name)

@application.route('/make_choice', methods=['POST'])
@login_required
def make_choice():  
    decision_processing()
    flash('Choice was successfully made')
    return redirect(url_for('review_choice'))

@application.route('/review_choice', methods=['GET'])
@login_required
def review_choice():
    choice_info = current_user.get_last_choice()
    ongoing = current_user.get_choices('O', session['round']-1)
    complete = current_user.get_choices('C', session['round']-1)
    failed = current_user.get_choices('F', session['round']-1)
    return render_template('review.html', user_choice=choice_info, ongoing=ongoing, complete=complete, failed=failed)

@application.route('/exit_survey', methods=['GET','POST'])
@login_required
def exit_survey():
    return render_template('exit_survey.html')

if __name__ == '__main__':
    init_db(application)
    application.run(host='0.0.0.0')
#Add host='0.0.0.0' to the run command to make it open to the world.
