import datetime
import jinja2
import logging
import os
import string
import webapp2

from utils import *
from dbmodels import *
from handlers import *

from google.appengine.ext import db
from google.appengine.api import images
from google.appengine.api import memcache


class UserHandler(ParentHandler):

	def get(self, username):
		if self.logged_in_user:
			if self.logged_in_user.verified:
				date_key = self.request.get('date')
				if not date_key:
					date_key = date_to_date_key(timezone_now().date())
				user_done_list = DoneList.get_done_list(username, date_key)
				this_user = User.get_user(username)
				user_todo_list = TodoList.get_todo_list(this_user)
				self.render_template('profile.html',
					title = username,
					user = self.logged_in_user,
					this_user = this_user,
					date_key = date_key,
					start_date = date_to_date_key(this_user.date_created),
					end_date = date_to_date_key(timezone_now().date()),
					user_done_list = user_done_list,
					user_todo_list = user_todo_list)
			else:
				self.write_verify_page()
		else:
			self.redirect('/')


class VerifyHandler(ParentHandler):

	def get(self, user_key):
		if self.logged_in_user and not self.logged_in_user.verified:
			if str(self.logged_in_user.key()) == user_key:
				self.logged_in_user.verified = True
				self.logged_in_user.put()
				self.logged_in_user.set_user_caches()
			self.redirect('/')
		else:
			self.redirect('/')

	def post(self, user_key):
		sendmail = self.request.get('sendmail')
		if sendmail == "Yes":
			self.logged_in_user.send_confirmation_mail()
			self.redirect('/')
			