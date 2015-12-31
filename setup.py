#!/usr/bin/env python
# -*- coding: utf-8 -*-


try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup


with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'rq', 'flask', 'redis', 'pymongo'
]

test_requirements = [
    # TODO: put package test requirements here
]

setup(
    name='smoothie',
    version='0.1.0',
    description="Wireless smoothie. Simple and usable web interface for common wireless attacks",
    long_description=readme + '\n\n' + history,
    author="David Francos Cuartero",
    author_email='me@davidfrancos.net',
    url='https://github.com/XayOn/smoothie',
    packages=[
        'smoothie',
    ],
    package_dir={'smoothie':
                 'smoothie'},
    include_package_data=True,
    install_requires=requirements,
    license="ISCL",
    entry_points={
        'console_scripts': [
            'smoothie=smoothie.smoothie:main',
        ],
    },
    zip_safe=False,
    keywords='smoothie',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: ISC License (ISCL)',
        'Natural Language :: English',
        "Programming Language :: Python :: 2",
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    test_suite='tests',
    tests_require=test_requirements
)
