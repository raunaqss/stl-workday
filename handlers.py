import datetime
import jinja2
import logging
import os
import string
import webapp2

from utils import *
from dbmodels import *

from google.appengine.ext import db
from google.appengine.api import memcache


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


class ParentHandler(Handler):

	def set_secure_cookie(self, cookie_name, val):
		'''
		Takes the name and val of the cookie.
		Makes the secure value of the cookie by using the val in the input.
		Sets the Cookie with the name provided and the secure cookie value.

		cookie_name: String
		nal = String
		'''
		cookie_val = make_secure_val(val)
		self.response.headers.add_header('Set-Cookie',
			"%s=%s; Path=/" % (cookie_name, cookie_val))

	def read_secure_cookie(self, cookie_name):
		'''
		Returns the Value of the cookie (without the hash) if the cookie value
		is valid.

		Name: String
		'''
		browser_cookie = self.request.cookies.get(cookie_name)
		#logging.info('browser cookie is %s' % browser_cookie)
		return browser_cookie and check_secure_val(browser_cookie)

	def login(self, user):
		'''
		Uses the funciton set_secure_cookie() to set the secure cookie value in
		order to login the user.

		user: User entity
		'''
		self.set_secure_cookie('user_id', str(user.key().id()))

	def logout(self):
		'''Sets the cookie to blank'''
		self.response.headers.add_header('Set-Cookie', 'user_id=; Path=/')

	def initialize(self, *a, **kw):
		'''
		Overrides webapp2's initialize function. This function is run with
		every request.
		This function calls webapp2's initialize function to maintain important
		functionality.

		It reads secure val of the cookie: 
		if it exists: 
			it sets the corresponding user to the variable self.logged_in_user.
		'''
		webapp2.RequestHandler.initialize(self, *a, **kw)
		uid = self.read_secure_cookie('user_id')
		#logging.info('uid is %s' % uid)
		self.logged_in_user = uid and User.get_user(uid)


class MainPage(ParentHandler):

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
		if not self.logged_in_user:
			self.write_login_form()
		else:
			self.write('Welcome, ' + self.logged_in_user.username + '!')

	def post(self):
		signin = self.request.get('signin')
		signup = self.request.get('signup')
		logging.error('signin = ' + signin)
		logging.error('signup = ' + signup)
		if signin:
			username_or_email = self.request.get('username_or_email')
			password = self.request.get('password')
			user = User.valid_login(username_or_email, password)
			if user:
				self.login(user)
				self.redirect('/')
			else:
				self.redirect('/login')
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
			else:
				existing_user = User.get_user(email)
				taken_username = User.get_user(username)
				if existing_user or taken_username:
					if existing_user:
						all_errors[
						'email_error'
						] = "This email has already been registered."
					if taken_username:
						all_errors[
						'username_error'
						] = "This username is already taken."
					self.write_login_form(email = email,
										  username = username,
										  fullname = fullname,
										  all_errors = all_errors)
				else:
					new_user = User.register(username,
											 email,
											 fullname,
											 password,
											 profile_picture)
					new_user.put()
					new_user.set_user_caches()
					self.login(new_user)
					self.redirect('/')


class LoginHandler(ParentHandler):

	def get(self):
		self.write('Okay, thank god.')
