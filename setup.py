#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Floorper - Setup Script
=====================

Setup script for installing Floorper.
"""

import os
from setuptools import setup, find_packages

# Read the long description from README.md
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Define package requirements
requirements = [
    "PyQt6>=6.0.0",
    "textual>=0.10.0",
    "rich>=10.0.0",
    "requests>=2.25.0",
    "pyyaml>=5.4.0",
    "cryptography>=3.4.0",
]

# Define development requirements
dev_requirements = [
    "pytest>=6.0.0",
    "black>=21.5b2",
    "isort>=5.9.0",
    "flake8>=3.9.0",
    "mypy>=0.812",
]

setup(
    name="floorper",
    version="0.1.0",
    description="A browser profile migration tool",
    author="Floorper Team",
    author_email="info@floorper.com",
    url="https://github.com/floorper/floorper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "rich>=12.0.0",
        "textual>=0.10.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.10.0",
            "flake8>=6.0.0",
            "black>=23.3.0",
            "mypy>=1.3.0",
            "isort>=5.12.0",
            "tox>=4.6.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "floorper=floorper.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
