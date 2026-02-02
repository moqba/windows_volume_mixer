#!/usr/bin/env python

from distutils.core import setup

from setuptools import find_packages

setup(
    name='windows_volume_mixer',
    description='Controls windows applications volume',
    version='0.0.1',
    author="Mohcine Qbaich",
    author_email='randeomcom@gmail.com',
    url='https://github.com/moqba/windows_volume_mixer',
    license='MIT',
    packages=find_packages(include=['windows_volume_mixer', 'windows_volume_mixer.*']),
    install_requires=['pycaw', 'fastapi', 'pydantic', 'uvicorn', 'screeninfo', 'pefile', 'pillow'],
    extras_require={
        'dev': ['pytest',]
    },
    python_requires='>=3.11',
)
