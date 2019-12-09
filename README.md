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

Alternatively you can install using pip as package. While in the root dir:
```
$ pip install -e .
...
$ SAUCE_USERNAME=<username> SAUCE_ACCESS_KEY=<access-key> copyshop <sauce-labs-test-report-url>
```

Feature Support
---------------

### Desktop Web

- [x] us-west-1 Datacenter
- [ ] us-east-1 Datacenter
- [x] eu-central-1 Datacenter

- [x] Capabilities
- [x] Change URL
- [x] Find Element By XPath
- [x] Find Element By name
- [x] Click on element
- [x] Clear Element
- [x] Send Value to Element
- [x] Implicit Timeouts

### Simulators/Emulators Web

Not tested yet.

### Real Devices

- [x] eu1.appium.testobject.com

- [x] Capabilities
- [x] Find Element By accessiblity ID
- [x] Click on element
- [x] Change context
