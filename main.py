#!/usr/bin/env python


import webapp2
from handlers import *


application = webapp2.WSGIApplication([
    ('/', MainPage),
], debug=True)
