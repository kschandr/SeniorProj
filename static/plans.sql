use kaysha;

drop table if exists plans;

CREATE TABLE plans (
  goal VARCHAR(20),
  day VARCHAR(10),
  id BIGINT,
  PRIMARY KEY (goal,day));


insert into plans (goal,day,id) values ("lose weight", "Monday", 1);	
insert into plans (goal,day,id) values ("lose weight", "Tuesday", 2);
insert into plans (goal,day,id) values ("lose weight", "Wednesday", 3);
insert into plans (goal,day,id) values ("lose weight", "Thursday", 4);
insert into plans (goal,day,id) values ("lose weight", "Friday", 5);
insert into plans (goal,day,id) values ("lose weight", "Saturday", 6);
insert into plans (goal,day,id) values ("lose weight", "Sunday", 7);
insert into plans (goal,day,id) values ("gain weight", "Monday", 8);
insert into plans (goal,day,id) values ("gain weight", "Tuesday", 9);
insert into plans (goal,day,id) values ("gain weight", "Wednesday", 10);
insert into plans (goal,day,id) values ("gain weight", "Thursday", 11);
insert into plans (goal,day,id) values ("gain weight", "Friday", 12);
insert into plans (goal,day,id) values ("gain weight", "Saturday", 13);
insert into plans (goal,day,id) values ("gain weight", "Sunday", 14);
insert into plans (goal,day,id) values ("maintain", "Monday", 15);
insert into plans (goal,day,id) values ("maintain", "Tuesday", 16);
insert into plans (goal,day,id) values ("maintain", "Wednesday", 17);
insert into plans (goal,day,id) values ("maintain", "Thursday", 18);
insert into plans (goal,day,id) values ("maintain", "Friday", 19);
insert into plans (goal,day,id) values ("maintain", "Saturday", 20);
insert into plans (goal,day,id) values ("maintain", "Sunday", 21);
