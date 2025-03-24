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
    version="1.0.0",
    author="Boolforge",
    author_email="info@boolforge.com",
    description="A comprehensive browser profile migration and management tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/boolforge/floorper",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
    },
    entry_points={
        "console_scripts": [
            "floorper=floorper.__main__:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
