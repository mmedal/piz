from setuptools import setup


with open("README.rst", "rb") as f:
    long_description = f.read().decode("utf-8")


setup(
    name="piz",
    packages=["piz"],
    entry_points={
        "console_scripts": ['piz = piz.piz:main']
    },
    version='v0.1',
    description="Get that track you want.",
    long_description=long_description,
    author="Matthew Medal",
    author_email="matt.medal@gmail.com",
    url="https://github.com/mmedal/piz",
)
