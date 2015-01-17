#!/usr/bin/env python

import webapp2
import jinja2
import json
import os
import urllib
from google.appengine.ext import ndb
from google.appengine.api import urlfetch


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


class OAuthSuccessHandler(BaseHandler):
    def get(self):
        """Get access_token and then get payments and add to db all in one!"""

        access_token = self.request.get('access_token')
        # self.write('success! ' + access_token + '\n')

        # make payments API call with access_token
        url = 'https://api.venmo.com/v1/payments?limit=1000&access_token=' + access_token
        result = urlfetch.fetch(url)

        if result.status_code == 200:
            self.write(result.content)


app = webapp2.WSGIApplication([
    ('/', MainHandler),
    ('/signin/?', OAuthStartHandler),
    ('/success/?', OAuthSuccessHandler)
], debug=True)
