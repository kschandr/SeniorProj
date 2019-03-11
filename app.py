import logging,sys,argparse, random
#import myfitnesspal
from flask import Flask, render_template,json,request, redirect, url_for, flash
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from subprocess import call
from helper import *
from datetime import date
import calendar

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kaysha'
app.config['MYSQL_DATABASE_PASSWORD'] = 'seniorproject'
app.config['MYSQL_DATABASE_DB'] = 'kaysha'
app.config['MYSQL_DATABASE_HOST'] = 'ambari-head.csc.calpoly.edu'
mysql.init_app(app)



#@app.route("/home/<user>")
#def homePage(user):
#    return render_template('home.html', user=user)

# login wrapper
# CREDIT: https://stackoverflow.com/questions/32640090/python-flask-keeping-track-of-user-sessions-how-to-get-session-cookie-id

def login_required(function_to_protect):
    @wraps(function_to_protect)
    def wrapper(*args, **kwargs):
        user_id = request.cookies.get('current_user')
        if user_id:
            user = database.get(user_id)
            if user:
                # Success!
                return function_to_protect(*args, **kwargs)
            else:
                flash("Session exists, but user does not exist (anymore)")
                return redirect(url_for('login'))
        else:
            flash("Please log in")
            return redirect(url_for('login'))
    return wrapper

# helper
def run_SP(*args, s_proc=None):
	if s_proc == None:
		raise ValueError("No store proc provided for run_SP method")
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc(s_proc,(args))
	data = cursor.fetchall()
	conn.commit()
	conn.close()
	return data

@app.route('/update_profile',methods=['POST'])
def updateProfile():
		# read the posted values from the UI
		_weight = request.form['weight']
		_height = request.form['height']
		_age = request.form['age']
		_sex = request.form['sex']
		_activity = request.form['activity']
		_user = request.cookies.get("current_user")
		app.logger.info("input activity: %s", _activity)

		app.logger.info("input weight: %s, height: %s, age: %s, sex: %s", _weight, _height,_age, _sex)
		#app.logger.info("input height %s", _height)
		#app.logger.info("input name len %d", len(_name))

		if _weight:
				#sql stuff
				run_SP(_weight, _user, s_proc='sp_editWeight')

		if _height:
			#sql stuff
				height_arr= _height.split("'")
				##currently the height table stores ints. So round to neared int
				h_inch = convertFeetToInches(height_arr)
				app.logger.info("height in inches %d", h_inch)
				run_SP(h_inch, _user, s_proc='sp_editHeight')

		if _age and _sex and _activity:
			run_SP(_age, _sex, _activity, _user, s_proc='sp_editAgeSexActivity')

		return redirect('home')



@app.route("/nutrition")
def showNutrition():
	return render_template('nutrition.html')

@app.route("/edit_profile")
def showEditProfile():
	user = request.cookies.get("current_user")
	activities = ["Sedentary (little to no exercise)", "Lightly Active (light exercise/sports 1-3 days/week)",
	            "Moderately Active (moderate exercise/sports 3-5 days/week)",
	            "Very Active (hard exercise/sports 6-7 days a week)",
	            "Extremely Active (very heavy exercise/ physical job/ training twice a day)"]
	heights = [str(feet) + "'" + str(inch) for feet in range(4,7) for inch in range(0,12)][8:]
	return render_template('edit_profile.html', user=user, heights = heights, activities=activities)

@app.route("/workout")
def showWorkout():
	user = request.cookies.get("current_user")
	# 104 is the length of the motivation table
	_id = random.randint(1,104)
	data = run_SP(_id, s_proc='sp_getQuote')
	quote = data[0][0]

	my_date = date.today()
	day = calendar.day_name[my_date.weekday()]
	app.logger.info("today's day: %s", day)
	app.logger.info("user: %s", user)

	# plan_id = (run_SP(user, day, s_proc= 'sp_getPlanID'))[0][0]
	# app.logger.info(plan_id)

	# app.logger.info("plan id %s", plan_id)	

	data = run_SP(user, day, s_proc= 'sp_getWorkout')

	app.logger.info(data)
	app.logger.info("workout data: %s", data)

	# workout = "None"
	# muscle_group = "None"
	# for x in data:
	# 	if x[0] == plan_id:
	# 		app.logger.info("plan id %s", plan_id)	
	# 		app.logger.info("selected %s", x[0])	
	# 		workout = x[2]
	# 		muscle_group = x[1]
	# 		break

	workout = data[0][0]
	muscle_group = data[0][1]

	app.logger.info("muscle %s", muscle_group)
	app.logger.info("workout data: %s", workout)		

	try:
		data = run_SP(user, my_date, s_proc='sp_getCompletion')
		app.logger.info(data)
		done = data[0][0]
		if done == "done":
			workout_done = True
		else:
			workout_done = False
		#super janky try/except block... should change
	except IndexError:
		workout_done = False

	return render_template('workout.html', quote=quote, workout=workout, muscle_group=muscle_group, workout_done=workout_done)


@app.route('/workoutDone')
def workoutDone():

	_user = request.cookies.get("current_user")
	my_date = date.today()
	run_SP(_user, my_date,s_proc='sp_workoutDone')

	return render_template('workout.html', workoutDone=True)

@app.route("/news")
def showNews():
	return render_template('news.html')

@app.route("/goals")
def showGoals():
	user = request.cookies.get("current_user")
	# 104 is the length of the motivation table
	_id = random.randint(1,104)
	data = run_SP(_id, s_proc='sp_getQuote')
	quote = data[0][0]
	data = run_SP(user,s_proc='sp_getGoals')
	app.logger.info(data)
	try:
		lift_bool = True if data[0][0]==1 else False
		run_bool = True if data[0][1]==1 else False
		weight_goal = data[0][2]
	except IndexError:
		lift_bool = True
		run_bool = True
		weight_goal = 0
	return render_template('goals.html', quote=quote, lift_bool=lift_bool, run_bool=run_bool, weight_goal=weight_goal)

@app.route("/update_goals",methods=['POST'])
def updateGoals():
	_weight_goal = request.form['weight']
	_pr = request.form.getlist("pr")
	app.logger.info(request.form.getlist("pr"))
	_user = request.cookies.get("current_user")
	_pr = list(map(int,_pr))
	# 1 = weightlifting, 2 = 5k
	run_SP(_user,_pr,_weight_goal, s_proc="sp_editGoals")
	return render_template('goals.html')

@app.route("/edit_goals")
def editGoals():
	weights = ["Lose", "Maintain", "Gain"]
	return render_template("edit_goals.html", weights = weights)

@app.route("/profile")
def showProfile():
	_weight= _height= _age= _sex= bmr=bmi=tdee=disp_height=0
	_user = request.cookies.get("current_user")
	data = run_SP(_user, s_proc='sp_getProfile')
	app.logger.info("data: %s", data)
	#app.logger.info("data %s", data[0][0])
	#_weight = data.weight
	#_height = data.height
	if data[0][0]:
		_weight, _height,_age,_sex,_activity = data[0]
		disp_height = convertInchesToFeet(_height)
		app.logger.info("_activity from profile: %s", _activity)
		bmr = calcBMR(_height,_weight,_age,_sex)
		tdee = calcTDEE(bmr, _activity)
		bmi = calcBMI(_height,_weight)
	return render_template('profile.html', user=_user, height = disp_height, weight = _weight, bmr=bmr, tdee=tdee, bmi=bmi)

@app.route("/friends")
def showFriends():
	return render_template('friends.html')


@app.route("/success")
@app.route("/home")
def homePage():

		## This is how you get the username
		user = request.cookies.get("current_user")
		app.logger.info("This is the home page. Current user: %s", user)
		## stores totals in calories, macros (dict form)
		#day_calories = client.get_date(2019,2,2).totals
		#app.logger.info("user day calories: %d", day_calories)
		#return render_template('home.html', day_calories=day_calories, user=user)
		return render_template('home.html', user=user)

@app.route("/showSignIn")
def showSignIn():
	#refresh user
	#clean cookies
	response = redirect('home')
	#response.set_cookie("current_user", '', max_age=0)
	response.delete_cookie("current_user")
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():
		#clean cookies
		response = redirect('home')
		#response.set_cookie("current_user", '', max_age=0)
		response.delete_cookie("current_user")
		# read the posted values from the UI
		_name = request.form['inputName']
		app.logger.info("!!!!$$This is the input name %s", _name)
		response.set_cookie("current_user", _name, max_age=0)
		#app.logger.info("input name len %d", len(_name))
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _password:
				#_hashed_password = generate_password_hash(_password)
				data = run_SP(_name, s_proc='sp_loginUser')
				if len(data) == 0 :
					flash("This username is not found, try signing up")
					return json.dumps({'error': 'this username is not found'})
				if not check_password_hash(data[0][0], _password):
						flash("Wrong password")
						app.logger.error("not a match for password")
						return json.dumps({'error':str(data[0])})
				else:
						## set the user cookies
						response = redirect('home')
						response.delete_cookie("current_user")
						response.set_cookie("current_user", _name)
						app.logger.info("setting name cookie %s", _name)
						return response
		else:
				app.logger.error("incomplete signin")
				return json.dumps({'html':'<span>Enter the required fields</span>'})


@app.route("/showSignUp")
def showSignUp():
	return render_template('signup.html')

@app.route("/")
@app.route("/main")
def main():
		return render_template('index.html')

@app.route('/signUp',methods=['POST'])
def signUp():
		#clean cookies
		response = redirect('home')
		response.set_cookie("current_user", '', max_age=0)
		# read the posted values from the UI
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _email and _password:
				_hashed_password = generate_password_hash(_password)

				#save the user and password into the usr_tbl via sp_createUser stored proc.
				data =run_SP(_name,_email,_hashed_password, s_proc='sp_createUser')

				if len(data) is 0:
						## set the user cookies
						## we should probably comply to GDPR :P
						response = redirect('home')
						response.set_cookie("current_user", _name)
						app.logger.info("setting name cookie %s", request.cookies.get("current_user"))
						return response
				else:
						app.logger.info("Unable to create user on mysql")
						return json.dumps({'error':str(data[0])})
		else:
				return json.dumps({'html':'<span>Enter the required fields</span>'})


if __name__ == "__main__":
		# parser = argparse.ArgumentParser(description='our fitness app.')
		# parser.add_argument('MFP_username',
		# 	help='your username for myfitnesspal')
		# args = parser.parse_args()
		# ## this next block would ideally be put into signup when we create users MFP accounts
		# ## save the username and hashed password into the myfitnesspal API
		# call(["myfitnesspal", "store-password", args.MFP_username])
		# client = myfitnesspal.Client(args.MFP_username)


		app.run(debug=True)
