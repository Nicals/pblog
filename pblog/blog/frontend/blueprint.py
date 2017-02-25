from flask import Blueprint


blueprint = Blueprint('blog', __name__)


@blueprint.route('/')
def home_page():
    return '<!DOCTYPE html><html><head></head><body></body></html>'
