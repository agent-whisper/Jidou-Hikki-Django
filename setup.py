# -*- coding: utf-8 -*-

# DO NOT EDIT THIS FILE!
# This file has been autogenerated by dephell <3
# https://github.com/dephell/dephell

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

readme = ''

setup(
    long_description=readme,
    name='jidou_hikki',
    version='0.1.0',
    python_requires='==3.*,>=3.8.0',
    author='fariz.tumbuan',
    author_email='fariz.tumbuan@gmail.com',
    license='MIT',
    packages=[
        'src', 'src.apps.jidou_hikki',
        'src.apps.jidou_hikki.migrations',
        'src.apps.jidou_hikki.models',
        'src.apps.jidou_hikki.tokenizer',
        'src.apps.jidou_hikki.utils'
    ],
    package_dir={"": "."},
    package_data={
        "src.apps.jidou_hikki": ["templates/jidou_hikki/*.html"]
    },
    install_requires=[
        'django==3.*,>=3.2.4', 'django-model-utils==4.*,>=4.1.1',
        'gunicorn==20.*,>=20.1.0', 'jaconv==0.*,>=0.3.0',
        'jamdict==0.*,>=0.1.0.a11', 'jamdict-data==1.*,>=1.5.0',
        'sudachidict-full[production]==20210608.*,>=20210608.0.0',
        'sudachipy==0.*,>=0.5.2'
    ],
)
