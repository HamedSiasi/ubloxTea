


`for new project start from point (A)`

`for an existing project just comment main() and start from point (B)`

`(A)`

`git clone https://github.com/HamedSiasi/mbed-os-ublox-test`

`cd mbed-os-ublox-test`

`mbed update`

`cd mbed-os`

`mbed update workshop-ublox`

`cd core`

`git checkout master`

`mbed update`

`cd ../..`

`mbed target SARA_NBIOT_EVK`

`mbed toolchain GCC_ARM`


`(B)`

`mbed test -c`

`git clone https://github.com/HamedSiasi/ubloxTea`

`cd saraTest`

`python testSetup.py`

`Y Enter`

`python testRun.py`
