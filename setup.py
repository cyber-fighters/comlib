import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="comlib",
    version="1.0.0",
    author="Cajus Pollmeier",
    author_email="pollmeier@gonicus.de",
    description="Support package to handle communcation with the backyard supervisor",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.gonicus.de/tuev/comlib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "requests>=2.21.0"
    ],
)
