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
    def get(self, category_id):
        if category_id not in CATEGORY_KEYS:
            self.error(404)
            self.write('Category not found')
            return

        category_entry = ndb.Key(main.Category, category_id).get()

        all_items = main.Item.query(main.Item.category == category_id)

        result_list = []

        for entry in category_entry.history:
            result_list.append({'start_date': entry['start_date'], 'items': []})

        for item in all_items:
            # calculate quarter
            if item.date.month < 4:
                quarter = '01/01/'
            elif item.date.month < 7:
                quarter = '04/01/'
            elif item.date.month < 10:
                quarter = '07/01/'
            else:
                quarter = '10/01/'

            if item.date.year >= 2012:
                quarter += str(item.date.year)
                for idx1, obj in enumerate(category_entry.history):
                    if obj['start_date'] == quarter:
                        quarter_num = idx1
                item_index = None
                for idx2, item2 in enumerate(result_list[quarter_num]['items']):
                    if item2['title'] == item.title:
                        item_index = idx2
                        break
                if not item_index:
                    result_list[quarter_num]['items'].append({
                        'title': item.title, 'average': 0, 'total': 0, 'count': 0
                    })
                    item_index = -1
                result_list[quarter_num]['items'][item_index]['total'] += item.amount
                result_list[quarter_num]['items'][item_index]['count'] += 1
                result_list[quarter_num]['items'][item_index]['average'] = (
                    result_list[quarter_num]['items'][item_index]['total']/result_list[quarter_num]['items'][item_index]['count'])

        self.write(json.dumps({'data': result_list}))


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
    ('/api/categories/([a-z]+)/items/?', ItemsHandler),
    ('/api/fake/?', FakeHandler)
], debug=True)