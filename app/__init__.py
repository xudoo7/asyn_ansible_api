# -*- coding: utf-8 -*-
from __future__ import print_function, unicode_literals, absolute_import

from flask import Flask
from flask_restful import Api
from celery import Celery
from config import BaseConfig, config
from logconfig import init_logging

celery = Celery(__name__, broker=BaseConfig.CELERY_BROKER_URL, backend=BaseConfig.CELERY_RESULT_BACKEND)


def create_app(config_name):
    app = Flask(__name__)
    api = Api(app)
    app.config.from_object(config[config_name])
#    app.config['CELERY_BROKER_URL'] = 'amqp://myuser:mypassword@192.168.56.101:5672/myvhost'
#    app.config['CELERY_RESULT_BACKEND'] = 'amqp://myuser:mypassword@192.168.56.101:5672/myvhost'
#    celery.conf.update(config[config_name])
    init_logging(app.config['APP_LOG_DIR'])
    celery.conf.update(app.config)
    return app, api
