import logging,sys,argparse
#import myfitnesspal
from flask import Flask, render_template,json,request, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from subprocess import call

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
		_user = request.cookies.get("current_user")

		app.logger.info("input weight %s", _weight)
		app.logger.info("input height %s", _height)
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
				conn = mysql.connect()
				cursor = conn.cursor()
				cursor.callproc('sp_editHeight',([_height, _user]))
				data = cursor.fetchall()
				conn.commit()
				conn.close()

		return redirect('home')



@app.route("/nutrition")
def showNutrition():
	return render_template('nutrition.html')

@app.route("/edit_profile")
def showEditProfile():
	user = request.cookies.get("current_user")
	return render_template('edit_profile.html', user=user)

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
	_user = request.cookies.get("current_user")

	conn = mysql.connect()
	cursor = conn.cursor()
	cursor.callproc('sp_getProfile',([_user]))
	data = cursor.fetchall()
	conn.commit()
	conn.close()
	app.logger.info("data %s", data[0][0])
	#_weight = data.weight 
	#_height = data.height
	_weight = data[0][0]
	_height = data[0][1]

	return render_template('profile.html', user=_user, height = _height, weight = _weight)

@app.route("/friends")
def showFriends():
	return render_template('friends.html')


@app.route("/success")
@app.route("/home")
def homePage():

		## This is how you get the username
		user = request.cookies.get("current_user")
		app.logger.info(user)
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
				if not check_password_hash(data, _password):
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
				cursor.callproc('sp_createUser',(_name,_email,_password))
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
