"""
"""

from werkzeug.serving import run_simple

from pblog.factory import create_app


application = create_app()


if __name__ == '__main__':
    run_simple('localhost', 8000, application, use_reloader=True, use_debugger=True)
