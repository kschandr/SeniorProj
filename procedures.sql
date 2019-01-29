use kaysha;

drop table if exists tbl_user;

CREATE TABLE tbl_user (
  user_id BIGINT AUTO_INCREMENT,
  user_name VARCHAR(45) NULL,
  user_username VARCHAR(45) NULL,
  user_password VARCHAR(95) NULL,
  PRIMARY KEY (user_id));
  
DROP PROCEDURE IF EXISTS sp_createUser;

DELIMITER $$
CREATE  PROCEDURE `sp_createUser`(
    IN p_name VARCHAR(45),
    IN p_username VARCHAR(45),
    IN p_password VARCHAR(93)
)
BEGIN
    if ( select exists (select 1 from tbl_user where user_username = p_username) ) THEN
     
        select 'Username Exists !!';
     
    ELSE
     
        insert into tbl_user
        (
            user_name,
            user_username,
            user_password
        )
        values
        (
            p_name,
            p_username,
            p_password
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
   select user_password from tbl_user where user_username = p_username;
END$$
DELIMITER ;