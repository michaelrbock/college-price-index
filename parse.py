import re, json, pdb

# Things to match:

# print u'[', u'\U0001F300-\U0001F5FF', u'\U0001F600-\U0001F64F',
# 			u'\U0001F680-\U0001F6FF', u'\u2600-\u26FF\u2700-\u27BF]+'

hamburger = u'\U0001F354'
pizza = u'\U0001F355'
chicken = u'\U0001F356'
chicken1 = u'\U0001F357'
sushi = u'\U0001F363'
sushi2 = u'\U0000E344'
bowling = u'\U0001F3B3'
spaghetti = u'\U0001F35D'
icecream = u'\U0001F366'
icecream1 = u'\U0001F367'
icecream2 = u'\U0001F368'
shrooms = u'\U0001F344'
cinRoll = u'\U0001F365'
coffee = u'\U0001F375'
drink = u'\U0001F375'
drink1 = u'\U0001F376'
drink2 = u'\U0001F377'
drink3 = u'\U0001F378'
drink4 = u'\U0001F379'
drink4 = u'\U0001F37A'
drink4 = u'\U0001F37B'



keywords = {
    "meals": [
        "breakfast",
        "dinner",
        "lunch"
    ],
    "food" : [
        "burger",
        "pizza",
        "bread",    
        "cereal",
        "drinks",
        "sandwich",
        "burrito",
        "chipotle",
        "froyo",
        "sushi",
        "fries",
        hamburger,
		pizza    ,
		chicken  ,
		chicken1 ,
		sushi    ,
		sushi2   ,
		bowling  ,
		spaghetti,
		icecream ,
		icecream1,
		icecream2,
		shrooms  ,
		cinRoll  ,
		coffee   
    ],
    "housing" : [
        "rent",
        "gas",
        "utilities",
        "electric",
    ],
    "transportation" : [
        "ticket",
        "airbnb",
        "hotel",
        "flight",
        "cab",
        "taxi",
        "lyft"
    ],
    "school" : [
        "school supplies",
        "books",
        "textbooks"
    ],
    "extracurriculars" : [
        "movie",
        "dues",
        "tickets",
        "concert",
        "beer",
        "weed",
        drink ,
		drink1,
		drink2,
		drink3,
		drink4,
		drink4,
		drink4
    ]
}

regexes = []

def compileRegex():
	# compile all the keywords as regex
	for categories, array in keywords.iteritems():
		for keyword in array:
			regexes.append(re.compile(keyword, re.IGNORECASE)) 

def classifyPayment(data):
	compileRegex();

	# only try to classify if payment went through
	for index, payment in enumerate(data["data"]):
		if payment["status"] == "settled":
			amount = payment["amount"]
			date = payment["date_created"]
			note = payment["note"]

			item = parseNote(note)

			# send to db if regex matched value
			if item:
				print "matched: "+str(item)
				# sendNewData(item, amount, date)

def regexIndexToKeyword(index):
	sumIndices = 0;
	for category, value in keywords.iteritems():
		# check if index we're searching for is this category's array		
		if index < (sumIndices + len(value)):
			return (category, value[index - sumIndices])

		sumIndices += len(value)
	return false

def parseNote(note):
	item = ""

	for index, regex in enumerate(regexes):
		if regex.match(note):
			# if description has 2 matching classifiers, toss it out
			if item:
				return False

			# returns tuple (category, keyword)
			item = regexIndexToKeyword(index)
	return item

def main():
	# read file in to variable and make is readable as json
	with open("testData2.json", "r") as myfile:
		data = json.load(myfile)
	# call method to test
	classifyPayment(data)

if __name__ == "__main__": main()