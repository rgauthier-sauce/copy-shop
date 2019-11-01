CopyShop
=========

`copyshop` is a tool for the Sauce Labs support teams.
It simply takes a test report URL and outputs a Java test script with the same capabilities as the original test.

Usage
-----

```
$ pip install -r requirements.txt
...
$ SAUCE_USERNAME=<username> SAUCE_ACCESS_KEY=<access-key> python3 copyshop.py <sauce-labs-test-report-url>
```
