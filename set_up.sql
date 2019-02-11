use kaysha;

/*
Table stuff
*/

drop table if exists tbl_user;

CREATE TABLE tbl_user (
  user_id BIGINT AUTO_INCREMENT,
  user_username VARCHAR(45) NULL,
  user_email VARCHAR(45) NULL,
  user_password VARCHAR(95) NULL,
  PRIMARY KEY (user_id));
  
drop table if exists tbl_profile;

CREATE TABLE tbl_profile (
  username varchar(45) NOT NULL,
  weight int(11) DEFAULT NULL,
  height int(11) DEFAULT NULL,
  sex varchar(10) NULL,
  age int(11) NULL,
  PRIMARY KEY (username)
);

  
drop table if exists users;


/* 
Stored procedures stuff
*/

DROP PROCEDURE IF EXISTS sp_createUser;

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
DELIMITER $$
CREATE PROCEDURE `sp_editWeight`(
    IN weight INT,
    IN username VARCHAR(45)
)
BEGIN
	UPDATE tbl_profile SET weight = weight WHERE username = username;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_editAgeSex;

DELIMITER $$
CREATE PROCEDURE `sp_editAgeSex`(
    IN age INT,
    IN sex VARCHAR(45),
    IN username VARCHAR(45)
)
BEGIN
	UPDATE tbl_profile SET age = age and sex=sex WHERE username = username;
END$$
DELIMITER ;

DROP PROCEDURE IF EXISTS sp_getProfile;


DELIMITER $$
CREATE PROCEDURE `sp_getProfile`(
    IN username VARCHAR(45)
)
BEGIN
	select weight, height, age, sex from tbl_profile where username = username;
END$$
DELIMITER ;



