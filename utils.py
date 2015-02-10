import re


USER_RE = re.compile(r"^[a-zA-Z0-9_-]{3,20}$")
PASS_RE = re.compile(r"^.{3,20}$")
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
