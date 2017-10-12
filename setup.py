#!/usr/bin/env python
from setuptools import setup, find_packages
from pupa import __version__

long_description = ''

setup(name='pupa',
      version=__version__,
      packages=find_packages(),
      author='James Turk',
      author_email='james@openstates.org',
      license='BSD',
      url='https://github.com/opencivicdata/pupa/',
      description='scraping framework for muncipal data',
      long_description=long_description,
      platforms=['any'],
      zip_safe=False,
      entry_points='''[console_scripts]
pupa = pupa.cli.__main__:main''',
      install_requires=[
          'Django>=1.9.0',
          'opencivicdata',
          'dj_database_url==0.3.0',
          'scrapelib>=1.0',
          'jsonschema==2.6.0',
          'psycopg2',
          'pytz',
      ],
      extras_require={
          'dev': [
            'mock',
            'pytest',
            'pytest-cov',
            'pytest-django',
            'coveralls',
            'flake8',
          ],
      },
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.4",
                   "Programming Language :: Python :: 3.5",
                   "Programming Language :: Python :: 3.6",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
      )
