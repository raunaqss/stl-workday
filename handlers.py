import datetime
import jinja2
import os
import webapp2

from google.appengine.ext import db


# initializing jinja2
template_dir = os.path.join(os.path.dirname(__file__), 'templates')
jinja_env = jinja2.Environment(loader = jinja2.FileSystemLoader(template_dir),
							   autoescape = True)


class Handler(webapp2.RequestHandler):

	def write(self, *a, **kw):
		self.response.write(*a, **kw)

	def render_str(self, template, **params):
		t = jinja_env.get_template(template)
		return t.render(params)

	def render_template(self, template, **params):
		self.write(self.render_str(template, **params))


class MainPage(webapp2.RequestHandler):

    def get(self):
        self.redirect('/login')


class LoginHandler(Handler):

	def get(self):
		self.render_template('login.html')
