use kaysha;

drop table if exists exercises;

CREATE TABLE exercises (
  id BIGINT,
  muscle_group VARCHAR(20) NULL,
  workout VARCHAR(1000) NULL,
  PRIMARY KEY (id));


SELECT @cardio := "1 mile light jog
		  3 min at 80% effort
		  3 min at walking pace
		  2 min at 80% effort
		  2 min at walking pace
		  3 min at 80% effort
		  1 mile light jog
		  ";


SELECT @chest_back := "TRISET
		 	  12 reps incline winding DB bench
			  12 reps pushups
			  15 reps flat DB chest flys

			  TRISET
			  12 reps close-grip seated rows
			  12 reps wide-grip pull downs
			  12 reps DB pullovers

			  SUPERSET
			  5x6 DB bench
			  5x6 bent over rows

			  SUPERSET
			  5x10 pullups
			  5x10 bench dips  
			  ";

SELECT @legs := "TRISET
		12 reps single leg press
		12 reps single leg hamstring curls
		12 reps single leg extensions

		SUPERSET
		5x6 goblet squat
		5x6 deadlift
		";

SELECT @HIIT := "SUPERSET
		4x12 kettle bell swing
		4x15 air squats

		HIIT 5 Rounds
		45s on, 45s off running

		TRISET
		4x25 weighted crunches
		4x20 back extensions
		4x40 ab twists
		4x10 hanging knee raises
		";

SELECT @shoulders := "TRISET
			 12 reps plate raises
			 12 reps DB lat raises
			 12 reps DB rear delt flys

			 TRISET
			 5x6 DB Arnold press
			 5x6 behind the neck barbell press

			 SUPERSET
			 5x6 barbell upright row
			 5x6 DB strict press
			 ";

SELECT @arms := "GIANT SET
		12 reps alt. DB curls
		12 reps 1 arm overhead tricep extension
		21 method: 2 arm cable curls
		12 reps DB tricep kickbacks

		SUPERSET
		4x6 close grip bench press
		4x6 EZ bar curls
		";	



insert into exercises (id, muscle_group, workout) values (1, "cardio",@cardio);
insert into exercises (id, muscle_group, workout) values (2, "HIIT", @HIIT);
insert into exercises (id, muscle_group, workout) values (3, "rest", "rest day");
insert into exercises (id, muscle_group, workout) values (4, "legs", @legs);
insert into exercises (id, muscle_group, workout) values (5, "cardio", @cardio);
insert into  exercises (id, muscle_group, workout) values (6, "HIIT", @HIIT);
insert into exercises (id, muscle_group, workout) values (7, "arms", @arms);

insert into exercises (id, muscle_group, workout) values (8, "arms", @arms);
insert into exercises (id, muscle_group, workout) values (9, "legs", @legs);
insert into exercises (id, muscle_group, workout) values (10, "HIIT", @HIIT);
insert into exercises (id, muscle_group, workout) values (11, "chest/back", @chest_back);	
insert into exercises (id, muscle_group, workout) values (12, "shoulders", @shoulders);
insert into exercises (id, muscle_group, workout) values (13, "cardio", @cardio);
insert into exercises (id, muscle_group, workout) values (14, "rest", "rest day");

insert into exercises (id, muscle_group, workout) values (15, "cardio", @cardio);
insert into exercises (id, muscle_group, workout) values (16, "HIIT", @HIIT);
insert into exercises (id, muscle_group, workout) values (17, "legs", @legs);		
insert into exercises (id, muscle_group, workout) values (18, "rest", "rest day");
insert into exercises (id, muscle_group, workout) values (19, "arms", @arms);
insert into exercises (id, muscle_group, workout) values (20, "HIIT", @HIIT);
insert into exercises (id, muscle_group, workout) values (21, "chest/back", @chest_back);












