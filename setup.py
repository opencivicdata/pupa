#!/usr/bin/env python
from setuptools import setup, find_packages
from pupa import __version__

long_description = ''

setup(name='pupa',
      version=__version__,
      packages=find_packages(),
      author='James Turk',
      author_email='jturk@sunlightfoundation.com',
      license='BSD',
      url='http://github.com/opencivicdata/pupa/',
      description='scraping framework for muncipal data',
      long_description=long_description,
      platforms=['any'],
      entry_points='''[console_scripts]
pupa = pupa.cli.__main__:main''',
      install_requires=[
          #'Django==1.7.0',
          'dj_database_url==0.3.0',
          'django-uuidfield==0.5.0',
          'djorm-pgarray==1.0',
          'jsonfield==0.9.20',
          'scrapelib>=0.8',
          'validictory>=0.9',
          'opencivicdata==0.5.1',
      ],
      classifiers=["Development Status :: 4 - Beta",
                   "Intended Audience :: Developers",
                   "License :: OSI Approved :: BSD License",
                   "Natural Language :: English",
                   "Operating System :: OS Independent",
                   "Programming Language :: Python :: 3.3",
                   "Programming Language :: Python :: 3.4",
                   "Topic :: Software Development :: Libraries :: Python Modules",
                   ],
)
