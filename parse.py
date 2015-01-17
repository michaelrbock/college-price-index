import re, json

# Things to match:
keywords = [
	"burger",
	"cereal",
	"rent",
	"gas",
	"bread",
	"beer",
	"weed",
	"books",
	"textbooks",
	"dinner",
	"pizza"
]

regexes = []

def compileRegex():
	# compile all the keywords as regex
	for keyword in keywords:
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

def parseNote(note):
	item = ""
	for index, regex in enumerate(regexes):
		if regex.match(note):
			# if description has 2 matching classifiers, toss it out
			if item:
				return False
			item = keywords[index]
	return item

def main():
	# read file in to variable and make is readable as json
	with open("testData.json", "r") as myfile:
		data = json.load(myfile)
	# call method to test
	classifyPayment(data)

if __name__ == "__main__": main()