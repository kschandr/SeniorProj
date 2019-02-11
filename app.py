import logging,sys,argparse
#import myfitnesspal
from flask import Flask, render_template,json,request, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from subprocess import call
from helper import *
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
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.callproc('sp_editWeight',([_weight, _user]))
				data = cursor.fetchall()
				conn.commit()
				conn.close()

		if _height:
			#sql stuff
				height_arr= _height.split("'")
				##currently the height table stores ints. So round to neared int
				h_inch = convertFeetToInches(height_arr)
				app.logger.info("hegiht in inches %d", h_inch)
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.callproc('sp_editHeight',([h_inch, _user]))
				data = cursor.fetchall()
				conn.commit()
				conn.close()
		if _age and _sex and _activity:
			conn = mysql.connect()
			cursor = conn.cursor()
			cursor.callproc('sp_editAgeSexActivity', ([_age, _sex, _activity, _user]))
			conn.commit()
			conn.close()

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
	return render_template('workout.html')

@app.route("/news")
def showNews():
	return render_template('news.html')

@app.route("/goals")
def showGoals():
	return render_template('goals.html')

@app.route("/profile")
def showProfile():
	_weight= _height= _age= _sex= bmr=bmi=tdee=disp_height=0
	_user = request.cookies.get("current_user")
	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_getProfile',([_user]))
	data = cursor.fetchall()
	conn.commit()
	conn.close()
	app.logger.info("data: %s", data)
	#app.logger.info("data %s", data[0][0])
	#_weight = data.weight
	#_height = data.height
	if data[0][0]:
		_weight = data[0][0]
		app.logger.info("table %d", data[0][1])
		_height = data[0][1]
		disp_height = convertInchesToFeet(_height)
		_age = data[0][2]
		_sex = data[0][3]
		_activity = data[0][4]
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
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():
		#clean cookies
		response = redirect('home')
		response.set_cookie("current_user", '', max_age=0)
		# read the posted values from the UI
		_name = request.form['inputName']
		app.logger.info("!!!!$$This is the input name %s", _name)
		#app.logger.info("input name len %d", len(_name))
		_password = request.form['inputPassword']

		# validate the received values
		if _name and _password:
				#sql stuff
				conn = mysql.connect()
				cursor = conn.cursor()
				#_hashed_password = generate_password_hash(_password)
				cursor.callproc('sp_loginUser',([_name]))
				data = cursor.fetchall()
				if len(data) == 0 :
					return json.dumps({'error': 'this username is not found'})
				if not check_password_hash(data[0][0], _password):
						app.logger.error("not a match for password")
						return json.dumps({'error':str(data[0])})
				else:
						conn.commit()
						conn.close()
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
				#sql stuff
				conn = mysql.connect()
				cursor = conn.cursor()
				_hashed_password = generate_password_hash(_password)

				#save the user and password into the usr_tbl via sp_createUser stored proc.
				cursor.callproc('sp_createUser',(_name,_email,_hashed_password))
				data = cursor.fetchall()

				if len(data) is 0:
						conn.commit()
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
