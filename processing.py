from flask import Flask, request, render_template, redirect, url_for, session, g, abort, flash
from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUserMixin,
                            confirm_login, fresh_login_required)
from database import *
from user import *
from choice import *
import random
import string
from werkzeug.security import generate_password_hash, check_password_hash

def decision_processing():
    #flash('Doing a bunch of stuff here')
    proc_type = query_db('select distinct type from procedures')
    complete = 'O'
    if int(request.form['choice']) == 1:
        complete = 'N'
    g.db.execute('insert into user_choice (user_id, choice_id, round, support, complete, final_value, resources_spent) values (?, ?, ?, ?, ?, ?, ?)',
                 [current_user.id, request.form['choice'], session['round'], request.form['support'], complete, 0, 0])
    if int(request.form['choice']) != 1:
        for proc in proc_type:
            g.db.execute('insert into user_choice_proc (user_id, round, procedure_id) values (?, ?, ?)',
                         [current_user.id, session['round'], request.form[proc['type']]])
    completion_processing()
    g.db.commit()
    session['round'] = session['round'] + 1
    
def completion_processing():
    incomplete = query_db('select * from user_choice WHERE user_id = ? AND complete = ? ORDER BY round',
                          [current_user.id, 'O'])
    worked_on = len(incomplete)
    for decision in incomplete:
        p_fail = .1
        user = User(decision['user_id'])
        choice = UserChoice(user,decision['round'])
        #update the resources spent for each choice
        choice.resources_spent = choice.resources_spent + user.get_resources()/float(worked_on)
        g.db.execute('update user_choice SET resources_spent = ? WHERE id = ?',
                    [choice.resources_spent, decision['id']])
        g.db.commit()
        #round_complete = choice.round + choice.time_to_implement() - 1
        #Check if failed before check if complete
        if choice.fail(p_fail) == 1:
            g.db.execute('update user_choice SET complete = ?, complete_round = ?, final_value = ? WHERE id = ?',
                         ['F', session['round'], choice.get_value(), decision['id']])
            g.db.commit()
        elif choice.resources_spent >= choice.resources_to_implement():
            g.db.execute('update user_choice SET complete = ?, complete_round = ?, final_value = ? WHERE id = ?',
                         ['C', session['round'], choice.get_value(), decision['id']])
            for feature in choice.features:
                if user.product.count(feature)==0:
                    user.update_product(feature)
                    #flash('Your product now has a new feature!', 'feature')
            #Need to insert/update experience levels for each attribute
            for attr in choice.get_attributes():
                experience = current_user.attr_experience(attr)
                if experience == 0:
                    g.db.execute('insert into attr_experience (user_id, attribute_id, experience) values (?,?,?)',
                                 [current_user.id, attr['attribute_id'], 1])
                else:
                    experience = experience + 1
                    g.db.execute('update attr_experience SET experience = ? WHERE user_id = ? AND attribute_id = ?',
                                 [experience, current_user.id, attr['attribute_id']])
            g.db.commit()

def choose_options():
    """This function should return a list of 3 choices to be displayed based on some criteria"""
    random.seed()
    if session['round'] == 1:
        to_display = [7, 9, 12]
    else:
        all_choices = []
        user_choices = []
        displayed_choices = []
        weighted_choice = []
        cur1 = query_db('select id from choices where id <> ?',
                               [1])
        for choice in cur1:
            all_choices.append(choice['id'])
        cur2 = query_db('select choice_id from user_choice where user_id = ?',
                        [current_user.id])
        for choice in cur2:
            user_choices.append(choice['choice_id'])
        cur3 = query_db('select choice_id from choice_display where user_id = ? AND round = ?',
                        [current_user.id, (session['round'] - 1)])
        for choice in cur3:
            displayed_choices.append(choice['choice_id'])
        choice_set = set(all_choices) - set(user_choices)
        for choice in choice_set:
            #For each choice the weight is the experience of the user + a factor if the choice was previously displayed
            if choice in displayed_choices:
                factor = 2
            else:
                factor = 1
            weight = current_user.experience_with(Choice(choice))
            if weight == 0: #user has no experience
                weight = factor
            else:
                weight = weight*factor
            for x in range(weight):
                weighted_choice.append(choice)
        #Generete a list of 3 choices
        to_display = random.sample(weighted_choice,3)
        #Deal with duplicates
        while len(set(to_display)) <> 3:
            to_display = list(set(to_display))
            to_display = to_display + random.sample(weighted_choice,(3-len(to_display)))
    choices = [Choice(to_display[0]), Choice(to_display[1]), Choice(to_display[2])]
    #insert choices into choice display
    for choice in to_display:
        g.db.execute('insert into choice_display (user_id, choice_id, round) values (?, ?, ?)',
                    [current_user.id, choice, session['round']])
    g.db.commit()
    return choices

def str_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))

def newUserProcessing():
    #seed random number generator
    random.seed()
    #generate a random password
    password = str_generator()
    #hash password
    user_hash = generate_password_hash(password)
    #randomly assign to condition
    condition = str_generator(1,"CAMTU")
    #insert user
    cur = g.db.cursor()
    cur.execute('insert into users (password, active_flag, treatment) values (?, ?, ?)',
                 [user_hash, 1, condition])
    userID = cur.lastrowid
    g.db.commit()
    #insert user/feature combos
    features = [1, 2, 9, 10]
    for feature in features:
        g.db.execute('insert into user_feature (user_id, feature_id) values (?, ?)',
                    [userID, feature])
    g.db.commit()
    #pass user/password back
    return {'userID':userID, 'password':password}
            
