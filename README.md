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

### Configuration Opportunities

We will continually be identifying fun and unique ways to use this hardware pairing. Here i'm starting a list of obvious opportunities I see I'm studying all connections for this pairing.

This will be an ever growing list of things that are possible now with a bit of configuration of the PRi and maybe some lightweight code for the P2 or the RPi:

- Debug console while running apps on P2D2.
- Root access console to the RPi for apps running on the P2D2.
- Boot time ID ROM emulation so the RPi can do HAT (Hardware on Top) runtime configuration of drivers.
- ... many more tba ...

Then there are things we'd like to do but have yet to figure out how:

- Boot-time access to TAQOZ on the P2 from the RPi - would allow us to debug P2 attached hardware using TAQOZ.
- ... more as we find ...

# Hardware Interaction leading to configuration Choices

As with any embedded system with many I/O choices sometimes tradeoffs have to be made to use certain capabilities (to get one to operate maybe you have to disable another, etc.)  I put this README together so I could annotate here for us all any such tradeoff issues I find.  So far, the Serial port is the one where we have more choices to make. The following sections (one for each interface) provide any details I've found to date.

**NOTE: Turn on Interfaces you need.** The hardware interfaces at the GPIO connector are generally turned off by default. You will want to use **raspi-config** to enable each of the interfaces you wish to use.  

**Language Choices:** I tend to use Python or ANSI C for interacting with the various devices as there are a lot of rich examples and library support. However there are a number of other languages you could choose to use.  

**NOTE:** While most software including Python itself is installed using **apt-get install {package}** Some of the lesser used Python packages will need to be installed using using **pip(3) install {package}** as they may not be prepackaged for **apt-get** installation.



## Interface: I2C0

... TBA ...

## Interface: 1-Wire

Enable the 1-wire interface using raspi-config. There are options for enabling a pull-up on the GPIO pin but most people just wire up their own external resistor.  The driver should default to the GPIO4 pin but it never hurts to double check. <sup name="a1">[1](#f1)</sup>

## Interface: Serial: UART0
There are two hardware UARTs: miniUART and PL011 that are configured to be primary and secondary on RPi3 and RPI4. (earlier models are different!) [^1] and four additional UARTs [2-5] [^2].

### MiniUART (less capable, but fully meets our normal debugging needs)

The **miniUART** is configured to be the primary and is by default routed to UART0 (at the GPIO connector), it is disabled but is configured, when enabled, to be a serial console with full command line access. The clock for this miniUART is derived from the CPU clock so it can be affected by temperature throttleing or overclocking.  (It appears on device files: /dev/serial0, /dev/ttyS0)

Considerations for use: 

* This MiniUART is easily capable of our P2 deafult 2MBit 8N1 configuration (it can go higher)
* We need to fix the cpu clock fequency so it can not cause our miniUART to change frequencies while we are using it.
* We need to set the input clock frequency to the miniUART to get to our 2Mbit rate

### PL011 UART (more capable)
The second and more capable UART is the **PL011 UART**. This is configured to be the Bluetooth LE serial transceiver and is the secondary serial device. (It appears on device files: /dev/serial01, /dev/ttyAMA0)

Considerations for use: 

* The PL011 UART is also capable of our P2 deafult 2MBit 8N1 configuration (it too can go higher)
* If we want to use this UART as UART0 then we need to flip the miniUART to handle the Bluetooth LE device and PL011 to be the primary connecting it to UART0 at our GPIO header.  Alternatively, we can just disable the bluetooth to cause this to happen as well.

### Serial Boot-time Configuration

Two files are involved in configuration of serial port use: /boot/config.txt and /boot/cmdline.txt

As an RPi user it is probably cleaner to make as much configuration change as you can using 'sudo raspi-config' utility. With this utility you can enable the primary serial port (disabled by default) and you can disable the serial console use of the primary serial port.

You will need to fix clock frequency (and/or configure which UARTs do what) by modifying the files directly. You can modify these files by hand using 'vi' or 'nano' as your editor but this is slightly  more error prone so we want to be very deliberate here. (You don't want typo's or mis-spellings in these files as stuff just doesn't work right where there are...)

To get to our 2Mb/s we need to adjust the clock fed to the UART. The setting needs to be 
at least 16X faster than the baud rate we want for our uart. The default is only 3MHz which results in just a little over 115200. So at the default setting, the max UART baud rate is 115200. [^4]

Therefore by adding 
```
init_uart_clock=32000000
``` 
to /boot/config.txt we can now select a 2Mb/s rate. (*yes, testing shows this works!*)

*Please remember that after adjusting these /boot/ files your changes do not take affect until you reboot the RPi.*

## Interface: SPI0

... TBA ...

## Interface: I2C SD/SC (Hat ID ROM)

... TBA ...

## Interface: Non-tasked GPIOs

If you are using the remaining 15 non-purposed GPIOs then when you decide the purpose and configuration needed for a pin you can set a boot-time configuration entry so the pin you need will be configured correctly from boot.  Entries to do this are placed in ```/boot/config.txt``` [^5]

## Special Setup Notes

### Run RPi's remotely using VNC

To set up your raspbery pi to display it's desktop remotely there are a couple of adjustments  you'll want to make:

1. Enable VNC (SSH too if you use it)
1. If no display attached, config RPi for headless operation
1. set display resolution as desired I use 
1. if using RP4 disable special driver blocking screen resizing [^6]

The first (1) enable VNC(SSH), (2) enable headless mode and (3) set resolution are handled in raspi-config:

* sudo raspi-config
* arrow down to "Interfacing Options" and press return
* arrow down to "P2 SSH" and press return
* TAB so that < YES > is selected and press return
* press return for confirmation < OK > and you're back at the main screen
* arrow down to "Interfacing Options" and press return
* arrow down to "P3 VNC" and press return
* TAB so that < YES > is selected and press return
* press return for confirmation < OK > and you're back at the main screen
* arrow down to "Advanced Options" and press return
* arrow down to "A5 Resolution" and press return
* Arrow down to "DMT mode 82 1920x1080 60Hz 16:9" (or select the mode you want) and press return
* press return "OK" on confirmation screen (you should arrive back at the main screen)
* press TAB, TAB to select < finish > and press return

(now your RPi will reboot if changes were made.)

For (4) I found that on RPi4's there's a video driver enabled by default which interferes and is enabled in /boot/config.txt:

```shell
[pi4]
# Enable DRM VC4 V3d driver on top of the dispmanx display stack
droverlay=vc4-fkms-v3d
max_framebuffers=2 
```

I commented all of these lines out and my RP4 can now display a larger screen when run by VNC.

---


[^1]: Raspberry Pi Doumentation: [UARTs](https://www.raspberrypi.org/documentation/configuration/uart.md)

[^2]: Raspberry Pi Doumentation - UART configuration overlays. Scroll down to: [UARTs and Device Tree](https://www.raspberrypi.org/documentation/configuration/uart.md)

[^3]: SoC Peripheral Doument: [BCM2835 Ref](https://www.raspberrypi.org/documentation/hardware/raspberrypi/bcm2835/BCM2835-ARM-Peripherals.pdf)

[^4]: Raspberry Pi Forums: [Can the UART go faster than 115200?](https://www.raspberrypi.org/forums/viewtopic.php?t=73673) Lot's of repeat information in here along with the details we need.

[^5]: Raspberry Pi Doumentation: [GPIO Control in config.txt](https://www.raspberrypi.org/documentation/configuration/config-txt/gpio.md) read this to learn entry needed for each of the 15 GPIO pins you want to boot-time configure.

[^6]: Raspberry Pi Forums: [Set VNC resolution?](https://www.raspberrypi.org/forums/viewtopic.php?t=200196) (Scroll down to Thu Jan 04,2018 10:20pm post.)

<b id="f1">1</b> Raspberry Pi Forums: [1-Wire Setup Questions](https://www.raspberrypi.org/forums/viewtopic.php?t=176406) various answers but the raspi-config method is the easiest and configures the extra dirver loading, etc. [↩](#a1)

---

## Credits

...TBD...

---

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

----

### [Copyright](copyright) | [License](LICENSE)

[commits-shield]: https://img.shields.io/github/commit-activity/y/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge
[commits]: https://github.com/ironsheep/RPi-P2D2-Support/commits/master

[license-shield]: https://img.shields.io/github/license/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge

[maintenance-shield]: https://img.shields.io/badge/maintainer-S%20M%20Moraco%20%40ironsheepbiz-blue.svg?style=for-the-badge

[releases-shield]: https://img.shields.io/github/release/ironsheep/RPi-P2D2-Support.svg?style=for-the-badge
[releases]: https://github.com/ironsheep/RPi-P2D2-Support/releases
