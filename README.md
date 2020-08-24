# RPi-P2D2-Support
![Project Maintenance][maintenance-shield]

[![GitHub Activity][commits-shield]][commits]

[![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)

Useful information for using P2D2 (parallax Propeller V2) with Raspberry Pi.

I'm continually adding to this document as I "Learn things."

As you likely already know **Peter Jakacki's** P2D2 Boards are arriving with a 3rd header, matching the Raspberry Pi GPIO pinout, outboard of the two P2D2 headers already present. This allows the P2D2 to be plugged into the Raspbery Pi just like many other RPi Hats.

The P2D2 Plugs into the RPi GPIO Header and provides the following connections:

## The Hardware 

### Pins that are connected to the RPi

By plugging the P2D2 onto the RPi header the board is immediately connected to a number of useful interfaces and a new world of opportunity.

|  RPi Interface | # of Pins | Purpose | P2 Pins |
| ---------- | -------------- | -------------------- | ---- |
| I2C(1) | 2 pins | SDA, SCL | P0, P2 |
| 1-wire | 1 pin | 1-wire | P4 |
| UART(0) | 2 pins | TxD, RxD| P1, P3 |
| PCM | 1 pin? | PCM CLK | P5 |
| SPI(0) | 5 pins | MOSI, MISO, SCLK, !CE0, !CE1 | P12-P16 |
| I2C ID | 2 Pins | ID_SC, ID_SD  | P17, P20 |
| GPIOs | 15 pins | Unclaimed I/O | P6-P11, P19, P21-P26, P28, P30 | 

### Diagram of connections to RPi

Here is the header as shown in Peter's P2D2 r5 documents:

![Pinout](Images/RPi-Header.png)


## The Raspberry Pi (RPi)

Raspberry Pi's are fairly inexpensive devices and all software for them, operating system, applications are free.  RPi's such at the RPi4 with its 8GB ram is touted to be a nearly desktop class linux machine. It is well connected, offering WiFi, wired ethernet, and bluetooth interfaces, USB 2.0 and 3.0. It has wonderfully high resolution (up to 4k 60fps) HDMI output and it has world class open source data analysis and visualization tools available at no cost (open source.)

-

# Hardware Interaction leading to configuration Choices


## Interface: I2C0

## Interface: 1-Wire

## Interface: Serial: UART0
There are two hardware UARTs: miniUART and PL011 that are configured to be primary and secondary [^1] and four additional UARTs [2-5] [^2].

### MiniUART (less capable, but fully meets our normal debugging needs)

The **miniUART** is configured to be the primary and is by default routed to UART0 (at the GPIO connector), it is disabled but is configured, when enabled, to be a serial console with full command line access. The clock for this miniUART is derived from the CPU clock so it can be affected by temperature throttleing or overclocking.  (It appears on device files: /dev/serial0, /dev/ttyS0)

Considerations for use: 

* This MiniUART is easily capable of our P2 deafult 2MBit 8N1 configuration (it can go higher)
* We need to fix the cpu clock fequency so it can not cause our miniUART to change frequencies while we are using it.
* We need to set the input clock frequency to the miniUART to get to our 2Mbit rate

### PL011 UART (more capable)
The second and more capable UART is the **PL011 UART**. This is configured to be the Bluetooth LE serial transceiver and is the secondary serial device. (It appears on device files: /dev/serial01, /dev/ttyAMA0)

Considerations for use: 

* If we want to use this UART as UART0 then we need to flip the miniUART to handle the Bluetooth LE device and PL011 to be the primary connecting it to UART0 at our GPIO header.  Alternatively, we can just disable the bluetooth to cause this to happen as well.

### Serial Boot-time Configuration

Two files are involved in configuration of serial port use: /boot/config.txt and /boot/cmdline.txt

As an RPi user it is probably cleaner to make as much configuration change as you can using 'sudo raspi-config' utility. With this utility you can enable the primary serial port (disabled by default) and you can disable the serial console use of the primary serial port.

You will need to fix clock frequency (and/or configure which UARTs do what) by modifying the files directly. You can modify these files by hand using 'vi' or 'nano' as your editor but this is slightly  more error prone so we want to be very deliberate here. (You don't want typo's or mis-spellings in these files as stuff just doesn't work right where there are...)

## Interface: SPI0

## Interface: I2C SD/SC (Hat ID ROM)


[^1]: Raspberry Pi Doumentation: [UARTs](https://www.raspberrypi.org/documentation/configuration/uart.md)

[^2]: Raspberry Pi Doumentation - UART configuration overlays. Scroll down to: [UARTs and Device Tree](https://www.raspberrypi.org/documentation/configuration/uart.md)

[^3]: SoC Peripheral Doument: [BCM2835 Ref](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2835/BCM2835-ARM-Peripherals.pdf)

## Credits

...TBD...

----

## Disclaimer and Legal

> *Raspberry Pi* is registered trademark of *Raspberry Pi (Trading) Ltd.*
>
> *Parallax, Propeller Spin, and the Parallax and Propeller Hat logos* are trademarks of Parallax Inc., dba Parallax Semiconductor
>
> This project is a community project not for commercial use.
>
> This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Raspberry Pi (Trading) Ltd.* or any of its affiliates or subsidiaries.
> 
> Likewise, This project is in no way affiliated with, authorized, maintained, sponsored or endorsed by *Parallax Inc., dba Parallax Semiconductor* or any of its affiliates or subsidiaries.

--

### [Copyright](copyright) | [License](LICENSE)

[commits-shield]: https://img.shields.io/github/commit-activity/y/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge
[commits]: https://github.com/ironsheep/RPi-P2D2-Support/commits/master

[license-shield]: https://img.shields.io/github/license/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge

[maintenance-shield]: https://img.shields.io/badge/maintainer-S%20M%20Moraco%20%40ironsheepbiz-blue.svg?style=for-the-badge

[releases-shield]: https://img.shields.io/github/release/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge
[releases]: https://github.com/ironsheep/RPi-P2D2-Support/releases
