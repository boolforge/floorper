from setuptools import setup, find_packages

setup(
    name="floorpizer",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "Pillow>=9.0.0",
        "cairosvg>=2.7.0",
        "psutil>=5.9.0",
        "colorama>=0.4.6",
        "lz4>=4.3.2",
    ],
    entry_points={
        'console_scripts': [
            'floorpizer=floorpizer.floorpizer:main',
        ],
    },
    author="Your Name",
    description="Universal Browser Profile Migration Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/floorpizer",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
) 