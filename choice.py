from database import *
from numpy.random import binomial

#Choice stuff
class Choice:
    def __init__(self, choice_id):
        choice = query_db('select id, title, text from choices WHERE id = ?', [choice_id], one=True)
        self.id = choice['id']
        self.title = choice['title']
        self.text = choice['text']
        self.set_features()

    def get_attributes(self):
        attr = query_db('select attribute_id, type, label, level, observable from attributes, choice_attribute WHERE attributes.id = choice_attribute.attribute_id AND choice_attribute.choice_id = ?',
                        [self.id])
        return attr

    def get_attribute(self, attr_type):
        attr = query_db('select attribute_id, type, label, level, observable from attributes, choice_attribute WHERE attributes.id = choice_attribute.attribute_id AND choice_attribute.choice_id = ? AND attributes.type=?',
                        [self.id, attr_type], one=True)
        return attr

    def get_obs_attributes(self):
        attr = query_db('select attribute_id, type, label, level, observable from attributes, choice_attribute WHERE attributes.id = choice_attribute.attribute_id AND choice_attribute.choice_id = ? AND attributes.observable = ?',
                        [self.id, 1])
        return attr

    def base_value(self):
        value = 0
        attrs = self.get_attributes()
        for attr in attrs:
            value = value + attr['level']
        return value

    def set_features(self):
        self.features = []
        features = query_db('select feature_id from choice_feature where choice_id = ?', [self.id])
        for feature in features:
            self.features.append(feature['feature_id'])
        return self.features.sort()

    def feature_desc(self):
        temp = str(self.features).strip('[]')
        features = query_db('select label, desc from features WHERE id IN ('+temp+')',
                               [])
        return features

class UserChoice(Choice):
    def __init__(self, user, last_round):
        #this query needs to be longer and be joint with user choice
        choice = query_db('select choices.id as id, choices.title as title, choices.text as text, user_choice.support, user_choice.complete, user_choice.final_value, user_choice.complete_round, user_choice.resources_spent from choices, user_choice WHERE choices.id=user_choice.choice_id AND round=? AND user_id=?',
                            [last_round,user.id], one=True)
        self.id = choice['id']
        self.title = choice['title']
        self.text = choice['text']
        self.round = last_round
        self.user = user
        self.set_features()
        self.complete = choice['complete']
        self.final_value = choice['final_value']
        self.complete_round = choice['complete_round']
        self.resources_spent = choice['resources_spent']

    def get_procs(self):
        if self.title == 'NA':
            choice_proc = []
            for proc in query_db('select distinct type from procedures'):
                choice_proc.append({'type':proc['type'], 'label':'NA', 'desc':'NA'})
        else:
            choice_proc = query_db('select procedure_id, type, label, desc from procedures, user_choice_proc WHERE procedures.id = user_choice_proc.procedure_id AND user_choice_proc.round = ? AND user_choice_proc.user_id = ?',
                                    [self.round,self.user.id])
        return choice_proc
            
    def is_complete(self):
        if self.complete == 'C':
            return True
        else:
            return False
    
    def resources_to_implement(self):
        resource = self.user.get_resources()
        # you need more resources to deal with bigger customers
        attribute = self.get_attribute('Size')
        resource = resource + attribute['level']
        # When you have to do lots of customization it increases the resources needed.
        for feature in self.features:
            if self.user.product.count(feature)==0:
                resource = resource + 1
        for proc in self.get_procs():
            for attr in self.get_attributes():
                proc_effect = query_db('select time_effect from procedure_attribute where procedure_id = ? AND attribute_id = ?',
                                       [proc['procedure_id'], attr['attribute_id']], one=True)
                if proc_effect:
                    resource = resource + proc_effect['time_effect']
        #subtract off the experience with choices of this type
        resource = resource - self.user.experience_with(Choice(self.id))
        return resource

    def get_value(self):
        proc_value = self.base_value()
        for proc in self.get_procs():
            for attr in self.get_attributes():
                proc_effect = query_db('select value_effect from procedure_attribute where procedure_id = ? AND attribute_id = ?',
                                       [proc['procedure_id'], attr['attribute_id']], one=True)
                if proc_effect:
                    proc_value = proc_value + proc_effect['value_effect']
        return proc_value

    def time_spent(self):
        if self.complete == 'C':
            return self.complete_round - self.round
        else:
            return session['round'] - self.round
    
    def fail(self, p_fail):
        """Returns 1 if the project has is computed to have failed, else 0"""
        p_f = p_fail*self.time_spent()/2
        fails = binomial(n=1, p=p_f)
        return fails

    def update_resources_spent(self, dec_id):
        incomplete = query_db('select count(*) as num from user_choice WHERE user_id = ? AND complete = ? ORDER BY round',
                          [self.user.id, 'O'], one=True)
        complete = query_db('select count(*) as num from user_choice WHERE user_id = ? AND complete = ? and complete_round = ? ORDER BY round',
                          [self.user.id, 'C', session['round']], one=True)
        failed = query_db('select count(*) as num from user_choice WHERE user_id = ? AND complete = ? and complete_round = ? ORDER BY round',
                          [self.user.id, 'F', session['round']], one=True)
        worked_on = incomplete['num'] + complete['num'] +failed['num']
        print worked_on
        new_spent = self.resources_spent + self.user.get_resources()/worked_on
        print new_spent
        print self.resources_spent
        print self.user.get_resources()
        g.db.execute('update user_choice SET resources_spent = ? WHERE id = ?',
                         [new_spent, dec_id])
        g.db.commit()
        self.resources_spent = new_spent
        return new_spent

        
        
