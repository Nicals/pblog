"""Flask extensions instances are created in this module.
"""

from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

db = SQLAlchemy()
marshmallow = Marshmallow()
