#  settings.py - threadreader app settings
#
# Copyright (c) John Wainwright 2014 - All rights reserved.
#
__author__ = 'johnw'

import os, logging

APP = dict(
    port=9001,
    settings=dict(
        template_path=os.path.join(os.path.dirname(__file__), "templates"),
        static_path=os.path.join(os.path.dirname(__file__), "static"),
        twitter_consumer_key = 'jHkeUDDo4iOy3EE0pUtJgTu1z',
        twitter_consumer_secret = 'qIAIWQmO0ij7mAhm2QEfVRol9SfPbn8X86jlW2Jdd7qIggkBhA',
        cookie_secret = "__TODO:_GENERATE_YOUR_OWN_RANDOM_VALUE_HERE__",
        login_url = "/login",
        debug = True,
        serve_traceback = True,
        xsrf_cookies = True,
    )
)

LOGS = dict(
    LOG_ROOT = os.environ.get('THREADREADER_LOG_ROOT', '/var/log/threadreader'),
    LOGGING = {
        'version': 1,
        'disable_existing_loggers': False,
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse'
            }
        },
        'handlers': {
            'mail_admins': {
                'level': 'ERROR',
                'filters': ['require_debug_false'],
                'class': 'django.utils.log.AdminEmailHandler'
            },
            'null': {
                'level': 'DEBUG',
                'class':'django.utils.log.NullHandler',
            },

        },
        'loggers': {
            'django.request': {
                'handlers': ['mail_admins'],
                'level': 'ERROR',
                'propagate': True,
            },
        }
    },
    LOG_LEVEL = logging.DEBUG,
    LOG_FORMAT = '%(asctime)s %(process)d %(filename)s(%(lineno)d): %(levelname)s %(message)s',
)
