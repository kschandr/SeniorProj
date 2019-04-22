import logging,sys,argparse, random, re
import myfitnesspal
from flask import Flask, render_template,json,request, redirect, url_for, flash, Markup
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from subprocess import call
from helper import *
import datetime
from datetime import date
import calendar
from math import ceil
from wtforms import Form, StringField, SelectField


"""
Requirements:
pip install myfitnesspal
pip install Flask-WTF
"""

app = Flask(__name__)
# To use session dictionary, make sure to have app secret key
# generated in terminal via: python -c 'import os; print(os.urandom(16))'
app.secret_key = b'\xcdW\x16\x13\xcfU\xf0p\xd5\xdf\xef\xa7\x9b\xac\xb0H'
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kaysha'
app.config['MYSQL_DATABASE_PASSWORD'] = 'seniorproject'
app.config['MYSQL_DATABASE_DB'] = 'kaysha'
app.config['MYSQL_DATABASE_HOST'] = 'ambari-head.csc.calpoly.edu'
mysql.init_app(app)


client = ""
today = date.today().strftime('%Y-%m-%d')
app.logger.info("TODAY: ",today)

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

def getMacros(food_id):
	data = client.get_food_item_details(food_id)
	return (round(data.calories,2), round(data.protein,2),
		round(data.fat,2), round(data.carbohydrates,2))


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
	cals = 0 if not macros else macros[0][0]
	protein = 0 if not macros else macros[0][1]
	fat = 0 if not macros else macros[0][2]
	carb = 0 if not macros else macros[0][3]

	return render_template('nutrition.html', cal=cals, protein=protein, fat=fat,carbs=carb)

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
				return render_template('foodsearch.html', form=search, res=res[:10])

@app.route('/addFood', methods=['POST'])
def addFood():
	foods = request.form.getlist("foodSelection")
	user = request.cookies.get("current_user")
	macros = run_SP(user, today, s_proc="sp_getMacros")
	app.logger.info("in add food %s",macros)
	macros = [0,0,0,0] if not macros else macros[0]
	for food_id in foods:
		app.logger.info("food id: %s",food_id)
		app.logger.info("today: %s",today)
		macros_one = list(getMacros(food_id))
		macros = [sum(x) for x in zip(macros,macros_one)]
		app.logger.info("today %s, macros %s",today,macros)
		run_SP(user,food_id,today,s_proc="sp_addFood")
		run_SP(user,today,*macros,s_proc="sp_updateMacros")
		#run_SP(user,today, *(getMacros(food_id)),s_proc="sp_updateMacros")
	return render_template("nutrition.html")



'''
------
WORKOUT PAGE
------
'''

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

	return render_template('workout.html', quote=quote, workout=workout,
				muscle_group=muscle_group, workout_done=workout_done)

@app.route('/workoutDone')
@login_required
def workoutDone():
	""" Clears out the planned workout when user clicks done!

	"""

	_user = request.cookies.get("current_user")
	my_date = date.today()
	run_SP(_user, my_date,s_proc='sp_workoutDone')

	return render_template('workout.html', workoutDone=True)



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
		weight_goal = data[0][2]
	except IndexError:
		lift_bool = True
		run_bool = True
		weight_goal = 0
	return render_template('goals.html', quote=quote, lift_bool=lift_bool, run_bool=run_bool, weight_goal=weight_goal)

@app.route("/update_goals",methods=['POST'])
@login_required
def updateGoals():
	""" User can update weight and workout goals

	"""

	_weight_goal = request.form['weight']
	_pr = request.form.getlist("pr")
	app.logger.info(request.form.getlist("pr"))
	_user = request.cookies.get("current_user")
	_pr = ','.join(_pr)
	app.logger.info("_pr: %s", _pr)
	# 1 = weightlifting, 2 = 5k
	run_SP(_user,_pr,_weight_goal, s_proc="sp_editGoals")
	return render_template('goals.html')

@app.route("/edit_goals")
@login_required
def editGoals():
	weights = ["Lose", "Maintain", "Gain"]
	return render_template("edit_goals.html", weights = weights)



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
		#app.logger.info("This is the home page. Current user: %s", user)
		macros = run_SP(user, today, s_proc="sp_getMacros")
		app.logger.info("MACROS:", macros)
		# if macros == ():
		# 	macros = []
		# 	macros[0] = [0,0,0]
		#macros = [[0,0,0]]

		#app.logger.info(macros[0])

		quote = getQuotes()
		my_date = date.today()
		day = calendar.day_name[my_date.weekday()]
		muscle_group = run_SP(user, day, s_proc= 'sp_getWorkout')[0][1]

		pie_labels = ["protein", "carbohydrate", "fat"]
		pie_colors = ["#F7464A", "#46BFBD", "#FDB45C"]


		#user = request.cookies.get("current_user")
		#user = "k" # only one with data rn
		app.logger.info(macros.protein)
		# day = date.today()
		day = today
		app.logger.info(day)
		data = run_SP(user, day, s_proc='sp_getMacros')
		app.logger.info(data)
		protein = data[0][0]
		carb = data[0][1]
		fat = data[0][2]
		pie_values = [protein, carb, fat]


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
		## stores totals in calories, macros (dict form)
		#day_calories = client.get_date(2019,2,2).totals
		#app.logger.info("user day calories: %d", day_calories)
		#return render_template('home.html', day_calories=day_calories, user=user)
		return render_template('home.html', user=user,calories=macros[0][0],
						quote=quote,workout=muscle_group,done=workout_done, title="Today's Macros", set=zip(pie_values, pie_labels, pie_colors))

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
		response = redirect('home')
		#response.set_cookie("current_user", '', max_age=0)
		response.delete_cookie("current_user")
		# read the posted values from the UI
		_name = request.form['inputName']
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _password:
				#_hashed_password = generate_password_hash(_password)
				data = run_SP(_name, s_proc='sp_loginUser')
				if len(data) == 0 :
					app.logger.error("User trying to log in not found")
					flash("This username is not found, try signing up")
					return json.dumps({'error': 'this username is not found'})
				if not check_password_hash(data[0][0], _password):
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


# @app.route("/chart")
# def chart():
# 	labels = ["January","February","March","April","May","June","July","August"]
# 	values = [10,9,8,7,6,4,7,8]
# 	colors = [ "#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA","#ABCDEF", "#DDDDDD", "#ABCABC"  ]
# 	return render_template('chart.html', set=zip(values, labels, colors))


option_colors = [
	"#F7464A", "#46BFBD", "#FDB45C", "#FEDCBA",
	"#ABCDEF", "#DDDDDD", "#ABCABC", "#4169E1",
	"#C71585", "#FF4500", "#FEDCBA", "#46BFBD"]

@app.route('/bar')
def bar():
	labels = []
	values = []

	bar_labels=labels
	bar_values=values
	return render_template('bar_chart.html', title="This Week's Calories", labels=bar_labels, values=bar_values)

@app.route('/line')
def line():
	labels = []
	values = []

	line_labels=labels
	line_values=values
	return render_template('line_chart.html', title='Workouts This Week', max=17000, labels=line_labels, values=line_values)

@app.route('/pie')
def pie():
	pie_labels = ["protein", "carbohydrate", "fat"]
	pie_colors = ["#F7464A", "#46BFBD", "#FDB45C"]

	#user = request.cookies.get("current_user")
	user = "k" # only one with data rn
	app.logger.info(user)
	# day = date.today()
	day = "2019-04-18"
	app.logger.info(day)
	data = run_SP(user, day, s_proc='sp_getMacros')
	app.logger.info(data)
	protein = data[0][0]
	carb = data[0][1]
	fat = data[0][2]
	pie_values = [protein, carb, fat]
	return render_template('pie_chart.html', title="Today's Macros", set=zip(pie_values, pie_labels, pie_colors))


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
						flash("Username exists already :(")
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
		#call(["myfitnesspal", "store-password", "Danz1ty"])
		client = myfitnesspal.Client("Danz1ty")

		app.run(debug=True)
