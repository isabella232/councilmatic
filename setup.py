#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re
import os
import sys


name = 'councilmatic'
package = 'councilmatic'
description = 'City Council Legislative Subscription Service'
url = 'https://github.com/codeforamerica/councilmatic'
author = 'Mjumbe Wawatu Ukweli'
author_email = 'mjumbewu@gmail.com'
license = 'BSD'
dependency_links = [
    'git+git://github.com/mjumbewu/pysolr.git@056f4e2d#egg=pysolr-3.0.6',
    'git+git://github.com/toastdriven/django-haystack.git@b9c9e47#egg=django-haystack-2.0.0',
    'git+git://github.com/fgregg/legistar-scrape@5f04ebe7#egg=legistar-scrape-0.1',
    'git+git://github.com/abielr/mechanize@813ba36#egg=mechanize-0.2.6',
#    'https://bitbucket.org/ubernostrum/django-registration/get/default.tar.gz#egg=django-registration-dev',
    'git+git://github.com/mjumbewu/django-registration@a22ba5a#egg=django-registration-0.9.1-b1'
]
install_requires = [
# ====================
# Server
# ====================
'Django>=1.5',



# ====================
# Database
# ====================
'South==0.7.4',
'psycopg2==2.4.5',



# ====================
# API
# ====================
'djangorestframework==2.3.5',
'markdown',



# ====================
# Search
# ====================
'django-haystack==2.0.0',

# Using whoosh as the haystack (search) backend for now, for simplicity (it's
# pure Python).  May use pysolr later, but may not need to.
'whoosh==2.3.2',

# Using my version of pysolr until issue # is pulled, as DOTCLOUD's trailing
# slash on SOLR url breaks pysolr.
#pysolr==3.0.4
'pysolr==3.0.6',



# ====================
# Template rendering
# ====================
'django-uni-form',
'django-mustachejs==0.6.0',
'django_compressor==1.1.2',
'slimit==0.7.4',



# ====================
# Registration!
# ====================
'django-registration==0.9.1-b1',



# ====================
# External services
# ====================

# Requests, for talking HTTP to things like Google's geocoder
'requests==2.0.1',

# Scraping
'legistar-scrape==0.1',
'BeautifulSoup',
'BeautifulSoup4',
'pdfminer',
'slate',
'mechanize',


# ====================
# Testing and debugging
# ====================
'django-debug-toolbar==0.9.4',
#pep8
'django-nose==1.0',
'coverage==3.5.1',
'mock==0.8.0',

# Mamangement and deployment
#fabric
]


def get_version(package):
    """
    Return package version as listed in `__version__` in `init.py`.
    """
    init_py = open(os.path.join(package, '__init__.py')).read()
    return re.search("^__version__ = ['\"]([^'\"]+)['\"]", init_py, re.MULTILINE).group(1)


def get_packages(package):
    """
    Return root package and all sub-packages.
    """
    return [dirpath
            for dirpath, dirnames, filenames in os.walk(package)
            if os.path.exists(os.path.join(dirpath, '__init__.py'))]


def get_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)
            if not os.path.exists(os.path.join(dirpath, '__init__.py'))]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return {package: filepaths}


if sys.argv[-1] == 'publish':
    os.system("python setup.py sdist upload")
    args = {'version': get_version(package)}
    print "You probably want to also tag the version now:"
    print "  git tag -a %(version)s -m 'version %(version)s'" % args
    print "  git push --tags"
    sys.exit()


setup(
    name=name,
    version=get_version(package),
    url=url,
    license=license,
    description=description,
    author=author,
    author_email=author_email,
    packages=get_packages(package),
    package_data=get_package_data(package),
    dependency_links=dependency_links,
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.6",
        "Programming Language :: Python :: 2.7",
        "Framework :: Django",
    ],
)
