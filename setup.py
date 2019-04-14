# coding=utf-8

from setuptools import setup, find_packages

setup(
    name='hermit',
    version='0.0.1',
    packages=find_packages(exclude=['docs', 'tests*']),
    include_package_data=True,

    install_requires=[
        'click==7.0',
        'aiogram==2.0.1',
        'rivescript==1.14.9',
    ],

    entry_points='''
        [console_scripts]
        hermit=hermit.cli:main
        h=hermit.cli:hermit
        hs=hermit.cli:hermit_show
    ''',
)
