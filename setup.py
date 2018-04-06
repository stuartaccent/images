#!/usr/bin/env python

from setuptools import setup

from codecs import open
from os import path
from images import __version__


install_requires = [
    'Django>=2,<2.1',
    'Pillow>=5,<6',
    'Willow>=1,<2'
]

here = path.abspath(path.dirname(__file__))

with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='images',
    version=__version__,
    description='Images App',
    long_description=long_description,
    author='Stuart George',
    author_email='stuart@accentdesign.co.uk',
    url='https://github.com/stuartgeorge/images/',
    download_url='https://github.com/stuartgeorge/images/',
    license='MIT',
    packages=[
        'images'
    ],
    install_requires=install_requires,
    include_package_data=True,
    keywords=['django', 'images', 'application', 'library'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django',
        'Framework :: Django :: 2.0',
        'Topic :: Internet :: WWW/HTTP :: Site Management',
    ],
)
