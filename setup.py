#!/usr/bin/env python3.7

from setuptools import setup, find_packages

setup(
    name='plwn-graph-builder',
    version='1.0',
    description='PLWN graph builder.',
    author='Łukasz Kopociński',
    author_email="lkopocinski@gmail.com",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'plwn-graph-builder=plwn_graph_builder.main:main'
        ]
    },
    python_requires='>=3.7',
)
