from google.appengine.ext import db
from google.appengine.api import memcache
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
	company = db.StringProperty(default = DEFAULT_COMPANY)
	timezone = db.StringProperty(default = DEFAULT_TIMEZONE)
	date_created = db.DateTimeProperty(auto_now_add = True)
