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
    return false

def parseNote(note, regexes):
    item = ""

    for index, regex in enumerate(regexes):
        if regex.match(note):
            # if description has 2 matching classifiers, toss it out
            if item:
                return False

            # returns tuple (category, keyword)
            item = regexIndexToKeyword(index)
    return item

def classifyPayment(data):
    regexes = compileRegex()

    items = []

    # only try to classify if payment went through
    for index, payment in enumerate(data["data"]):
        if payment["status"] == "settled":
            amount = payment["amount"]
            date = payment["date_created"]
            note = payment["note"]
            _id = payment["id"]

            parse_note_tuple = parseNote(note, regexes)
            if parse_note_tuple:
                category, item = parseNote(note, regexes)
            else:
                continue

            logging.debug('index, item: ' + str(index) + ' ' + str(item))

            # send to db if regex matched value
            if item:
                items.append({'title': item, 'amount': amount, 'date': date, 'note': note,
                    'category': category, 'id': _id})
            logging.debug(str(len(items)))

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
            logging.debug('bool(response_json): ' + str(bool(response_json)))
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
