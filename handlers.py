import datetime
import jinja2
import logging
import os
import string
import webapp2

from utils import *
from dbmodels import *

from google.appengine.ext import db
from google.appengine.api import images
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

	def write_dashboard(self,
						function = "main",
						error = "",
						edit_no = None):
		"""
		Writes the dashboard page. Either for editing or adding.
		edit_no: Int or None
		"""
		group_users = User.get_group_users()
		edit_task_content = ""
		done_list = DoneList.todays_done_list(self.logged_in_user.username)
		if type(edit_no) is int: # since 0 is equivalent to None
			edit_task_content = done_list.tasks[edit_no]
			# logging.error('edit_task_content = ' + edit_task_content)
		self.render_template("dashboard-" + function + ".html",
							 now = date_string(timezone_now()),
							 user = self.logged_in_user,
							 group_users = group_users,
							 done_list = done_list,
							 edit_no = edit_no,
							 edit_task_content = edit_task_content,
							 error = error)

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
							 title = "Spacecom Workday",
							 email = email,
							 username = username,
							 fullname = fullname,
							 all_errors = all_errors)


class MainPage(ParentHandler):

	def get(self):
		if not self.logged_in_user:
			self.write_login_form()
		else:
			self.write_dashboard()

	def post(self):
		if self.logged_in_user:
			add_task = self.request.get('add_task')
			if add_task == "Add":
				done_task = self.request.get('done_task')
				if done_task:
					done_list = DoneList.todays_done_list(
						self.logged_in_user.username)
					if done_list:
						done_list = done_list.update(done_task)
						done_list.put()
					else:
						done_list = DoneList.construct(self.logged_in_user,
													   done_task)
						done_list.put()
					done_list.set_done_list_cache()
					self.redirect('/')
				else:
					error = "Task Required!"
					self.write_dashboard(error = error)
		else:
			sel.redirect('/') # to handle case of cookie deletion


class LoginHandler(ParentHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		signin = self.request.get('signin')
		if signin == "Sign In":
			username_or_email = self.request.get('username_or_email')
			password = self.request.get('password')
			user = User.valid_login(username_or_email, password)
			if user:
				self.login(user)
				self.redirect('/')
			else:
				self.redirect('/') # this is temporary


class SignupHandler(ParentHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		signup = self.request.get('signup')
		if signup == "Sign Up":
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
					try:
						new_user.put()
					except Exception as e:
						logging.error(e)
						all_errors[
						'profile_picture_error'
						] = ("Image should be less 1MB. Sorry!")
						self.write_login_form(email = email,
										  	  username = username,
										  	  fullname = fullname,
										  	  all_errors = all_errors)
					else:
						new_user.set_user_caches()
						memcache.delete('Spacecom') # del obsolete group cache
						self.login(new_user)
						self.redirect('/')


class SignoutHandler(ParentHandler):

	def get(self):
		self.redirect('/')

	def post(self):
		signout = self.request.get('signout')
		if signout == 'Sign Out':
			self.logout()
			self.redirect('/')


class EditHandler(ParentHandler):

	def get(self):
		task_index = self.request.get('task')
		self.write_dashboard("edit",
							 "",
							 int(task_index))

	def post(self):
		if self.logged_in_user:
			edit_task = self.request.get('edit_task')
			delete_task = self.request.get('delete_task')
			# logging.error('edit_task = ' + edit_task)
			# logging.error('delete_task = ' + delete_task)
			done_list = DoneList.todays_done_list(self.logged_in_user.username)
			if edit_task:
				done_task = self.request.get('done_task')
				if done_task:
					done_list = done_list.edit(int(edit_task), done_task)
					done_list.put()
					done_list.set_done_list_cache()
					self.redirect('/')
				else:
					error = "Task Required!"
					self.write_dashboard("edit",
										 error,
										 int(edit_task))
			elif delete_task:
				done_list = done_list.del_task(int(delete_task))
				done_list.put()
				done_list.set_done_list_cache()
				self.redirect('/')
		else:
			self.redirect('/')
		

class ImageHandler(ParentHandler):

	def get(self):
		img_id = self.request.get('img_id')
		user = db.get(img_id)
		dimensions = self.request.get('dimensions')
		width, height = dimensions and [int(x) for x in dimensions.split('x')]
		if user:
			logging.error(images.Image(user.profile_picture).width)
			img = user.profile_picture
			if not is_img_square(img):
				img_square = memcache.get(img_id) # because crop slows loading
				if not img_square:
					ratios = img_square_ratios(img)
					img = images.crop(img,
									  ratios[0],
									  ratios[1],
									  ratios[2],
									  ratios[3])
					try:
						set_cache(img_id, img) # because crop slows loading
					except:
						pass
				else:
					img = img_square
			avatar = images.resize(img, width, height)
			self.response.headers['Content-Type'] = 'image/png'
			self.write(avatar)
		else:
			self.write('No image')