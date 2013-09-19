insert into choices (title, text) values ('NA','No Action');

insert into procedures (type, label, desc) values ('Channels', 'Grassroots', 'Get users (tenants) first then approach where they live');
insert into procedures (type, label, desc) values ('Channels', 'Direct selling', 'Send a sales person to approach the landlord');
insert into procedures (type, label, desc) values ('Channels', 'Partner', 'Approach a vendor that already does business with the landlord');
insert into procedures (type, label, desc) values ('Pricing', 'Per unit', 'Price per apartment or house');
insert into procedures (type, label, desc) values ('Pricing', 'Per user', 'Price per user of app');
insert into procedures (type, label, desc) values ('Pricing', 'Per transaction', 'Price per transaction that occurs on app');
insert into procedures (type, label, desc) values ('Pricing', 'Bulk', 'Bulk discount for large numbers of users');

insert into procedure_attribute (procedure_id, attribute_id, value_effect, time_effect) values (1, 2, 2, 1);
insert into procedure_attribute (procedure_id, attribute_id, value_effect, time_effect) values (2, 2, 1, -1);
insert into procedure_attribute (procedure_id, attribute_id, value_effect, time_effect) values (3, 2, -1, -1);

insert into users (user_id, password, active_flag, treatment) values (28,'sha1$HS0RorTS$0a383bb2908adc044a1a16b1e8acec960e031ea0', 1, 'C');
insert into user_feature (user_id, feature_id) values (28,1);
insert into user_feature (user_id, feature_id) values (28,2);
insert into user_feature (user_id, feature_id) values (28,9);
insert into user_feature (user_id, feature_id) values (28,10);


