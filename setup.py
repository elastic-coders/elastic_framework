#!/usr/bin/env python

from setuptools import setup, find_packages

install_requires = ["Django==1.6.1", "djangorestframework==3.0.0",
                    "requests==2.5.0"]

import sys

setup(
    name='elastic_framework',
    version='0.0.4',
    description='A python/django framework to increase your productivity',
    author='Elastic Coders - Davide Scatto',
    author_email='davidescatto@elastic-coders.com',
    url='https://github.com/elastic-coders/elastic_framework.git',
    packages=find_packages(),
    install_requires=install_requires,
    zip_safe=True,
)
