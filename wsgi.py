"""
"""

from werkzeug.serving import run_simple

from pblog.blog import frontend


application = frontend.create_app()


if __name__ == '__main__':
    run_simple('localhost', 8000, application, use_reloader=True, use_debugger=True)
