import re, json, pdb

# Things to match:
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
drink5 = u'\U0001F37A'
drink6 = u'\U0001F37B'

electric = u'\U0001F4A1'
electric2 = u'\U0001F50C'
movie       = u'\U0001F3A5'
cig         = u'\U0001F6AC'
durgs       = u'\U0001F489'
taxi        = u'\U0001F695'
videoGames = u'\U0001F3AE'
fries       =     u'\U0001F35F'
donut       =     u'\U0001F369' 
rent       =     u'\U0001F3E0'
shopping    = u'\U0001F3EC'

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
        coffee   ,
        fries    ,
        donut    
    ],
    "housing" : [
        "rent",
        "gas",
        "utilities",
        "electric",
        electric,
        electric2,
        rent     
    ],
    "transportation" : [
        "ticket",
        "airbnb",
        "hotel",
        "flight",
        "cab",
        "taxi",
        "lyft",
        "uber",
        taxi     

    ],
    "school" : [
        "school supplies",
        "books",
        "textbooks"
    ],
    "recreational" : [
        "movie",
        "dues",
        "tickets",
        "concert",
        movie    ,
        videoGames,
        shopping 
    ],
    "substances" : [
        "beer",
        "weed",
        cig   ,
        durgs ,
        drink ,
        drink1,
        drink2,
        drink3,
        drink4,
        drink5,
        drink6
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