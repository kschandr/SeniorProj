use kaysha;

/*
Table stuff
*/

drop table if exists tbl_user;

/***tbl_user
login and credentials for user
*/
CREATE TABLE tbl_user (
  user_id BIGINT AUTO_INCREMENT,
  user_username VARCHAR(45) NULL,
  user_email VARCHAR(45) NULL,
  user_password VARCHAR(95) NULL,
  PRIMARY KEY (user_id));

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
  `weight_goal` varchar(45) DEFAULT 'Maintain'
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
create table food(
	id bigint(10) auto_increment,
	username varchar(45) not null,
    food_id int(20) not null,
    input_date DATE not null,
    primary key (id)
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



/*
Stored procedures 
*/

DROP PROCEDURE IF EXISTS sp_createUser;

/*** sp_createUser
Updates a user login and password into the tbl_user.

Parameters:
----
p_username: str, the username
p_email: str, email address
p_password: str, hashed password

*/
DELIMITER $$
CREATE  PROCEDURE `sp_createUser`(
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
    IN height INT,
    IN username VARCHAR(45)
)
BEGIN
  UPDATE tbl_profile SET height = height WHERE username = username;

END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_editWeight;

/***sp_editWeight
edit the weight value for a user

Parameters:
---
weight: int, the weight in pounds
username: str, username whose weight will be updated
*/
DELIMITER $$
CREATE PROCEDURE `sp_editWeight`(
    IN weight INT,
    IN username VARCHAR(45)
)
BEGIN
  UPDATE tbl_profile SET weight = weight WHERE username = username;
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
    IN age INT,
    IN sex VARCHAR(45),
    IN activity varchar(95),
    IN username VARCHAR(45)
)
BEGIN
  UPDATE tbl_profile SET age = age, sex=sex, activity=activity WHERE username = username;
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
    IN username VARCHAR(45)
)
BEGIN
  select weight, height, age, sex, activity from tbl_profile where username = username;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getWorkout;

/***sp_getWorkout. 
get a workout plan for the day

Parameters:
---
username: str, username 
day: str
*/
DELIMITER $$
CREATE PROCEDURE `sp_getWorkout`(
    IN username VARCHAR(45),
    IN day VARCHAR(20)
)
BEGIN
  select workout, muscle_group from exercises where id IN (select id from plans where day = day and goal IN (select weight_goal from tbl_goals where username=username));
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getCompletion;

/***sp_getCompletion. 
returns a complete boolean if the user has a workout plan

Parameters:
---
username: str, username 
day: str
*/
DELIMITER $$
CREATE PROCEDURE `sp_getCompletion`(
    IN username VARCHAR(45),
    IN day VARCHAR(60)
)
BEGIN
  if ( select exists (select 1 from workout_complete where username=username and day=day)) 
  THEN select 'done'
  ELSE select 'not'
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_workoutDone;

/***sp_workoutDone. 
updates the workout plan for the user to show that workout is completed

Parameters:
---
username: str, username 
day: str
*/
DELIMITER $$
CREATE PROCEDURE `sp_workoutDone`(
    IN username VARCHAR(45),
    IN day VARCHAR(60)
)
BEGIN
  insert into workout_complete (username, day) values (username, day);
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_editGoals;

/***sp_editGoals. 
updates goals for the user

Parameters:
---
p_username: str, username 
bool_list: str, has the list of goals the user wants to acheive (training goal)
weight: str, weight goal (maintain, lose or gain)
*/
DELIMITER $$
CREATE PROCEDURE `sp_editGoals`(
	in p_username varchar(45),
	in bool_list varchar(10),
    in weight varchar(45)
)
BEGIN
declare run boolean default 0;
declare weights boolean default 0;
set run = if(find_in_set('2',bool_list) <> 0, 1,0);
set weights = if(find_in_set('1',bool_list) <> 0, 1,0);

UPDATE tbl_goals SET lift = weights, run_5k=run, weight_goal = weight WHERE username = p_username;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getGoals;

/***sp_getGoals. 
get goals for the user

Parameters:
---
p_username: str, username 
*/
DELIMITER $$
CREATE PROCEDURE `sp_getGoals`(
	in p_username varchar(45)
)
BEGIN
	select lift, run_5k, weight_goal from tbl_goals WHERE username = p_username;
END$$
DELIMITER ;


DROP PROCEDURE IF EXISTS sp_getQuote;

/***sp_getQuote. 
get motivational quote

Parameters:
---
id: int, the random integer that takes a motivational quote 
*/
DELIMITER $$
CREATE PROCEDURE `sp_getQuote`(
    IN id INT
)
BEGIN
  select quote from motivation where id = id;
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
in username varchar(45),
in mfp_id bigint(20),
in today date /*yyyy-mm-dd*/
)
begin
	insert into food(username,food_id, input_date) values (username, mfp_id, today);
end $$
delimiter ;


DROP procedure if exists sp_updateMacros;
delimiter $$
CREATE PROCEDURE `sp_updateMacros`(
in username varchar(45),
in today date,
in cals bigint(20),
in protein bigint(20),
in fat bigint(20),
in carb bigint(20)
)
begin 
  if ( select exists (select 1 from macros where username=username and today=today)) 
  
  THEN 	update macros 
		SET calories = cals, protein=protein, fat = fat, carb =carb 
		WHERE username = username and today=today;
        
  ELSE 	insert into macros(username, today,calories,protein,fat,carb) 
		values(username,today, cals,protein,fat,carb);
end if;
end $$
delimiter ;

drop procedure if exists sp_getMacros;
delimiter $$
create procedure `sp_getMacros`(
in username varchar(45),
in today date
)
begin 
	select calories,protein,fat,carb from macros where username=username and today = today;
end $$
delimiter ;
