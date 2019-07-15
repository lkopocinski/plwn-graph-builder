#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='PLWNGraphBuilder',
    version='0.1.0',
    description='PLWN Graph Builder',
    author="Marlena Orlińska",
    author_email="Marlena.Orlinska@pwr.edu.pl",
    packages=[
        'PLWNGraphBuilder',
        'PLWNGraphBuilder.vertices'
    ],
    license='',
    entry_points={
        'console_scripts': [
            'PLWNGraphBuilder = PLWNGraphBuilder.main:main'
        ]
    },
    install_requires=[
        'future',
        'configargparse',
    ]
)
