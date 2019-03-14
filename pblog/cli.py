import configparser
import importlib
import logging
import pathlib
import threading
import os

import click

from pblog.client import AuthenticationError, Client, UnexpectedResponse
from pblog.package import build_package, PackageException, PackageValidationError


class Environment:
    def __init__(self, name, url, username, local_app_module=None):
        """
            name (str): name of the environment
            url (str): url to the blog application
            username (str): username to use to authenticate on the remote
                blog
            local_app (str): local app module if available
        """
        self.name = name
        self.url = url
        self.username = username
        self.local_app = None
        self.local_app_thread = None

        if local_app_module is not None:
            module_name, attr_name = local_app_module.rsplit('.', 1)
            app_module = importlib.import_module(module_name)
            self.local_app = getattr(app_module, attr_name)

    def run_local_app(self):
        if self.local_app is None:
            raise ValueError("This environment has no local application")

        # prevent werkzeug log
        werkzeug_logger = logging.getLogger('werkzeug')
        for handler in werkzeug_logger.handlers[:]:
            werkzeug_logger.removeHandler(handler)

        self.local_app_thread = threading.Thread(
            target=self.local_app.run, kwargs={'debug': False})
        self.local_app_thread.start()

    def stop_local_app(self):
        if self.local_app is None:
            raise ValueError("This environment has no local application")

        if self.local_app_thread is None:
            raise ValueError("No thread has been started")

        os.environ['werkzeug.server.shutdown']()
        self.local_app_thread.join()
        self.local_app_thread = None


class EnvError(Exception):
    """Base exception for env parsing
    """


def parse_env(env_file, env=None):
    """Reads a pblog.ini file.

    Args:
        env_file (file object): file-like object
        env (string or None: Environment to use. If None, the default
            environment will be used.

    Raises:
        pblog.cli.EnvException: if some section are not found in the file
        KeyError: if some value are not found

    Returns:
        pblog.cli.Environment: A named tuple with the following attributes:
            + api_root: the URL to Pblog API
            + username: the username to use to connect to Pblog API
    """
    parser = configparser.ConfigParser()
    parser.read_file(env_file)

    if env is None:
        if not parser.has_section('pblog'):
            raise EnvError("pblog section was not found")
        env = parser['pblog']['env']

    env_section = 'pblog:%s' % env
    if not parser.has_section(env_section):
        raise EnvError("Environment %s not defined" % env_section)

    return Environment(
        name=env,
        url=parser[env_section]['url'].rstrip('/'),
        username=parser[env_section]['username'],
        local_app_module=parser[env_section].get('wsgi'))


@click.group()
@click.option('-i', '--ini', default='pblog.ini', help='pblog.ini path')
@click.option('-e', '--env', help='pblog environment')
@click.option('-a', '--app', is_flag=True, help='run local app')
@click.pass_context
def cli(ctx, ini, env, app=False):
    try:
        ini_path = pathlib.Path(ini).resolve()
    except FileNotFoundError:
        raise click.ClickException('%s file not found' % ini)
    if not ini_path.is_file():
        raise click.ClickException('%s is not a file' % ini_path)

    try:
        with ini_path.open() as ini_file:
            env = parse_env(ini_file, env=env)
            ctx.obj['env'] = env
    except KeyError as e:
        raise click.ClickException(
            "no value for {} in ini file".format(e.args[0]))
    except (EnvError, configparser.Error) as e:
        raise click.ClickException(str(e))

    if app is True:
        if env.local_app is None:
            raise click.ClickException(
                "No local application defined for environment '%s'" % env.name)
        env.run_local_app()


@cli.command()
@click.argument('post_path')
@click.option('--encoding', default='utf-8', help='post file encoding')
@click.option('--password', prompt=True, hide_input=True)
@click.pass_context
def publish(ctx, post_path, encoding, password):
    env = ctx.obj['env']
    try:
        post_path = pathlib.Path(post_path).resolve()
    except FileNotFoundError:
        raise click.ClickException('%s file not found' % post_path)
    if not post_path.is_file():
        raise click.ClickException('%s is not a file' % post_path)

    client = Client(api_root=env.url + '/api/')
    try:
        client.authenticate(env.username, password)
    except AuthenticationError:
        raise click.ClickException("authentication failed")
    except UnexpectedResponse as e:
        raise click.ClickException("unexpected server response: %s" % e.received_status)

    # parse post and report errors if any
    package_path = post_path.parent / (post_path.stem + '.tar.gz')
    try:
        package = build_package(post_path, package_path, encoding=encoding)
    except PackageValidationError as e:
        click.echo(str(e), err=True)
        for field, errors in e.errors.items():
            for error in errors:
                click.echo('%s: %s' % (field, error), err=True)
        raise click.ClickException('aborting')
    except PackageException as e:
        raise click.ClickException(str(e))

    try:
        if package.post_id.get(env.name) is None:
            result_post = client.create_post(package_path)
            click.echo('post %s successfully created' % result_post['id'])
        else:
            result_post = client.update_post(package.post_id[env.name], package_path)
            click.echo('post %s successfully updated' % result_post['id'])
    except UnexpectedResponse as e:
        raise click.ClickException("unexpected server response: %s" % e.received_status)

    new_meta = dict(
        post_id={env.name: result_post['id']},
        post_slug=result_post['slug'],
        published_date=result_post['published_date'],
    )
    if package.update_post_meta(**new_meta):
        with post_path.open('wb') as post_file:
            post_file.write(package.markdown_content.encode(encoding))
        click.echo('post metadata updated')

    click.echo('url: {url}/post/{id}/{slug}'.format(
        url=env.url,
        id=result_post['id'],
        slug=result_post['slug']))
