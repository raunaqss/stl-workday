#!/usr/bin/env python


import webapp2
from handlers import *
from userhandler import *
from todo import *


# path_parameter_RE = r'^/([a-zA-Z][a-zA-Z0-9_-]{3,20})/?([0-9-]{10})?/?$'

application = webapp2.WSGIApplication([
    ('/', MainPage),
    (r'^/_edit/?$', EditHandler),
    (r'^/img/?$', ImageHandler),
    (r'^/login/?$', LoginHandler),
    (r'^/signup/?$', SignupHandler),
    (r'^/signout/?$', SignoutHandler),
    (r'^/todo/?(_edit)?/?$', TodoHandler),
    (r'^/reset/?([a-zA-Z0-9-_]+)?/?$', ResetHandler),    
    (r'^/verify/?([a-zA-Z0-9-_]+)?/?$', VerifyHandler),
    (r'^/([a-zA-Z][a-zA-Z0-9_-]{3,20})/?$', UserHandler)
], debug=True)
