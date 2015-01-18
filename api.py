#!/usr/bin/env python

import datetime
import webapp2
import json
import logging
import main
import os
import re
import urllib
from google.appengine.ext import ndb


class BaseHandler(webapp2.RequestHandler):
    def render(self, template, **kw):
        self.response.out.write(render_str(template, **kw))

    def write(self, *a, **kw):
        self.response.out.write(*a, **kw)


CATEGORY_KEYS = ['food', 'transportation', 'housing', 'school', 'recreational', 'vices']


class CategoriesHandler(BaseHandler):
    def get(self):
        category_objects = []

        for key in CATEGORY_KEYS:
            # category info
            category_entry = ndb.Key(main.Category, key).get()
            if not category_entry:
                continue
            average = category_entry.total / category_entry.count

            history = category_entry.history

            for quarter in history:
                if quarter['count'] > 0:
                    quarter['average'] = quarter['total'] / quarter['count']
                else:
                    quarter['average'] = 0

            category_obj = {'title': key, 'total': category_entry.total,
                'count': category_entry.count, 'average': average, 'history': history
            }
            category_objects.append(category_obj)

        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.write(json.dumps({'data': category_objects}))


class OverallHandler(BaseHandler):
    def get(self):
        food_entry = ndb.Key(main.Category, 'food').get()

        history_list = []
        for quarter in food_entry.history:
            d = {'title': 'food'}
            d['average'] = (quarter['total']/quarter['count'] if quarter['count']>0 else 0)
            d.update(quarter.items())
            del d['start_date']
            history_list.append({
                'start_date': quarter['start_date'],
                'categories': [
                    d
                ]
            })

        for key in CATEGORY_KEYS:
            if key == 'food':
                continue
            category_entry = ndb.Key(main.Category, key).get()
            if not category_entry:
                continue

            for index, quarter in enumerate(history_list):
                d = {'title': category_entry.key.id()}
                d['average'] = (category_entry.history[index]['total']/category_entry.history[index]['count']
                    if category_entry.history[index]['count']>0 else 0)
                d.update(category_entry.history[index].items())
                del d['start_date']
                history_list[index]['categories'].append(d)

        self.response.headers['Access-Control-Allow-Origin'] = '*'
        self.write(json.dumps({'data': history_list}))


class ItemsHandler(BaseHandler):
    def get(self):
        pass


class FakeHandler(BaseHandler):
    def get(self):
            CONST = """
    {
        "data": {
            "categories": [
                {
                    "title": "food",
                    "total": 662.90,
                    "count": 53,
                    "average": 11.75,
                    "history": [
                        {
                            "title": "Q1 2012",
                            "average": 1
                        },
                        {
                            "title": "Q2 2012",
                            "average": 2
                        },
                        {
                            "title": "Q3 2012",
                            "average": 3
                        },
                        {
                            "title": "Q4 2012",
                            "average": 4
                        },
                        {
                            "title": "Q1 2013",
                            "average": 5
                        }
                    ]
                },
                {
                    "title": "transportation",
                    "count": 31,
                    "average": 34.05903225806451,
                    "total": 1055.83,
                    "history": [
                        {
                            "title": "lol no more",
                            "average": 9000
                        }
                    ]
                }
            ]
        }
    }"""
            self.response.headers['Access-Control-Allow-Origin'] = '*'
            self.write(CONST)


app = webapp2.WSGIApplication([
    ('/api/categories/?', CategoriesHandler),
    ('/api/overall/?', OverallHandler),
    ('/api/items/?', ItemsHandler),
    ('/api/fake/?', FakeHandler)
], debug=True)