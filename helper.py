## helper constants

activity_dict = {"sedentary": 1.2,
								"light": 1.375,
								"moderate": 1.55,
								"very": 1.725,
								"extreme": 1.9}

## helper functions

def convertFeetToInches(data):
	data =  list(map(int, data))
	data[1] += data[0]*12 + data[1]
	return int(data[1])

def convertInchesToFeet(inches):
	inches = int(inches)
	feet = inches//12
	i = inches %12
	return str(feet) + "'" + str(i)

def calcTDEE(BMR, activity_level):
	return round(BMR * activity_dict[activity_level], 2)

def calcBMR(height, weight, age, sex):
	i = (int(height) * 4.7) + (int(weight) * 4.35)- (int(age) * 4.7)
	if sex == "female":
		return round(i + 655,2)
	else:
		return round(i + 66, 2)

def calcBMI(height, weight):
	height_m = height * 0.0254
	weight_kg = weight*0.4535
	return round(weight_kg/((height_m)**2),2)