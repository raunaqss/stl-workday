import datetime
import logging
import string

from google.appengine.ext import db
from google.appengine.api import memcache
from pytz.gae import pytz
from utils import *


# Since app is open to only spacecom.in emails as of now
DEFAULT_COMPANY = 'Spacecom Software LLP'
DEFAULT_TIMEZONE = 'Asia/Kolkata'


def users_key(group = 'default'):
	return db.Key.from_path('users', group)


class User(db.Model):
	"""Datastore entity for each user."""

	username = db.StringProperty()
	email = db.EmailProperty()
	fullname = db.StringProperty()
	pw_hash = db.StringProperty()
	profile_picture = db.BlobProperty()
	company = db.StringProperty(default = DEFAULT_COMPANY)
	timezone = db.StringProperty(default = DEFAULT_TIMEZONE)
	date_created = db.DateTimeProperty()

	@classmethod
	def get_user(cls, uid_or_username_or_email):
		"""
		uid_or_username: String
		Returns User

		Attempts memcache get first.
		If memcache get is not successful -> Calls the appropriate DB Query
		funciton (And sets to memcache.)
		"""
		user = memcache.get(uid_or_username_or_email)
		if not user:
			attribute = what_attribute(uid_or_username_or_email)
			if attribute == 'uid':
				user = cls.by_id(uid_or_username_or_email)
			elif attribute == 'email':
				user = cls.by_email(uid_or_username_or_email)
			elif attribute == 'username':
				user = cls.by_username(uid_or_username_or_email)

			if user:
				user.set_user_caches()
		return user

	@classmethod
	def by_id(cls, uid):
		'''
		Returns the user with the id uid.

		uid: String
		Returns: User entity
		'''
		logging.error('DB QUERY')
		return cls.get_by_id(long(uid), parent = users_key())

	@classmethod
	def by_username(cls, username):
		'''
		Returns the user with the given username.

		username: String
		Returns: User entity
		'''
		logging.error('DB QUERY')
		user = cls.all().ancestor(users_key()).filter("username = ",
													  username).get()
		return user

	@classmethod
	def by_email(cls, email):
		"""
		Returns the user with the given email.
		email: String (from EmailProperty)
		"""
		logging.error('DB QUERY')
		user = cls.all().ancestor(users_key()).filter("email = ",
													 email).get()
		return user


	@classmethod
	def register(cls, username, email, fullname, pw, profile_picture):
		'''
		Hashes the given password (pw).
		Constructs a User entity for the given information.
		Returns the construted User entity.

		name: String
		pw: String
		email: String (optional)

		Returns: User entity
		'''
		pw_hash = make_pw_hash(username, pw)
		return cls(parent = users_key(),
					username = username,
					email = email,
					fullname = fullname,
					pw_hash = pw_hash,
					profile_picture = profile_picture,
					date_created = aware_utcnow())

	@classmethod
	def valid_login(cls, username_or_email, pw):
		'''
		if user exits and if login is valid: Returns User

		name: String
		pw: String

		Returns: User entity
		'''
		user = cls.get_user(username_or_email)
		if user and valid_pw(user.username, pw, user.pw_hash):
			return user

	def set_user_caches(self):
		set_cache(self.username, self)
		set_cache(str(self.key().id()), self)
		set_cache(self.email, self)


class DoneList(db.Model):
	"""Datastore entity for each item in the Done List."""

	tasks = db.ListProperty(db.Text)
	user_id = db.IntegerProperty()
	tz_date = db.DateProperty()
	company = db.StringProperty(default = DEFAULT_COMPANY)

	@classmethod
	def get_done_list(cls, user, tz_date):
		"""
		This decorator will first check the cache.
		If not found in cache, call DB query and set the cache.
		"""
		done_list = memcache.get(make_cache_key(user.key().id(), tz_date))
		if not done_list:
			done_list = cls.by_user_n_date(user, tz_date)
		return done_list

	@classmethod
	def by_user_n_date(cls, user, tz_date):
		"""This decorator is a DB Query."""
		done_task = cls.all().ancestor(user)
		done_task.filter("user_id = ", user.key().id())
		done_task.filter("tz_date = ", tz_date)

		return done_task.get()

	@classmethod
	def construct(cls, task, user):
		"""Constructs the DoneList and returns it without putting it."""
		return cls(parent = user,
				   tasks = [db.Text(task)],
				   user_id = user.key().id(),
				   tz_date = timezone_now().date())

	def update(self, task):
		"""Updates itself with the given task without putting it to the db."""
		self.tasks.append(db.Text(task))
		return self

	def set_done_list_cache(self):
		set_cache(make_cache_key(self.user_id, self.tz_date), self)
