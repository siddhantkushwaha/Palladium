## Palladium

I got tired of having to download install Chrome/Chromium and Chromdrivers whenever I had to deploy/experiment my projects that use Selenium.
This sets up everything automatically for you.
Package also comes with a class called **CustomChrome** which is a wrapper on **Chrome** with some additional functionalities.

[![forthebadge made-with-python](http://ForTheBadge.com/images/badges/made-with-python.svg)](https://www.python.org)

[![MIT license](https://img.shields.io/badge/License-MIT-blue.svg)](https://lbesson.mit-license.org/)

[![PyPI version fury.io](https://badge.fury.io/py/palladium-python.svg)](https://pypi.python.org/pypi/palladium-python)
[![PyPI pyversions](https://img.shields.io/pypi/pyversions/palladium-python.svg)](https://pypi.python.org/pypi/palladium-python)
[![PyPI status](https://img.shields.io/pypi/status/palladium-python.svg)](https://pypi.python.org/pypi/palladium-python)

## How to install

    pip install palladium-python

## How to use
 
    from palladium.chrome_custom import ChromeCustom
    
    driver = ChromeCustom(headless=False)

