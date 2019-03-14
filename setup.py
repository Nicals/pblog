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
        'Flask==1.0.2',
        'Flask-SQLAlchemy==2.3.1',
        'Markdown==3.0.1',
        'Flask-RESTful==0.3.7',
        'PyYAML==5.1',
        'Cerberus==1.1',
        'marshmallow==2.19.0',
        'markdown-extra==1.0.1',
        'python-slugify==1.2.1',
        'requests==2.21.0',
        'click==6.7',
    ],
    extras_require={
        'docs': ['Sphinx', 'sphinxcontrib-programoutput'],
        'tests': ['pytest', 'blinker'],
    },
)
