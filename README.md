# If You Do Not Have An Existing Project

If you do not have an existing mbed project that you want to test, proceed as follows:

`git clone https://github.com/u-blox/mbed-os-ublox-test`

`cd mbed-os-ublox-test`

`mbed update`

`mbed target SARA_NBIOT_EVK`

`mbed toolchain GCC_ARM`

Then continue as below.

# For An Existing Project

If you have an existing project that you want to test, `cd` to it and `#ifdef`-out your existing `main()`, then:

`git clone https://github.com/HamedSiasi/ubloxTea`

`cd ubloxTea/saraTest`

`python testSetup.py`

`Y <enter>`

Then compile the tests with:

`mbed test -c --continue-on-build-fail`

Note: you will always need to specify `-c` as the test case source is copied before being compiled and so timestamps won't work.

Edit `testRun.py` and, near the bottom of the file, change the `COM` port to be the port where your SARA EVK's USB port is connected, then:

`python testRun.py`