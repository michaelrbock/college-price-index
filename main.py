#!/usr/bin/env python

import webapp2
import jinja2
import json
import logging
import os
import re
import urllib
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

def compileRegex():
    # compile all the keywords as regex
    regexes = []
    for keyword in keywords:
        regexes.append(re.compile(keyword, re.IGNORECASE))
    return regexes

def parseNote(note, regexes):
    item = ""
    for index, regex in enumerate(regexes):
        if regex.match(note):
            # if description has 2 matching classifiers, toss it out
            if item:
                return False
            item = keywords[index]
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

            item = parseNote(note, regexes)
            logging.debug('index, item: ' + str(index) + ' ' + str(item))

            # send to db if regex matched value
            if item:
                items.append({'title': item, 'amount': amount, 'date': date, 'note': note})
            logging.debug(str(len(items)))

    logging.debug('FINAL ' + str(len(items)))
    return items


class OAuthSuccessHandler(BaseHandler):
    def get(self):
        """Get access_token and then get payments and add to db all in one!"""

        access_token = self.request.get('access_token')

        # make payments API call with access_token
        url = 'https://api.venmo.com/v1/payments?limit=500&access_token=' + access_token
        response = urlfetch.fetch(url, deadline=30)

        logging.debug('response.status_code ' + str(response.status_code) + '////')

        logging.debug(response.content + '////')


        # parse json, create db entries
        if response.status_code == 200:
            response_json = json.loads(response.content)
            logging.debug('bool(response_json): ' + str(bool(response_json)))
            items = classifyPayment(response_json)
        self.write(str(items) + ' //// ')

        for item in items:
            item_entry = Item(date=dateutil.parser.parse(item['date']), title=item['title'],
                amount=item['amount'], note=item['note'])
            # self.write(str(item_entry))
            item_entry.put()
            self.write(item['title'] + ' was put in db, ')


class StatsHandler(BaseHandler):
    def get(self):
        self.write('stats')


class Item(ndb.Model):
    date = ndb.DateTimeProperty(required=True)
    title = ndb.StringProperty(required=True)
    amount = ndb.FloatProperty(required=True)
    note = ndb.TextProperty(required=True)


class Category(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)
    title = ndb.StringProperty(required=True)


class User(ndb.Model):
    date_created = ndb.DateTimeProperty(auto_now_add=True)



app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signin/?', OAuthStartHandler),
    ('/success/?', OAuthSuccessHandler),
    ('/stats/?', StatsHandler)
], debug=True)
