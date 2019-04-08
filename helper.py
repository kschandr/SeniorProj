import re
## helper constants

activity_dict = {"Sedentary": 1.2,
								"Lightly": 1.375,
								"Moderately": 1.55,
								"Very": 1.725,
								"Extremely": 1.9}

## helper functions

def convertFeetToInches(data):
	""" convert feet to inches

	Parameters:
	------
	data: int list
		The list of height in feet and inches

	"""
	data =  list(map(int, data))
	data[1] += data[0]*12 + data[1]
	return int(data[1])

def convertInchesToFeet(inches):
	""" convert inches to feet

	Parameters:
	------
	inches: int
		The inches

	"""
	inches = int(inches)
	feet = inches//12
	i = inches %12
	return str(feet) + "'" + str(i)

def calcTDEE(BMR, activity_level):
	""" calculate TDEE based on BMR and activity level

	Parameters:
	------
	BMR: int
		Basal Metabolic Rate
	activity_level: str
		Sedentary, lightly active, very active, etc.

	"""

	return round(BMR * getActivity(activity_level), 2)

def calcBMR(height, weight, age, sex):
	"""Calculate the BMR

	Parameters:
	-----
	height: int
		height in inches
	weight: int
		weight in pounds
	age: int
	sex: str
		female or male

	"""

	i = (int(height) * 4.7) + (int(weight) * 4.35)- (int(age) * 4.7)
	if sex == "female":
		return round(i + 655,2)
	else:
		return round(i + 66, 2)

def calcBMI(height, weight):
	""" calculate BMI

	Parameters:
	----
	height: int
		in inches
	weight: int
		in pounds

	"""

	height_m = height * 0.0254
	weight_kg = weight*0.4535
	return round(weight_kg/((height_m)**2),2)

def getActivity(input):
	""" returns a value for a given string input

	Parameter:
	----
	input: str
		contains a description of activity level

	"""

	activities = ["Sedentary", "Lightly", "Moderately", "Very", "Extremely"]
	for a in activities:
		p = re.compile(a+"+")
		if p.match(input):
			return activity_dict[a]
	return activity_dict["Sedentary"]
