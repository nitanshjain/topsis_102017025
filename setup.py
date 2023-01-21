from setuptools import setup, find_packages
import codecs
import os


VERSION = '0.0.1'
DESCRIPTION = 'Topsis Calculation Package'
LONG_DESCRIPTION = 'A package that allows the user to perform Topsis (MCDM) on a dataset'

# Setting up
setup(
    name="Topsis-Nitansh-102017025",
    version=VERSION,
    author="Nitansh Jain",
    author_email="<njain_be20@thapar.edu>",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=LONG_DESCRIPTION,
    packages=find_packages(),
    install_requires=['pandas', 'numpy', 'detect_delimiter', 'scipy', 'sys'],
    keywords=['python', 'topsis', 'mcdm'],
    classifiers=[
        "Development Status :: 1 - Planning",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Operating System :: Unix",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)