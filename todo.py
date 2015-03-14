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


class TodoHandler(ParentHandler):

	def write_todo_page(self,
						function = "main",
						error = ""):
		"""
		Writes the dashboard page. Either for editing or adding.
		edit_no: Int or None
		"""
		group_users = User.get_group_users()
		todo_list = TodoList.get_todo_list(self.logged_in_user)
		if not todo_list:
			function = "edit"
		self.render_template("todo-" + function + ".html",
							 now = date_string(timezone_now()),
							 user = self.logged_in_user,
							 group_users = group_users,
							 function = function,
							 todo_list = todo_list,
							 error = error)

	def get(self, edit):
		if self.logged_in_user:
			if not edit:
				self.write_todo_page()
			else:
				self.write_todo_page(function = "edit")

	def post(self, edit):
		if self.request.get('add_content'):
			todo_content = self.request.get('todo_content')
			if todo_content:
				todo_list = TodoList.get_todo_list(self.logged_in_user)
				if todo_list:
					todo_list.update(todo_content)
				else:
					todo_list = TodoList.construct(self.logged_in_user,
												   todo_content)
				todo_list.put()
				todo_list.set_todo_list_cache()
				self.redirect('/todo')
			else:
				self.write_todo_page(function = "edit",
									 error = "Content Required!!")
		else:
			self.redirect('/')
