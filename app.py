import logging,sys,argparse, random, re
import myfitnesspal,pexpect
import datetime,calendar
from flask import Flask, render_template,json,request, redirect, url_for, flash, Markup,jsonify
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from helper import *
from datetime import date, datetime, timedelta
from math import ceil
from wtforms import Form, StringField, SelectField


"""
Requirements:
pip install myfitnesspal
pip install Flask-WTF
pip install pexpect
"""

app = Flask(__name__)
# To use session dictionary, make sure to have app secret key
# generated in terminal via: python -c 'import os; print(os.urandom(16))'
app.secret_key = b'\xcdW\x16\x13\xcfU\xf0p\xd5\xdf\xef\xa7\x9b\xac\xb0H'
mysql = MySQL()
app.logger.setLevel(logging.INFO)
# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kaysha'
app.config['MYSQL_DATABASE_PASSWORD'] = 'seniorproject'
app.config['MYSQL_DATABASE_DB'] = 'kaysha'
app.config['MYSQL_DATABASE_HOST'] = 'ambari-head.csc.calpoly.edu'
mysql.init_app(app)


client = ""
today = date.today().strftime('%Y-%m-%d')

PER_PAGE = 10

class Pagination(object):

		def __init__(self, page, per_page, total_count):
				self.page = page
				self.per_page = per_page
				self.total_count = total_count

		@property
		def pages(self):
				return int(ceil(self.total_count / float(self.per_page)))

		@property
		def has_prev(self):
				return self.page > 1

		@property
		def has_next(self):
				return self.page < self.pages

		def iter_pages(self, left_edge=2, left_current=2,
									 right_current=5, right_edge=2):
				last = 0
				for num in xrange(1, self.pages + 1):
						if num <= left_edge or \
							 (num > self.page - left_current - 1 and \
								num < self.page + right_current) or \
							 num > self.pages - right_edge:
								if last + 1 != num:
										yield None
								yield num
								last = num

"""
------------------------------------
Auxiliary Methods
------------------------------------
"""
def run_SP(*args, s_proc=None,):
	""" Runs the stored procedure

	If the s_proc argument is not passed, an error is raised

	Parameters:
	-----
	args: str, optional
		The arguments passed into the mySQL stored procedure
	s_proc: str
		The name of the stored procedure

	Raises:
	-----
	ValueError
		If no s_proc name is passed

	"""

	if s_proc == None:
		raise ValueError("No store proc provided for run_SP method")
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc(s_proc,(args))
	data = cursor.fetchall()
	conn.commit()
	conn.close()
	return data

def login_required(function_to_protect):
		"""Is a wrapper to ensure user is logged into a session

		CREDIT: https://stackoverflow.com/questions/32640090/python-flask-keeping-track-of-user-sessions-how-to-get-session-cookie-id

		Parameters:
		-----
		function_to_protect: func
			The name of the function of which this wrapper precedes

		"""

		def a_wrapper_accepting_arguments(*args, **kwargs):
				user_id = request.cookies.get('current_user')
				if user_id:
						data = run_SP(user_id, s_proc="sp_loginUser")
						if len(data) != 0:
								# Success!
								return function_to_protect(*args, **kwargs)
						else:
								flash("Session exists, but user does not exist (anymore)")
								return redirect(url_for('showSignIn'))
				else:
						return redirect(url_for('showSignIn'))
		a_wrapper_accepting_arguments.__name__ = function_to_protect.__name__
		return a_wrapper_accepting_arguments


"""
-----------------------------------
App Main Functions
-----------------------------------
"""
def getQuotes():
	_id = random.randint(1,104)
	data = run_SP(_id, s_proc='sp_getQuote')
	quote = data[0][0]
	return quote

def getMacros(food_id,serving=1):
	serving = int(serving)
	data = client.get_food_item_details(food_id)
	return (round(data.calories,2)*serving, round(data.protein,2)*serving,
		round(data.fat,2)*serving, round(data.carbohydrates,2)*serving)


'''
-------
PROFILE PAGE
-------
'''
@app.route('/update_profile',methods=['POST'])
@login_required
def updateProfile():
		""" Allows the user to update their profile with weight, height, etc.

		Calls a POST HTTP method onto the edit_profile.js

		"""

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
				run_SP(_weight, _user, today, s_proc='sp_editWeight')

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

@app.route("/edit_profile")
@login_required
def showEditProfile():
	""" show the edit profile page to the user

	Form asks for activity level of user

	"""

	user = request.cookies.get("current_user")
	activities = ["Sedentary (little to no exercise)", "Lightly Active (light exercise/sports 1-3 days/week)",
							"Moderately Active (moderate exercise/sports 3-5 days/week)",
							"Very Active (hard exercise/sports 6-7 days a week)",
							"Extremely Active (very heavy exercise/ physical job/ training twice a day)"]
	heights = [str(feet) + "'" + str(inch) for feet in range(4,7) for inch in range(0,12)][8:]
	return render_template('edit_profile.html', user=user, heights = heights, activities=activities)

@app.route("/profile")
@login_required
def showProfile():
	""" shows user profile

		displays values if the user has already given input

	"""

	_weight= _height= _age= _sex= bmr=bmi=tdee=disp_height=0
	_user = request.cookies.get("current_user")
	data = run_SP(_user, s_proc='sp_getProfile')
	app.logger.info("data: %s", data)
	if data[0][0]:
		_weight, _height,_age,_sex,_activity = data[0]
		disp_height = convertInchesToFeet(_height)
		app.logger.info("_activity from profile: %s", _activity)
		bmr = calcBMR(_height,_weight,_age,_sex)
		tdee = calcTDEE(bmr, _activity)
		bmi = calcBMI(_height,_weight)
	return render_template('profile.html', user=_user, height = disp_height, weight = _weight, bmr=bmr, tdee=tdee, bmi=bmi)



'''
----
NUTRITION PAGE
---
'''
@app.route("/nutrition")
@login_required
def showNutrition():
	""" Shows the calories and macros user has inputted

	Dependent on MFP account

	"""
	user = request.cookies.get("current_user")
	macros = run_SP(user, today, s_proc="sp_getMacros")
	app.logger.info("in show nutrition: %s",macros)
	macros = [0,0,0,0] if not macros else macros[0]
	cals, protein, fat, carb = macros
	food_servings = run_SP(user, today, s_proc = "sp_getTodayFood")
	app.logger.info("todayfood: %s", food_servings)
	food_data= [client.get_food_item_details(i[0]) for i in food_servings]
	servings = [i[1] for i in food_servings]
	meal = [i[2] for i in food_servings]
	for i,m in enumerate(meal):
		if i > 0 and m == meal[i-1]:
			meal[i] = ""
	app.logger.info("meal: %s", meal)

	try:
		data = run_SP(user, today, s_proc='sp_getCompletion')
		app.logger.info(data)
		done = data[0][0]
		if done == "done":
			_workout_done = True
		else:
			_workout_done = False
		#super janky try/except block... should change
	except IndexError:
		_workout_done = False

	my_date = date.today()
	day = calendar.day_name[my_date.weekday()]
	_workout_cal = run_SP(user, day, s_proc="sp_getWorkout")[0][2]
	app.logger.info("cals")
	app.logger.info(_workout_cal)
	met_dict = {"bike":7.0, "run":12.9, "walk":3.2}
	weight = run_SP(user, s_proc="sp_getProfile")[0][0]
	alt1 = run_SP(user, today, s_proc='sp_getAltWorkouts1')
	app.logger.info(alt1)
	alt1 = 0 if not alt1 else (met_dict[alt1[0][0]] * float(alt1[0][1]))
	alt2 = run_SP(user, today, s_proc='sp_getAltWorkouts2')
	app.logger.info(alt2)
	alt2 = 0 if not alt2 else (met_dict[alt2[0][0]] * 20)

	_workout_cal += alt1+alt2
	_net_cal = cals - _workout_cal
	return render_template('nutrition.html', cal=cals, workout_done = _workout_done, workout_cal= _workout_cal, \
		net_cal= _net_cal, protein=protein, fat=fat,carbs=carb, food_ids=zip(food_data,servings, meal))

	#return render_template('nutrition.html')

class FoodSearch(Form):
	 search = StringField('')

@app.route("/searchFood", methods=['GET', 'POST'])
@login_required
def searchFood():
	"""
	Allows user to search and add food to their day

	Requires MFP
	"""
	search = FoodSearch(request.form)
	if request.method == 'POST':
				return searchResults(search)
	return render_template("foodsearch.html", form=search)


@app.route('/results')
def searchResults(search):
		search_string = search.data['search']
		res = client.get_food_search_results(search_string)
		if not res:
				flash('No results found!')
				return redirect('/nutrition')
		else:
				# display results
				#app.logger.info("results: \n%s", res)
				food_items = res[:10]
				app.logger.info("food_items: %s" , food_items)
				data = [client.get_food_item_details(i.mfp_id) for i in res[:10]]
				food_data = zip(food_items,data)
				return render_template('foodsearch.html', form=search, res=food_data)

@app.route('/addFood', methods=['POST'])
def addFood():
	foods = request.form.getlist("food_id")
	servings = request.form.getlist("serving_size")
	meal = request.form['meal_selected']
	meal = "Breakfast" if meal=="" else meal
	app.logger.info(meal)
	data = [i for i in list(zip(foods, servings)) if i[1] != ""]
	user = request.cookies.get("current_user")
	macros = run_SP(user, today, s_proc="sp_getMacros")
	macros = [0,0,0,0] if not macros else macros[0]
	for food_id, serving in data:
		macros_one = list(getMacros(food_id, serving))
		macros = [sum(x) for x in zip(macros,macros_one)]
		app.logger.info("food id %s, serving %s,\n today %s", food_id,serving,today)
		run_SP(user,food_id,today,serving,meal, s_proc="sp_addFood")
		run_SP(user,today,*macros,s_proc="sp_updateMacros")
		#run_SP(user,today, *(getMacros(food_id)),s_proc="sp_updateMacros")
	return render_template("nutrition.html")

@app.route('/editFood', methods=['GET','POST'])
def editFood():
	if request.method == "POST":
		app.logger.info("gh")
	foods = request.form.getlist("f")
	servings = request.form.getlist("s")
	app.logger.info("foo %s\n s %s\n", foods, servings)
	data = [i for i in list(zip(foods, servings)) if i[1] != ""]
	app.logger.info("data: %s", data)
	user = request.cookies.get("current_user")

	for food_id, serving in data:
		run_SP(user, food_id, today, serving, s_proc="sp_editFood")

	data = run_SP(user, today, s_proc="sp_getTodayFood")
	app.logger.info(data)
	macros=[0,0,0,0]
	for food_id, serving,meal in data:
		macros_one = list(getMacros(food_id, serving))
		macros = [sum(x) for x in zip(macros,macros_one)]
		run_SP(user,today,*macros,s_proc="sp_updateMacros")
		#run_SP(user,today, *(getMacros(food_id)),s_proc="sp_updateMacros")
	return render_template("nutrition.html")



'''
------
WORKOUT PAGE
------
'''
@app.route("/workout?alt_workout1=bike&alt_workout2=run")
@app.route("/workout")
@login_required
def showWorkout():
	""" show the assigned workout for the day

	Depends on the day of the week and the user's goals

	"""

	user = request.cookies.get("current_user")
	# 104 is the length of the motivation table
	quote = getQuotes()

	my_date = date.today()
	day = calendar.day_name[my_date.weekday()]
	app.logger.info("today's day: %s", day)
	app.logger.info("user: %s", user)

	data = run_SP(user, day, s_proc= 'sp_getWorkout')

	workout = data[0][0]
	muscle_group = data[0][1]

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

	alt_chosen=False
	alt_info = ""
	data1 = run_SP(user, today, s_proc='sp_getAltWorkouts1')
	data2 = run_SP(user, today, s_proc='sp_getAltWorkouts2')
	if data1:
		alt_chosen=True
		alt_info = data1[0][0] + ", " + data1[0][1] + "mins"

	if data2:
		alt_info = alt_info + data2[0][0] + ", " + data2[0][1] + "mins"

	return render_template('workout.html', quote=quote, workout=workout,
				muscle_group=muscle_group, workout_done=workout_done,
				alternate_chosen=alt_chosen, alternate=alt_info)

@app.route('/workoutDone')
@login_required
def workoutDone():
	""" Clears out the planned workout when user clicks done!

	"""
	_user = request.cookies.get("current_user")
	my_date = date.today()
	run_SP(_user, my_date,s_proc='sp_workoutDone')

	return render_template('workout.html', workoutDone=True)

# @app.route("/postmethod", methods=["POST"])
# def postmethod():
# 	j =request.form["alt2"]
# 	app.logger.info(j)
# 	return j

@app.route("/update_workouts", methods=['GET','POST'])
@login_required
def udpateWorkout():
	_user = request.cookies.get("current_user")
	app.logger.info("in update workout")
	_w1 = request.form['alt_workout1']
	app.logger.info("i have w1 %s",_w1)
	#_w2= ""
	_w2 = request.form['alt_workout2']
	# app.logger.info("i have w2 %s",_w2)
	_t1 = request.form['time_1']
	_t2 = request.form['time_2']

	if not _w2:
		try:
			_w2 = run_SP(_user,today,s_proc='sp_getAltWorkouts2')[0][0]
			_t2 = run_SP(_user,today,s_proc='sp_getAltWorkouts2')[0][1]
		except IndexError:
			_w2 = ""
			_t2 = ""
	_t2=20
	run_SP(_user,today,_w1,_t1,_w2,_w2, s_proc="sp_setAltWorkouts")
	return redirect("workout")


#work on this
@app.route("/edit_workouts")
@login_required
def altWorkout():
	""" User can update alternate workouts

	"""
	_user = request.cookies.get("current_user")
	return render_template("edit_workouts.html", alt_workouts=["run", "walk", "bike"])



'''
-----
NEWS PAGE
-----
'''
@app.route("/news")
@login_required
def showNews():
	""" Blank template for news page
	"""
	user = request.cookies.get("current_user")
	# 8 is the length of the motivation table
	ids = random.sample(list(range(1,9)), 3)

	art1 = run_SP(ids[0], s_proc='sp_getArticle')
	art2 = run_SP(ids[1], s_proc='sp_getArticle')
	art3 = run_SP(ids[2], s_proc='sp_getArticle')
	return render_template('news.html', art1=art1, art2=art2, art3=art3)



'''
-----
GOALS PAGE
-----
'''
@app.route("/goals")
@login_required
def showGoals():
	""" Display user inputted goals and quotes

	"""

	user = request.cookies.get("current_user")
	quote = getQuotes()
	data = run_SP(user,s_proc='sp_getGoals')
	app.logger.info(data)
	try:
		lift_bool = True if data[0][0]==1 else False
		run_bool = True if data[0][1]==1 else False
		weight_diff = data[0][2]
		weight_goal = data[0][3]
		cal_goal = data[0][4]
	except IndexError:
		lift_bool = True
		run_bool = True
		weight_diff = 0
		weight_goal = 0
		cal_goal = 0

	try:
		cur_weight = run_SP(user,s_proc='sp_getWeight')[0][0]
	except IndexError:
		cur_weight = 0

	try:
		cur_cals = run_SP(user,today, s_proc='sp_getMacros')[0][0]
	except IndexError:
		cur_cals = 0

	manual=False
	goals = run_SP(user, s_proc='sp_getIndGoals')[0]
	i = 1
	ind_goals = []
	for x in goals:
		ind_goals.append([i, x])
		if x != '':
			manual=True
		i = i + 1



	return render_template('goals.html', quote=quote, lift_bool=lift_bool, run_bool=run_bool, weight_goal=weight_diff, \
		goal_lbs=weight_goal, cur_weight=cur_weight, goal_cals=cal_goal, today_cals=cur_cals, manual_goals=manual, \
		ind_goals = ind_goals)

@app.route("/update_goals",methods=['POST'])
@login_required
def updateGoals():
	""" User can update weight and workout goals

	"""

	_weight_diff = request.form['weight']
	_pr = request.form.getlist("pr")
	app.logger.info(request.form.getlist("pr"))
	_user = request.cookies.get("current_user")
	_pr = ','.join(_pr)
	app.logger.info("_pr: %s", _pr)
	# 1 = weightlifting, 2 = 5k
	_weight_goal = request.form['goal_weight']
	_cal_goal = request.form['cal_goal']

	_ind_goals = []
	_ind_goals.append(request.form['ind_goal_1'])
	_ind_goals.append(request.form['ind_goal_2'])
	_ind_goals.append(request.form['ind_goal_3'])
	_ind_goals.append(request.form['ind_goal_4'])
	_ind_goals.append(request.form['ind_goal_5'])

	for i in range(5):
		if _ind_goals[i] == '':
			try:
				_ind_goals[i] = run_SP(_user, s_proc='sp_getIndGoals')[0][i]
			except IndexError:
				_ind_goals[i] = 0

	if not _weight_goal:
		try:
			_weight_goal = run_SP(_user,s_proc='sp_getGoals')[0][3]
		except IndexError:
			_weight_goal = 0

	if not _cal_goal:
		try:
			_cal_goal = run_SP(_user, s_proc='sp_getGoals')[0][4]
		except IndexError:
			_cal_goal = 0

	run_SP(_user,_pr,_weight_diff, _weight_goal, _cal_goal, _ind_goals[0], _ind_goals[1], _ind_goals[2], _ind_goals[3], _ind_goals[4], s_proc="sp_editGoals")
	return render_template('goals.html')

@app.route("/edit_goals")
@login_required
def editGoals():
	_user = request.cookies.get("current_user")
	weights = ["Lose", "Maintain", "Gain"]
	goals = run_SP(_user, s_proc='sp_getIndGoals')[0]
	i = 1
	ind_goals = []
	for x in goals:
		ind_goals.append([i, x])
		i = i + 1
	return render_template("edit_goals.html", weights = weights, ind_goals = ind_goals)





'''
----------
HOME PAGE
----------
'''
@app.route("/success")
@app.route("/home")
@login_required
def homePage():
		""" The first page a user lands on when they log in successfully

			Shows a brief overview of their fitness tracking and goals and progress
		"""

		## This is how you get the username
		user = request.cookies.get("current_user")
		app.logger.info("This is the home page. Current user: %s", user)

		#MACROS CHART
		macros = run_SP(user, today, s_proc="sp_getMacros")
		macros = [0,0,0,0] if not macros else macros[0]
		protein = macros[1]
		carb = macros[2]
		fat = macros[3]
		pie_values = [protein, carb, fat]

		quote = getQuotes()
		my_date = date.today()
		day = calendar.day_name[my_date.weekday()]


		muscle_group =run_SP(user, day, s_proc= 'sp_getWorkout')
		app.logger.info(muscle_group)
		muscle_group = muscle_group[0][1]
		#muscle_group = "arms" #for debugging purposes

		pie_labels = ["protein", "carbohydrate", "fat"]
		pie_colors = ["#F7464A", "#46BFBD", "#FDB45C"]


		#WEEKLY CALORIES CHART
		cals = []
		dates = []
		for N in [6, 5, 4, 3, 2, 1, 0]:
			day = (datetime.now() - timedelta(days=N)).date()
			dates.append(day)
			info = run_SP(user, day, s_proc='sp_getMacros')
			app.logger.info(info)
			if info != [] and info != ():
				cal = info[0][0]
				app.logger.info(cal)
				cals.append(cal)
			else:
				cals.append(0)
		app.logger.info("cals: %s", cals)

		#WEIGHT PROGRESS CHART
		all_weight_updates = run_SP(user, s_proc='sp_getWeightProgress')
		app.logger.info("user %s", user)
		app.logger.info("WEIGHT %s", all_weight_updates)
		line_values = []
		line_labels = []
		for item in all_weight_updates:
			line_values.append(item[1])
			line_labels.append(item[2].strftime("%m-%d-%Y"))
		app.logger.info(line_labels)
		app.logger.info(line_values)
		line_max = 100 if not line_values else (max(line_values) + 100)

		try:
			goal_weight = run_SP(user,s_proc='sp_getGoals')[0][3]
		except IndexError:
			goal_weight = 0
		goal_weight = 0 if not goal_weight else goal_weight
		try:
			goal_cals = run_SP(user,s_proc='sp_getGoals')[0][4]
		except IndexError:
			goal_cals = 0
		goal_cals = 0 if not goal_cals else goal_cals
		app.logger.info(goal_cals)
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
		return render_template('home.html', user=user,calories=macros[0],
						quote=quote,workout=muscle_group,done=workout_done,
						g1_title="Today's Macros", set=zip(pie_values, pie_labels, pie_colors),
						g2_title="Calories Over Last Week", labels=dates, values=cals, max=(max(max(cals),goal_cals)+300),
						g3_title="Weight Progress", line_labels=line_labels, line_values=line_values, line_max=line_max,
						goal_weight=goal_weight, goal_cals=goal_cals)

@app.route("/signOut")
def signOut():
	""" Sign out and delte user cookies
	"""

	response = redirect('main')
	response.delete_cookie("current_user")
	return response

@app.route("/showSignIn")
def showSignIn():
	""" Show the sign in page to user
	"""

	response = redirect('home')
	response.delete_cookie("current_user")
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():
		""" Take in the user's answers to sign in form

		sets the user session up and creates user cookies for username

		"""
		#clean cookies
		response = redirect('showSignIn')
		#response.set_cookie("current_user", '', max_age=0)
		response.delete_cookie("current_user")
		# read the posted values from the UI
		_name = request.form['inputName']
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _password:
				data = run_SP(_name, s_proc='sp_loginUser')
				if len(data) == 0 :
					app.logger.error("User trying to log in not found")
					flash("This username is not found, try signing up")
					return json.dumps({'error': 'this username is not found'})
				if not check_password_hash(data[0][0], _password) and data[0][0] != _password:
						flash("Wrong password")
						app.logger.error("not a match for password")
						return json.dumps({'error':str(data[0])})
				else:
						## set the user cookies
						response = redirect('home')
						response.set_cookie("current_user", _name)
						app.logger.info("setting name cookie %s", _name)
						return response
		else:
				app.logger.error("incomplete signin")
				flash("Please input your username and password")
				return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route("/showSignUp")
def showSignUp():
	""" Show sign up form
	"""
	return render_template('signup.html')

@app.route("/")
@app.route("/main")
def main():
		""" SHows welcome page with signup button
		"""
		return render_template('index.html')

option_colors = [
	"#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
	"#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
	"#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]


@app.route('/signUp',methods=['POST'])
def signUp():
		""" Allows user to create a new account
			Sets session cookies for user
		"""

		#clean cookies
		response = redirect('home')
		response.set_cookie("current_user", '', max_age=0)
		# read the posted values from the UI
		_name = request.form['inputName']
		_email = request.form['inputEmail']
		_password = request.form['inputPassword']


		# validate the received values
		if _name and _email and _password:
				match = re.match('^[_a-z0-9-]+(\.[_a-z0-9-]+)*@[a-z0-9-]+(\.[a-z0-9-]+)*(\.[a-z]{2,4})$', \
					_email)

				if match == None:
						flash("Invalid email address")
						return json.dumps({'html':'<span>Enter the required fields</span>'})

				_hashed_password = generate_password_hash(_password)
				#_hashed_password = _password

				#save the user and password into the usr_tbl via sp_createUser stored proc.
				data =run_SP(_name,_email,_hashed_password, s_proc='sp_createUser')

				if len(data) is 0:
						## set the user cookies
						## we should probably comply to GDPR :P
						response = redirect('showSignUp')
						response.set_cookie("current_user", _name)
						app.logger.info("setting name cookie %s", request.cookies.get("current_user"))
						return response
				else:
						flash("Username exists already :(")
						app.logger.info("Unable to create user on mysql")
						return json.dumps({'error':str(data[0])})
		else:
				return json.dumps({'html':'<span>Enter the required fields</span>'})


if __name__ == "__main__":


		try:
			client = myfitnesspal.Client("Danz1ty")
		except myfitnesspal.keyring_utils.NoStoredPasswordAvailable:
			child = pexpect.spawn("myfitnesspal store-password Danz1ty")
			child.expect("MyFitnessPal Password for Danz1ty:")
			child.sendline("senior")

		app.run(debug=True)
