#!/usr/bin/env python

from setuptools import setup

setup(
    name='plwn_graph_builder',
    version='1.0',
    description='PLWN Graph Builder',
    author="Łukasz Kopociński",
    author_email="lkopocinski@gmail.com",
    packages=[
        'plwn_graph_builder',
        'plwn_graph_builder.vertices'
    ],
    license='',
    entry_points={
        'console_scripts': [
            'plwn_graph_builder=plwn_graph_builder.main:main'
        ]
    },
    python_requires='>=3.6',
)
