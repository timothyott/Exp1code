from flask.ext.login import (LoginManager, current_user, login_required,
                            login_user, logout_user, UserMixin, AnonymousUser,
                            confirm_login, fresh_login_required)
from database import *
from choice import *

#User stuff
class User(UserMixin):
    def __init__(self, user_id):
        user = query_db('select user_id, password, active_flag from users where user_id = ?', [user_id], one=True)
        if user:
            self.id = user_id
            self.active = user['active_flag']
            self.password = user['password']
            self.exists = True
            self.set_product()
        else:
            self.exists = False

    def is_active(self):
        return self.active

    def set_product(self):
        self.product = []
        product = query_db('select feature_id from user_feature where user_id = ?', [self.id])
        for feature in product:
            self.product.append(feature['feature_id']) 
        return self.product.sort()

    def update_product(self, feature):
        g.db.execute('insert into user_feature (user_id, feature_id) values (?, ?)',
                 [self.id, feature])
        self.product.append(feature)
        return self.product.sort()

    def product_desc(self):
        temp = str(self.product).strip('[]')
        description = query_db('select label, desc from features WHERE id IN ('+temp+')',
                               [])
        return description

    #def is_authenticated(self):
        #return True

    def get_last_choice(self):
        user_choice = None
        last_round = query_db('select max(round) AS round from user_choice WHERE user_id=?',
                              [self.id], one=True)
        if not last_round['round']:
            return None
        else:
            user_choice = UserChoice(self,last_round['round'])
            return user_choice

    def get_choices(self, complete, cur_round):
        choices = []
        if complete == 'O':
            cur = query_db('select round from user_choice where user_id=? AND complete=?',
                           [self.id, complete])
        else:
            cur = query_db('select round from user_choice where user_id=? AND complete=? AND complete_round=?',
                           [self.id, complete, cur_round])
        for choice in cur:
            choices.append(UserChoice(self, choice['round']))
        return choices

    def get_value(self):
        value = 0
        cur = query_db('select final_value from user_choice where user_id = ? and complete=?',
                       [self.id, 'C'])
        for x in cur:
            value = value + x['final_value']
        return value

    def get_resources_spent(self):
        spent = 0
        cur = query_db('select resources_spent from user_choice where user_id = ? and complete=?',
                       [self.id, 'C'])
        for x in cur:
            spent = spent + x['resources_spent']
        return spent

    def attr_experience(self, attr):
        value = 0
        exps = query_db('select experience from attr_experience WHERE user_id = ? AND attribute_id = ?',
                 [self.id, attr['attribute_id']])
        for exp in exps:
            value = value + exp['experience']
        return value

    def experience_with(self, choice):
        attributes = choice.get_attributes()
        value = 0
        for attr in attributes:
            value = value + self.attr_experience(attr)
        #divide by the number of attributes to get the average experience level
        value = value / len(attributes)
        return value

# get the resources
    def get_resources(self):
        resource_base = 5.0
        complete = query_db('select count(*) as num from user_choice WHERE user_id = ? AND complete = ? AND complete_round < ?',
                          [self.id, 'C', session['round']], one=True)
        value = complete['num']
        #costs = self.get_resources_spent()/2 no costs for now, just increase base by completed
        resources = resource_base + value
        return resources

class Anonymous(AnonymousUser):
    name = u"Anonymous"

