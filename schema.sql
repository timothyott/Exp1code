drop table if exists users;
create table users (
    user_id integer primary key autoincrement,
    password not null,
    active_flag bit not null,
    treatment string not null
);

drop table if exists choices;
create table choices (
  id integer primary key autoincrement,
  title string not null,
  text string not null
);
    
drop table if exists attributes;
create table attributes (
    id integer primary key AUTOINCREMENT,
    type string not null,
    label string not null,
    level int,
    observable bit not null
);

drop table if exists procedures;
create table procedures (
    id integer primary key autoincrement,
    type string not null,
    label string not null,
    desc string not null
);

drop table if exists features;
create table features (
    id integer primary key autoincrement,
    label string not null,
    desc string not null
);

drop table if exists user_choice;
create table user_choice (
  id integer primary key autoincrement,
  user_id string not null,
  choice_id integer not null,
  round integer not null,
  support string,
  complete char not null,
  complete_round integer,
  final_value integer,
  resources_spent float,
  FOREIGN KEY(choice_id) REFERENCES choices(id),
  FOREIGN KEY(user_id) REFERENCES users(user_id)
);

drop table if exists choice_display;
create table choice_display (
    user_id string not null,
    choice_id integer not null,
    round integer not null,
    FOREIGN KEY(choice_id) REFERENCES choices(id),
    FOREIGN KEY(user_id) REFERENCES users(user_id)
);

drop table if exists user_choice_proc;
create table user_choice_proc (
    user_id integer not null,
    round integer not null,
    procedure_id integer not null,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(procedure_id) REFERENCES procedures(id)
);    

drop table if exists choice_attribute;
create table choice_attribute (
    choice_id integer not null,
    attribute_id integer not null,
    FOREIGN KEY(choice_id) REFERENCES choices(id),
    FOREIGN KEY(attribute_id) REFERENCES attributes(id)
);

drop table if exists procedure_attribute;
create table procedure_attribute (
    procedure_id integer not null,
    attribute_id integer not null,
    value_effect integer not null,
    time_effect integer not null,
    FOREIGN KEY(procedure_id) REFERENCES procedures(id),
    FOREIGN KEY(attribute_id) REFERENCES attributes(id)
);

drop table if exists choice_feature;
create table choice_feature (
    choice_id integer not null,
    feature_id integer not null,
    FOREIGN KEY(choice_id) REFERENCES choices(id),
    FOREIGN KEY(feature_id) REFERENCES features(id)
);

drop table if exists user_feature;
create table user_feature (
    user_id integer not null,
    feature_id integer not null,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(feature_id) REFERENCES features(id)
);

drop table if exists attr_experience;
create table attr_experience (
    user_id integer not null,
    attribute_id integer not null,
    experience integer not null,
    FOREIGN KEY(user_id) REFERENCES users(user_id),
    FOREIGN KEY(attribute_id) REFERENCES attributes(id)
);

