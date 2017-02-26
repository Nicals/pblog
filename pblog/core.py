"""Flask extensions instances are created in this module.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_restful import Api

db = SQLAlchemy()
api = Api()
