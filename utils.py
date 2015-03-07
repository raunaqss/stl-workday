import datetime
import hashlib
import hmac
import logging
import random
import re
import string

from google.appengine.ext import db
from google.appengine.api import memcache
from pytz.gae import pytz
from secret import *


def donelist_permalink(username, date_object):
	return username + '/' + date_object.strftime('%a-%d-%b-%Y')


def make_cache_key(user_id, date_object):
	return str(user_id) + '_' + date_string(date_object)


def date_string(date_object):
	return date_object.strftime('%a %d %b %Y')


def timezone_now(timezone = 'Asia/Kolkata'):
	pytz_timezone = pytz.timezone(timezone)
	return pytz_timezone.normalize(aware_utcnow().astimezone(pytz_timezone))


def aware_utcnow():
	"""Get aware utcnow to store it in the date_createrd property."""
	return datetime.datetime.utcnow().replace(tzinfo = pytz.UTC)


def what_attribute(uid_or_username_or_email):
	"""
	Helper function for master Query function User.get_user().
	It tells the function the attribute the user wants to query.
	"""
	if uid_or_username_or_email.isdigit():
		return 'uid'
	elif valid_email(uid_or_username_or_email):
		return 'email'
	else:
		return 'username'


def set_cache(cache_key, value):
	"""
	Sets memcache using Check & Set.
	It uses only 'set' if the key is uninitialized.
	"""
	client = memcache.Client()
	try:
		while True:
			old_value = client.gets(cache_key)
			assert old_value, 'Uninitialized Key'
			if client.cas(cache_key, value):
				break
	except AssertionError:
		client.add(cache_key, value)
		logging.error('Initializing Key')


def make_salt():
	"""	
	Returns a random 5 letter salt used for hashing the password.
	Helper function for: make_pw_hash()

	Input: NA
	Returns: String
	"""
	return ''.join(random.choice(string.letters) for x in xrange(5))


def make_pw_hash(name, pw, salt = make_salt()):
	"""
	Returns the valid password hash: 'string of password hash','salt'
	The hashed password has a comma , as the separator.

	name: String
	pw: String
	Salt: String

	Returns: String
	"""
	h = hashlib.sha256(name + pw + salt).hexdigest()
	return '%s,%s' % (h, salt)


def valid_pw(name, pw, h):
	"""
	Returns a boolean for whether the given password is valid.

	name: String
	pw: String
	h: String
	Returns: Boolean
	"""
	return h == make_pw_hash(name, pw, h.split(',')[-1])


def hash_str(val):
	"""
	Helper function for make_secure_val(). Hashes the val with the SECRET in
	the global environment.

	val: String
	Returns: String
	"""
	return hmac.new(SECRET, val).hexdigest()


def make_secure_val(val):
	"""
	Makes the hashed cookie for a given val.
	The hashed cookie uses a pipe | as the separator between the value and it's
	hash.

	val: String
	Returns: String
	"""
	return '%(value)s|%(hashed)s' % {'value': val, 'hashed': hash_str(val)}


def check_secure_val(h):
	"""
	Used to validate the hashed cookie when received from the browser in a
	request.
	if valid -> Returns the val of the cookie

	h: String
	Returns: String
	"""
	val = h.split('|')[0]
	if h == make_secure_val(val):
		return val


USER_RE = re.compile(r"^[a-zA-Z][a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{6,20}$")
EMAIL_RE = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")


def valid_username(username):
    return USER_RE.match(username)


def valid_password(password):
    return PASS_RE.match(password)


def valid_email(email):
    return EMAIL_RE.match(email)


def validate_signup(username, email, fullname, password, profile_picture):
	all_errors  = {"username_error": "",
				   "password_error": "",
				   "signup_error": "",
				   "email_error": "",
				   "fullname_error": "",
				   "profile_picture_error": ""}
	valid_entries = True
	if not valid_username(username):
		all_errors["username_error"] = "That's not a valid username."
		valid_entries = False
	if not valid_password(password):
		all_errors["password_error"] = "That wasn't a valid password."
		valid_entries = False
	if not valid_email(email):
		all_errors["email_error"] = "That's not a valid email."
		valid_entries = False
	if not fullname:
		all_errors["fullname_error"] = "Please enter your full name."
	if not profile_picture:
		all_errors[
		"profile_picture_error"
		] = "Please upload a Profile Picture."
		valid_entries = False
	if valid_entries:
		if not "@spacecom.in" in email:
			all_errors[
				"signup_error"
				] = "You are not authorized to sign up."
			valid_entries = False
	return valid_entries, all_errors
