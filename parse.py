import re, json, pdb

# Things to match:
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
        "fries"
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
        "flight"
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
        "weed"
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
	with open("testData.json", "r") as myfile:
		data = json.load(myfile)
	# call method to test
	classifyPayment(data)

if __name__ == "__main__": main()