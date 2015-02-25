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