#  ~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~
#  MIT License
#
#  Copyright (c) 2021 Nathan Juraj Michlo
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#  ~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~=~

import setuptools


# ========================================================================= #
# HELPER                                                                    #
# ========================================================================= #


with open("README.md", "r", encoding="utf-8") as file:
    long_description = file.read()

with open('requirements.txt', 'r') as f:
    install_requires = (req[0] for req in map(lambda x: x.split('#'), f.readlines()))
    install_requires = [req for req in map(str.strip, install_requires) if req]


# ========================================================================= #
# SETUP                                                                     #
# ========================================================================= #


setuptools.setup(
    name="mtgdata-cc",
    author="Christopher Caporale",
    author_email="c.caporale@pm.me",

    version="0.1.0",
    python_requires=">=3.7",  # we make use of standard library features only in 3.8
    packages=setuptools.find_packages(),

    install_requires=install_requires,

    url="https://github.com/ccaporale1/mtgdata-cc",
    description="MTG image dataset with automatic image scraping and conversion.",
    long_description=long_description,
    long_description_content_type="text/markdown",

    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Intended Audience :: Science/Research",
    ],
)


# ========================================================================= #
# END                                                                       #
# ========================================================================= #
