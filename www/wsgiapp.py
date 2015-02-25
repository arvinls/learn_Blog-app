#wsgiapp.py

import logging; logging.basicConfig(level = logging.INFO)
import os

from transwarp import db
from transwarp.web import WSGIApplication, Jinja2TemplateEngine

from config import configs

#initialize the database
db.create_engine(**configs.db)

#create WSGIApplication:
wsgi = WSGIApplication(os.path.dirname(os.path.abspath(__file__)))

#initialize the jinja2 Template engine:
template_engine = Jinja2TemplateEngine(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates'))

wsgi.template_engine = template_engine

#add the function of URL with @get/@post
import urls
wsgi.add_module(urls)

#start the local server at post 9000:
if __name__ == '__main__':
	wsgi.run(9000)