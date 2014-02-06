FxOS Powertool!
===============

The FxOS Powertool! is intended for FxOS developers to use when optimizing software for power consumption.  It is also handy for verifying and fixing power consumption bugs.

Prerequisites
-------------

This tool requires that you have a USB ammeter device like the [Yoctopuce USB ammeter](http://www.yoctopuce.com/EN/products/usb-sensors/yocto-amp) or build your own using the [Mozilla ammeter design](http://wiki.mozilla.org).

You will also need a battery harness for your FxOS device.  The battery harnesses are open source hardware that consist of a 3D printed piece, and a small circuit board.  You can find all of the data files for the currently supported FxOS devices below:

* [Alcatel OneTouch Battery Harness](http://missing.link)
* [Samsung Nexus S Battery Harness](http://missing.link)
* [LG Nexus 4 Battery Harnes](http://missing.link)

Quick Start
-----------

The first step is to clone this repo:

```sh
$ git clone git://github.com/JonHylands/fxos-powertool
```

Then isntall the application and dependencies:

```sh
$ cd fxos-powertool
$ sudo python ./setup.py install
```

Write your test suite description file.  There is an example in the examples folder.  It is a JSON file that looks like this:

```json
{
    "title": "My Tests",
    "tests": [
        "My first test",
        "My second test",
        "My third test"
    ]
}
```

Plug in your ammeter device, and hook it up to the battery harness for your device.  Then launch the powertool to begin testing.
