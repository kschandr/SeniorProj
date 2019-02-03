import logging
from flask import Flask, render_template,json,request, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash
from subprocess import call
import sys
import myfitnesspal

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'kaysha'
app.config['MYSQL_DATABASE_PASSWORD'] = 'seniorproject'
app.config['MYSQL_DATABASE_DB'] = 'kaysha'
app.config['MYSQL_DATABASE_HOST'] = 'ambari-head.csc.calpoly.edu'
mysql.init_app(app)

#### VERY INSECURE LOL
## Password is passed in as an argument (python app.py <your username> <your password> )
#my_username = sys.argv[1]
#password = sys.argv[2]

#@app.route("/home/<user>")
#def homePage(user):
#    return render_template('home.html', user=user)

@app.route("/nutrition")
def showNutrition():
	return render_template('nutrition.html')

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



	return render_template('profile.html')

@app.route("/friends")
def showFriends():
	return render_template('friends.html')


@app.route("/success")
@app.route("/home")
def homePage():
		## info when we get out ability to create and input food
		#user = request.cookies.get("logged_user")
		app.logger.info("Getting client from MFP")
		client = myfitnesspal.Client("Danz1ty")

		## stores totals in calories, macros (dict form)
		day_calories = client.get_date(2019,2,2).totals
		#app.logger.info("user day calories: %d", day_calories)
		return render_template('home.html', day_calories=day_calories)


@app.route("/showSignIn")
def showSignIn():
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():

		# read the posted values from the UI
		_name = request.form['inputName']
		app.logger.info("!!!!$$This is the input name %s", _name)
		app.logger.info("input name len %d", len(_name))
		_password = request.form['inputPassword']


		# validate the received values
		if _name and _password:
				#sql stuff
				conn = mysql.connect()
				cursor = conn.cursor()

				_hashed_password = generate_password_hash(_password)
				cursor.callproc('sp_loginUser',([_name]))
				data = cursor.fetchall()


				if not check_password_hash(data, _password):
						return json.dumps({'error':str(data[0])})
				else:
						conn.commit()
						return redirect('home')
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

				## save the username and hashed password into the myfitnesspal API
				#call(["myfitnesspal", "store-password", _name])
				#call(_hashed_password)


				#save the user and password into the usr_tbl via sp_createUser stored proc.
				cursor.callproc('sp_createUser',(_name,_email,_password))
				data = cursor.fetchall()

				if len(data) is 0:
						conn.commit()
						## set the user cookies
						response = redirect('home')
						response.set_cookie("logged_user", _name)
						return response
				else:
						return json.dumps({'error':str(data[0])})
		else:
				return json.dumps({'html':'<span>Enter the required fields</span>'})


if __name__ == "__main__":
		app.run(debug=True)