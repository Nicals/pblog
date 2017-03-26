import os

from setuptools import setup

project_dir = os.path.dirname(os.path.abspath(__file__))


setup(
    name='pblog',
    version='0.1.dev0',
    description='A markdown driven blog with full CLI interface',
    long_description=open(os.path.join(project_dir, 'README.rst')).read(),
    url='http://github.com/Nicals/pblog',
    author='Nicolas Appriou',
    author_email='nicolas.appriou@gmail.com',
    license='MIT',
    packages=['pblog', 'flask_pblog'],
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Environment :: Console',
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Text Processing :: Markup',
    ],
    keywords='flask blog cli',
    install_requires=[
        'Flask==0.12',
        'Flask-SQLAlchemy==2.1',
        'Flask-DebugToolbar==0.10.1',
        'Markdown==2.6.8',
        'Flask-RESTful==0.3.5',
        'PyYAML==3.12',
        'Cerberus==1.1',
        'marshmallow-sqlalchemy==0.12.1',
        'Flask-Script==2.0.5',
        'markdown-extra==0.2.0',
        'python-slugify==1.2.1',
        'Flask-Migrate==2.0.3',
        'requests==2.13.0',
        'click==6.7',
    ],
)
