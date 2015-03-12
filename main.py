#!/usr/bin/env python


import webapp2
from handlers import *
from userhandler import *


application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'^/_edit/?$', EditHandler),
    (r'^/img/?$', ImageHandler),
    (r'^/login/?$', LoginHandler),
    (r'^/signup/?$', SignupHandler),
    (r'^/signout/?$', SignoutHandler),
    (r'^/([a-zA-Z][a-zA-Z0-9_-]{3,20})/?([0-9-]{10})?/?$', UserHandler)
], debug=True)
