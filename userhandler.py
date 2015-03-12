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

	def get(self, username, date_key):
		if self.logged_in_user:
			user_done_list = DoneList.get_done_list(done_list_key(username,
																  date_key))
			self.render_template('profile.html',
				title = username,
				user = self.logged_in_user,
				this_user = User.get_user(username),
				user_done_list = user_done_list)