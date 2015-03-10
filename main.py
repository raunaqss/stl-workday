#!/usr/bin/env python


import webapp2
from handlers import *


application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'^/_edit/?$', EditHandler),
    (r'^/img/?$', ImageHandler),
    (r'^/login/?$', LoginHandler),
    (r'^/signup/?$', SignupHandler),
    (r'^/signout/?$', SignoutHandler)
], debug=True)
