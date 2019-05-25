use kaysha;

/*
Table stuff
*/

drop table if exists alt_workouts;
create table alt_workouts (
user varchar(45) not null,
type1 varchar(15) not null,
time1 varchar(10) not null,
type2 varchar(15) not null,
time2 varchar(10) not null,
date DATE not null,
primary key (user, date, type1, type2));

drop procedure if exists sp_getAltWorkouts1;
delimiter $$
create procedure sp_getAltWorkouts1 (
in p_username varchar(45),
in p_date DATE
)
begin
select type1,time1 from alt_workouts where user=p_username and date=p_date;
END $$
delimiter ;

drop procedure if exists sp_getAltWorkouts2;
delimiter $$
create procedure sp_getAltWorkouts2 (
in p_username varchar(45),
in p_date DATE
)
begin
select type2,time2 from alt_workouts where user=p_username and date=p_date;
END $$
delimiter ;

ALTER TABLE tbl_goals ADD COLUMN goal_1 VARCHAR(30);
ALTER TABLE tbl_goals ADD COLUMN goal_2 VARCHAR(30);
ALTER TABLE tbl_goals ADD COLUMN goal_3 VARCHAR(30);
ALTER TABLE tbl_goals ADD COLUMN goal_4 VARCHAR(30);
ALTER TABLE tbl_goals ADD COLUMN goal_5 VARCHAR(30);

update tbl_goals set goal_1='',goal_2='',goal_3='',goal_4='',goal_5='';

drop procedure if exists sp_getIndGoals;
delimiter $$
CREATE PROCEDURE sp_getIndGoals (
  in p_username varchar(45)
)
BEGIN
select goal_1, goal_2, goal_3, goal_4, goal_5
from tbl_goals where username=p_username;
END $$
delimiter ;

drop procedure if exists sp_setAltWorkouts;
delimiter $$
create procedure sp_setAltWorkouts (
in p_username varchar(45),
in p_date DATE,
in p_type1 varchar(15),
in p_time1 varchar(10),
in p_type2 varchar(15),
in p_time2 varchar(10)
)
begin
insert into alt_workouts (user, date, type1, time1, type2, time2) 
values (p_username, p_date, p_type1, p_time1, p_type2, p_time2);
END $$
delimiter ;







drop table if exists tbl_user;

/***tbl_user
login and credentials for user
*/
CREATE TABLE `tbl_user` (
  `user_id` bigint(20) NOT NULL AUTO_INCREMENT,
  `user_username` varchar(45) NOT NULL,
  `user_email` varchar(45) DEFAULT NULL,
  `user_password` varchar(95) DEFAULT NULL,
  PRIMARY KEY (`user_id`),
  UNIQUE KEY `user_username` (`user_username`)
);

drop table if exists tbl_profile;

/*** tbl_profile
the user's bio info ie weight, height, etc.
*/
CREATE TABLE tbl_profile (
  username varchar(45) NOT NULL,
  weight int(11) DEFAULT NULL,
  height int(11) DEFAULT NULL,
  sex varchar(10) NULL,
  age int(11) NULL,
  activity varchar(95) null,
  PRIMARY KEY (username)
);

drop table if exists tbl_goals;
CREATE TABLE `tbl_goals` (
  `username` varchar(45) NOT NULL,
  `lift` tinyint(1) DEFAULT '0',
  `run_5k` tinyint(1) DEFAULT '0',
  `weight_goal` varchar(45) DEFAULT 'Maintain',
  `goal_lbs` int(11) DEFAULT '100',
  `goal_cals` int(11) DEFAULT '1200',
  KEY `tbl_goals` (`username`),
  CONSTRAINT `tbl_goals_ibfk_1` FOREIGN KEY (`username`) REFERENCES `tbl_user` (`user_username`)
);

drop table if exists motivation;
CREATE TABLE `motivation` (
  `id` bigint(20) NOT NULL AUTO_INCREMENT,
  `quote` varchar(100) DEFAULT NULL,
  PRIMARY KEY (`id`)
);

drop table if exists plans;
CREATE TABLE `plans` (
  `goal` varchar(20) NOT NULL,
  `day` varchar(10) NOT NULL,
  `id` bigint(20) DEFAULT NULL,
  PRIMARY KEY (`goal`,`day`)
);

drop table if exists workout_complete;
CREATE TABLE `workout_complete` (
  `username` varchar(45) NOT NULL,
  `day` varchar(60) NOT NULL,
  PRIMARY KEY (`username`,`day`)
);

drop table if exists exercises;
CREATE TABLE `exercises` (
  `id` bigint(20) NOT NULL,
  `muscle_group` varchar(20) DEFAULT NULL,
  `workout` varchar(1000) DEFAULT NULL,
  PRIMARY KEY (`id`)
);


drop table if exists news;

CREATE TABLE `news` (
  `id` bigint(20) NOT NULL auto_increment,
  `art_name` TINYTEXT CHARACTER SET utf8 DEFAULT NULL,
  `author` TINYTEXT CHARACTER SET utf8 DEFAULT NULL,
  `content` TEXT CHARACTER SET utf8 DEFAULT NULL,
  PRIMARY KEY (`id`)
);

drop table if exists food;
CREATE TABLE `food` (
  `username` varchar(45) NOT NULL,
  `food_id` varchar(45) NOT NULL,
  `input_date` date NOT NULL,
  `serving_size` int(11) DEFAULT '1',
  `meal` varchar(45) NOT NULL DEFAULT 'Breakfast',
  PRIMARY KEY (`username`,`food_id`,`input_date`)
);

drop table if exists macros;
CREATE TABLE `macros` (
  `username` varchar(45) NOT NULL,
  `today` date NOT NULL,
  `calories` bigint(20) NOT NULL,
  `protein` bigint(20) NOT NULL,
  `fat` bigint(20) NOT NULL,
  `carb` bigint(20) NOT NULL,
  PRIMARY KEY (username,today)
);

drop table if exists weight_progress;
CREATE TABLE `weight_progress` (
  `user` varchar(45) NOT NULL,
  `pounds` int(11) DEFAULT NULL,
  `day` date NOT NULL,
  PRIMARY KEY (`user`,`day`)
);

/*
Stored procedures
*/



/*** sp_createUser
Updates a user login and password into the tbl_user.

Parameters:
----
p_username: str, the username
p_email: str, email address
p_password: str, hashed password

*/
DROP PROCEDURE IF EXISTS sp_createUser;
DELIMITER $$
CREATE PROCEDURE `sp_createUser`(
    IN p_username VARCHAR(45),
    IN p_email VARCHAR(45),
    IN p_password VARCHAR(93)
)
BEGIN
    if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN

        select 'Username Exists !!';

    ELSE

        insert into tbl_user
        (
            user_username,
            user_email,
            user_password
        )
        values
        (
            p_username,
            p_email,
            p_password
        );

        insert into tbl_profile
        (
          username
        )
        values
        (
          p_username
        );

        insert into tbl_goals
        (
          username, weight_goal
        )
        values
        (
          p_username, 'Maintain'
        );

    END IF;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_loginUser;

/*** sp_loginUser
checks if the user logging in has credentials in the table

Parameters:
---
p_username: str, the username
*/
DELIMITER $$
CREATE  PROCEDURE `sp_loginUser`(
    IN p_username VARCHAR(45)
)
BEGIN
  if (select exists(select 1 from tbl_profile where username=username)) then
    select user_password from tbl_user where user_username = p_username;
  end if;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_editHeight;

/***sp_editHeight
edit the height value for a user

Parameters:
---
height: int, the height in inches
username: str, username whose height will be updated
*/
DELIMITER $$
CREATE PROCEDURE `sp_editHeight`(
    IN _height INT,
    IN _username VARCHAR(45)
)
BEGIN
  UPDATE tbl_profile SET height = _height WHERE username = _username;

END$$
DELIMITER ;




drop procedure if exists sp_editAgeSex;
drop procedure if exists sp_editAgeSexActivity;

/***sp_editAgeSexActivity
edit the age, sex, activity value for a user

Parameters:
---
age: int
sex: str, female or male
activity: str, intensity of regular day activities
username: str, username
*/
DELIMITER $$
CREATE PROCEDURE `sp_editAgeSexActivity`(
    IN _age INT,
    IN _sex VARCHAR(45),
    IN _activity varchar(95),
    IN _username VARCHAR(45)
)
BEGIN
  UPDATE tbl_profile SET age = _age, sex= _sex, activity= _activity WHERE username = _username;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getProfile;

/***sp_getProfile.
Returns the profile of user

Parameters:
---
username: str, username
*/
DELIMITER $$
CREATE PROCEDURE `sp_getProfile`(
    IN _username VARCHAR(45)
)
BEGIN
  select weight, height, age, sex, activity from tbl_profile where username = _username;
END$$
DELIMITER ;




/***sp_getWorkout.
get a workout plan for the day

Parameters:
---
username: str, username
day: str
*/
DROP PROCEDURE IF EXISTS sp_getWorkout;
DELIMITER $$
CREATE PROCEDURE `sp_getWorkout`(
    IN _username VARCHAR(45),
    IN _day VARCHAR(20)
)
BEGIN
  select workout, muscle_group, cals from exercises 
  where id 
  IN (select id from plans 
	  where day = _day and goal IN ((
			select weight_goal from tbl_goals 
				where username=_username), "Maintain"));
END$$
DELIMITER ;


/***sp_getCompletion.
returns a complete boolean if the user has a workout plan

Parameters:
---
username: str, username
day: str
*/
DROP PROCEDURE IF EXISTS sp_getCompletion;

DELIMITER $$
CREATE PROCEDURE `sp_getCompletion`(
    IN _username VARCHAR(45),
    IN _day VARCHAR(60)
)
BEGIN
  if ( select exists (select 1 from workout_complete where username=_username and day=_day))
  THEN select 'done';
  ELSE select 'not';
  end if;
END$$
DELIMITER ;



/***sp_workoutDone.
updates the workout plan for the user to show that workout is completed

Parameters:
---
username: str, username
day: str
*/
DROP PROCEDURE IF EXISTS sp_workoutDone;
DELIMITER $$
CREATE PROCEDURE `sp_workoutDone`(
    IN _username VARCHAR(45),
    IN _day VARCHAR(60)
)
BEGIN
  insert into workout_complete (username, day) values (_username, _day);
END$$
DELIMITER ;



/***sp_editGoals.
updates goals for the user

Parameters:
---
p_username: str, username
bool_list: str, has the list of goals the user wants to acheive (training goal)
weight: str, weight goal (maintain, lose or gain)
*/
drop procedure if exists sp_editGoals; 
delimiter $$
CREATE PROCEDURE sp_editGoals (
  in p_username varchar(45),
  in bool_list varchar(10),
    in weight_diff varchar(45),
    in weight_goal int,
    in cals int,
    in ind_1 varchar(30),
    in ind_2 varchar(30),
    in ind_3 varchar(30),
    in ind_4 varchar(30),
    in ind_5 varchar(30)
)
BEGIN
declare run boolean default 0;
declare weights boolean default 0;
set run = if(find_in_set('2',bool_list) <> 0, 1,0);
set weights = if(find_in_set('1',bool_list) <> 0, 1,0);

UPDATE tbl_goals set 
lift=weights,run_5k=run,weight_goal=weight_diff,goal_lbs=weight_goal, goal_cals=cals, 
goal_1=ind_1, goal_2=ind_2, goal_3=ind_3, goal_4=ind_4, goal_5=ind_5
where username=p_username;
END $$
delimiter ;

/***sp_getGoals.
get goals for the user

Parameters:
---
p_username: str, username
*/
drop procedure if exists sp_getGoals;
delimiter $$
CREATE PROCEDURE `sp_getGoals`(
  in p_username varchar(45)
)
BEGIN
  select lift, run_5k, weight_goal, goal_lbs, goal_cals from tbl_goals WHERE username = p_username;
END $$
delimiter ;


DROP PROCEDURE IF EXISTS sp_getQuote;

/***sp_getQuote.
get motivational quote

Parameters:
---
id: int, the random integer that takes a motivational quote
*/
DELIMITER $$
CREATE PROCEDURE `sp_getQuote`(
    IN _id INT
)
BEGIN
  select quote from motivation where id = _id;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getArticle;
DELIMITER $$
CREATE PROCEDURE `sp_getArticle`(
    IN num BIGINT
)
BEGIN
  select art_name, author, content from news where id = num;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_newArticle;
DELIMITER $$
CREATE PROCEDURE `sp_newArticle`(
    in a_name tinytext,
	in a_author tinytext,
	in a_content text
)
BEGIN
  insert into news(art_name, author, content)  values (a_name, a_author, a_content);
END$$
DELIMITER ;

drop procedure if exists sp_addFood;
delimiter $$
CREATE  PROCEDURE `sp_addFood`(
in _username varchar(45),
in mfp_id bigint(20),
in today date /*yyyy-mm-dd*/,
in serving int,
in _meal varchar(45)
)
begin
	insert into food
		(username,food_id, input_date, serving_size, meal)
    values
		(_username, mfp_id, today,serving, _meal)
	on duplicate key update
		serving_size = serving_size + serving, meal=_meal;
end $$
delimiter ;

drop procedure if exists sp_editFood;
delimiter $$
CREATE  PROCEDURE `sp_editFood`(
in _username varchar(45),
in mfp_id bigint(20),
in today date /*yyyy-mm-dd*/,
in serving int
)
begin
	if (serving <= 0)
    then
		delete from food 
        where username=_username and input_date=today and food_id=mfp_id;
    else
		update food 
        set serving_size =serving 
        where username=_username and input_date=today and food_id=mfp_id;
	end if;
end $$
delimiter ;


DROP procedure if exists sp_updateMacros;
delimiter $$
CREATE PROCEDURE `sp_updateMacros`(
in _username varchar(45),
in _today date,
in _cals bigint(20),
in _protein bigint(20),
in _fat bigint(20),
in _carb bigint(20)
)
begin

insert into macros
	(username, today,calories,protein,fat,carb)
values
    (_username,_today, _cals, _protein,_fat,_carb)
on duplicate key update
	calories = _cals, protein=_protein, fat = _fat, carb =_carb;
end $$
delimiter ;

drop procedure if exists sp_getMacros;
delimiter $$
create procedure `sp_getMacros`(
in _user varchar(45),
in _today date
)
begin
	select calories,protein,fat,carb from macros where username=_user and today = _today;
end $$
delimiter ;


drop procedure if exists sp_getTodayFood;
delimiter $$
CREATE PROCEDURE `sp_getTodayFood`(
in _username varchar(45),
in _today date)
begin
	select food_id, serving_size,meal from food where username=_username and input_date=_today order by meal;
end $$
delimiter ;

drop procedure if exists sp_getWeightProgress;
delimiter $$
CREATE PROCEDURE `sp_getWeightProgress`(
    IN username VARCHAR(45)
)
BEGIN
  select * from weight_progress where user=username;
END $$
delimiter ;

drop procedure if exists sp_getWeight;
delimiter $$
create procedure `sp_getWeight`(
  in p_username varchar(45)
)
BEGIN
select pounds from weight_progress where user=p_username order by `day` DESC LIMIT 1;
END $$
delimiter ;

drop procedure if exists sp_editWeight;

/***sp_editWeight
edit the weight value for a user
update the weight progress table with the inputted weight in pounds

Parameters:
---
weight: int, the weight in pounds
username: str, username whose weight will be updated
today: todays' date
*/
delimiter $$
CREATE PROCEDURE `sp_editWeight`(
    IN _weight INT,
    IN _username VARCHAR(45),
    in _today date
)
BEGIN
  UPDATE tbl_profile SET weight = _weight WHERE username = _username;
  insert into weight_progress
  (user, pounds, day)
  values
    (_username,_weight,_today)
  on duplicate key update
  pounds = _weight;
END $$
delimiter ;

