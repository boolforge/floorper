from setuptools import setup, find_packages

setup(
    name="floorpizer",
    version="2.0.0",
    packages=find_packages(),
    install_requires=[
        "matplotlib>=3.5.0",
        "pillow>=9.0.0",
        "colorama>=0.4.6",
        "lz4>=4.3.2",
        "cairosvg>=2.7.0",
        "psutil>=5.9.0"
    ],
    entry_points={
        "console_scripts": [
            "floorpizer=floorpizer.__main__:main",
        ],
    },
    author="Your Name",
    description="Floorp Profile Migration Tool",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    license="MIT",
    python_requires=">=3.8",
    include_package_data=True,
)