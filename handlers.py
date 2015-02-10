import datetime
import jinja2
import logging
import os
import webapp2

from utils import *

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


class MainPage(Handler):

	def write_login_form(self, email = "",
							   username = "",
							   fullname = "",
							   all_errors  = {"username_error": "",
				   							  "password_error": "",
				   							  "signup_error": "",
				   							  "email_error": "",
				   							  "fullname_error": "",
				     						  "profile_picture_error": ""}):

		self.render_template('login.html', 
							 email = email,
							 username = username,
							 fullname = fullname,
							 all_errors = all_errors)

	def get(self):
		self.write_login_form()

	def post(self):
		signin = self.request.get('signin')
		signup = self.request.get('signup')
		logging.error('signin = ' + signin)
		logging.error('signup = ' + signup)
		if signin:
			self.write_login_form()
		elif signup:
			username = self.request.get('username')
			email = self.request.get('email')
			fullname = self.request.get('fullname')
			password = self.request.get('password')
			profile_picture = self.request.get('profile_picture')
			valid_entries, all_errors = validate_signup(username,
														email,
														fullname,
														password,
														profile_picture)
			if not valid_entries:
				self.write_login_form(email = email,
									  username = username,
									  fullname = fullname,
									  all_errors = all_errors)


class LoginHandler(Handler):

	def get(self):
		self.redirect('/')
