#!/usr/bin/env python

import webapp2
import jinja2
import json
import logging
import os
import re
import urllib
from collections import defaultdict
from google.appengine.ext import ndb
from google.appengine.api import urlfetch

import sys
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))
import dateutil.parser


jinja_environment = jinja2.Environment(autoescape=True,
    loader=jinja2.FileSystemLoader(os.path.join(os.path.dirname(__file__), 'templates')))


def render_str(template, **params):
    t = jinja_environment.get_template(template)
    return t.render(params)


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


class MainHandler(BaseHandler):
    def get(self):
        self.render('index.html')


class OAuthStartHandler(BaseHandler):
    def get(self):
        # read client id from secrets file
        folder = os.path.dirname(os.path.realpath(__file__))
        file_path = os.path.join(folder, 'secrets.txt')
        f = open(file_path, 'r')
        client_id = f.read()
        f.close()

        scope = urllib.quote('access_profile')
        redirect_uri = urllib.quote_plus('https://collegepriceindex.appspot.com/success')

        self.redirect(('https://api.venmo.com/v1/oauth/authorize?client_id={0}&scope={1}&'
            'response_type=token&redirect_uri={2}').format(client_id, scope, redirect_uri))


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
drugs       = u'\U0001F489'
taxi        = u'\U0001F695'
videoGames = u'\U0001F3AE'
fries       =     u'\U0001F35F'
donut       =     u'\U0001F369'
rent       =     u'\U0001F3E0'
shopping    = u'\U0001F3EC'

keywords = {
    "food" : [
        "meal",
        "breakfast",
        "dinner",
        "lunch"
        "burger",
        "pizza",
        "bread",
        "cereal",
        "drinks",
        "sandwich",
        "burrito",
        "chipotle",
        "panera",
        "jimmy johns",
        "subway",
        "starbucks",
        "noodles",
        "quiznos",
        "juice",
        "smoothie",
        "froyo",
        "sushi",
        "fries",
        "grocer",
        "milk",
        "eggs",
        "bacon",
        hamburger,
        pizza    ,
        chicken  ,
        chicken1 ,
        sushi    ,
        sushi2   ,
        spaghetti,
        icecream ,
        icecream1,
        icecream2,
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
        "cable",
        electric,
        electric2,
        rent
    ],
    "transportation" : [
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
        "book"
    ],
    "recreational" : [
        "movie",
        "dues",
        "ticket",
        "concert",
        movie    ,
        videoGames,
        shopping,
        bowling
    ],
    "vices" : [
        "beer",
        "weed",
        cig   ,
        drugs ,
        drink ,
        drink1,
        drink2,
        drink3,
        drink4,
        drink5,
        drink6,
        shrooms
    ]
}

def compileRegex():
    # compile all the keywords as regex
    regexes = []
    for categories, array in keywords.iteritems():
        for keyword in array:
            regexes.append(re.compile(keyword, re.IGNORECASE))
    return regexes

def regexIndexToKeyword(index):
    sumIndices = 0;
    for category, value in keywords.iteritems():
        # check if index we're searching for is this category's array
        if index < (sumIndices + len(value)):
            return (category, value[index - sumIndices])

        sumIndices += len(value)

def is_ascii(s):
    return all(ord(c) < 128 for c in s)


def parseNote(note, regexes):
    item = None

    for index, regex in enumerate(regexes):
        if re.search(regex, note):
            # if description has 2 matching classifiers, toss it out
            if item:
                logging.debug('if item is true, item= ' + str(item))
                return False

            # returns tuple (category, keyword)
            item = regexIndexToKeyword(index)

            if is_ascii(item[1]):
                logging.debug('item = ' + item[1])
    return item

def classifyPayment(data):
    regexes = compileRegex()

    items = []

    # only try to classify if payment went through
    for payment in data["data"]:
        if payment["status"] == "settled":
            amount = payment["amount"]
            date = payment["date_created"]
            note = payment["note"]
            _id = payment["id"]

            parse_note_tuple = parseNote(note, regexes)
            if parse_note_tuple:
                category, item = parse_note_tuple
            else:
                continue

            # send to db if regex matched value
            if item:
                items.append({'title': item, 'amount': amount, 'date': date, 'note': note,
                    'category': category, 'id': _id})

    logging.debug('FINAL ' + str(len(items)))
    return items


class OAuthSuccessHandler(BaseHandler):
    def get(self):
        """Get access_token and then get payments and add to db all in one!"""

        access_token = self.request.get('access_token')

        # make payments API call with access_token
        url = 'https://api.venmo.com/v1/payments?limit=5000&access_token=' + access_token
        response = urlfetch.fetch(url, deadline=30)

        logging.debug('response.status_code ' + str(response.status_code))

        logging.debug(response.content)


        # parse json, create db entries
        if response.status_code == 200:
            response_json = json.loads(response.content)
            items = classifyPayment(response_json)

        categories = defaultdict(list)

        for item in items:
            categories[item['category']].append(item['amount'])
            item_entry = Item(date=dateutil.parser.parse(item['date']), title=item['title'],
                amount=item['amount'], note=item['note'], category=item['category'], id=item['id'])
            item_entry.put()

        for key in categories:
            # query db to get the category, update info
            category_entry = ndb.Key(Category, key).get()
            if not category_entry:
                category_entry = Category(id=key, total=sum(categories[key]),
                    count=len(categories[key]))
            else:
                category_entry.total += sum(categories[key])
                category_entry.count += len(categories[key])
            category_entry.put()

        self.write('Thanks for adding {0} items in {1} categories the College Price Index! '.format(
            str(len(items)), str(len(categories))))
        self.write('We appreciate your contribution to science! ')


class StatsHandler(BaseHandler):
    def get(self):
        self.write('stats')


class Item(ndb.Model):
    date = ndb.DateTimeProperty(required=True)
    title = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    note = ndb.TextProperty(required=True)
    category = ndb.StringProperty()


class Category(ndb.Model):
    # id is lowecase name
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    total = ndb.FloatProperty()
    count = ndb.IntegerProperty()


class User(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signin/?', OAuthStartHandler),
    ('/success/?', OAuthSuccessHandler),
    ('/stats/?', StatsHandler)
], debug=True)
