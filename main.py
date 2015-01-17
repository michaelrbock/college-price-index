#!/usr/bin/env python

import webapp2
import jinja2
import json
import os
import urllib
from google.appengine.ext import ndb


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

        scope = 'access_feed'
        redirect_uri = urllib.quote_plus('https://venmoprice.appspot.com/success')

        self.write(('https://api.venmo.com/v1/oauth/authorize?client_id={0}&scope={1}&'
            'redirect_uri={2}').format(client_id, scope, redirect_uri))


class OAuthSuccessHandler(BaseHandler):
    def get(self):
        self.write('success!')


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signin/?', OAuthStartHandler),
    ('/success/?', OAuthSuccessHandler)
], debug=True)
