from flask import Flask, render_template,json,request, redirect, url_for
from flaskext.mysql import MySQL
from werkzeug import generate_password_hash, check_password_hash

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

@app.route("/home")
def homePage():
		return render_template('home.html')


@app.route("/showSignIn")
def showSignIn():
	return render_template('signin.html')

@app.route('/signIn',methods=['POST'])
def signIn():

		# read the posted values from the UI
		_name = request.form['inputName']
		_password = request.form['inputPassword']


		# validate the received values
		if _name and _password:
				#sql stuff
				conn = mysql.connect()
				cursor = conn.cursor()

				#_hashed_password = generate_password_hash(_password)
				cursor.callproc('sp_loginUser',(_name,_password))
				data = cursor.fetchall()

				if len(data) is not 0:
						return json.dumps({'error':str(data[0])})
				else:
						conn.commit()
						return redirect(url_for('showSuccess'))
		else:
				return json.dumps({'html':'<span>Enter the required fields</span>'})

@app.route("/success")
def showSuccess():
	return render_template('success.html')

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
				#_hashed_password = generate_password_hash(_password)
				cursor.callproc('sp_createUser',(_name,_email,_password))
				data = cursor.fetchall()

				if len(data) is 0:
						conn.commit()
						return redirect(url_for('showSuccess'))
				else:
						return json.dumps({'error':str(data[0])})
		else:
				return json.dumps({'html':'<span>Enter the required fields</span>'})


if __name__ == "__main__":
		app.run(debug=True)