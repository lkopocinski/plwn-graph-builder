#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup

setup(
    name='PLWNGraphBuilder',
    version='1.0.0',
    description='PLWN Graph Builder',
    author="Łukasz Kopociński",
    author_email="lkopocinski@gmail.com",
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
