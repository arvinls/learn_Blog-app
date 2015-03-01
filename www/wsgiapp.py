#!/usr/bin/env python
# -*- coding: utf-8 -*-

#wsgiapp.py

import logging; logging.basicConfig(level = logging.INFO)
import os, time
from datetime import datetime

from transwarp import db
from transwarp.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

# define datetime_fileter, input t,output unicode
def datetime_filter(t):
	dalta = int(time.time() - t)
	if delta < 60:
		return u'1分钟前'
	if delta < 3600:
		return u'%s分钟前' % (delta // 60)
	if delta < 86400:
		return u'%s分钟前' % (delta // 3600)
	if delta < 604800:
		return u'%s分钟前' % (delta // 86400)
	dt = datetime.fromtimestamp(t)
	return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


#initialize the database
db.create_engine(**configs.db)

#create WSGIApplication:
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))





#initialize the jinja2 Template engine:
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))
template_engine.add_filter('datetime', datetime_filter)

wsgi.template_engine = template_engine

#add the function of URL with @get/@post
import urls
wsgi.add_module(urls)

#start the local server at post 9000:
if __name__ == '__main__':
	wsgi.run(9000)