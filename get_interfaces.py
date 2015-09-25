#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Get a list of network interfaces on Linux
# Copyright © 2015 Jean Nassar

# Permission is hereby granted, free of charge, to any person obtaining
# a copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included
# in all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES
# OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
# TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE
# OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
__doc__ = """
File: {name}
Author: Jean Nassar
Email: jeannassar5@gmail.com
Github: https://github.com/masasin
Description: Get a list of network interfaces on Linux.

This code is compatible with Python versions 2 and 3.

Usage:
    {name} [-e] [-a | -ai]
    {name} -h | --help
    {name} --version

Options:
    -h --help       Show this screen.
    --version       Show version.
    -a --active     Only show interfaces which are UP, with IP addresses.
    -e --external   Only show external interfaces, with MAC addresses.
    -i --ip-only    Only show IP addresses.

""".format(name=__file__)
__version__ = "0.1"

from collections import namedtuple
import re

from docopt import docopt
import sh


def main():
    args = docopt(__doc__, version=__version__)
    external = args["--external"]
    active = args["--active"]
    interfaces = get_interfaces(external, active)
    for iface in interfaces:
        if args["--ip-only"]:
            print(iface.ip)
        else:
            print("{name}{sep}{mac}{sep2}{ip}"
                  .format(name=iface.name if external or active else iface,
                          sep=": " if external or active else "",
                          mac=(iface.mac + " ") if external else "",
                          sep2="@ " if external and active else "",
                          ip=iface.ip if active else ""))


def get_interfaces(external=False, active=False):
    """
    Get a list of network interfaces on Linux.

    To access the MAC address and/or the IP address, set the relevant keyword
    arguments to True.

    Parameters
    ----------
    external : bool, optional
        Only show external interfaces, and ignore virtual (e.g. loopback)
        devices, and return their MAC addresses.
    active : bool, optional
        Only show interfaces which are UP and have an IP address, and return
        their IPv4 addresses.

    Returns
    -------
    interfaces
        list of str containing the interface name by default, or list of
        namedtuple containing `name`, `mac`, and `ip` as requested.

    Raises
    ------
    ValueError
        No external interfaces have a valid IP address.

    Examples
    --------
    >>> print(get_interfaces())
    ['eth0', 'lo', 'wlan0']
    >>> print(get_interfaces(external=True))
    [Interface(name='eth0', mac='a0:b1:c2:d3:e4:f5'), Interface(name='wlan0', ma
    c='f5:e4:d3:c2:b1:a0')]
    >>> print(get_interfaces(ip=True))
    [Interface(name='lo', ip='127.0.0.1'), Interface(name='wlan0', ip='192.168.1
    1.2')]
    >>> print(get_interfaces(external=True, ip=True))
    [Interface(name='wlan0', mac='f5:e4:d3:c2:b1:a0', ip='192.168.11.2')]

    """
    name_pattern = "^(\w+)\s"
    mac_pattern = ".*?HWaddr[ ]([0-9A-Fa-f:]{17})" if external else ""
    ip_pattern = ".*?\n\s+inet[ ]addr:((?:\d+\.){3}\d+)" if active else ""
    pattern = re.compile("".join((name_pattern, mac_pattern, ip_pattern)),
                         flags=re.MULTILINE)

    ifconfig = str(sh.ifconfig())
    interfaces = pattern.findall(ifconfig)
    if external or active:
        if active and active and not interfaces:
            raise ValueError("No interfaces are up")
        Interface = namedtuple("Interface", "name {mac} {ip}".format(
            mac="mac" if external else "",
            ip="ip" if active else ""))
        return [Interface(*interface) for interface in interfaces]
    else:
        return interfaces


if __name__ == "__main__":
    # interfaces = get_interfaces(external=True, active=True)
    # for interface in interfaces:
        # print("{name}: {ip}".format(name=interface.name, ip=interface.ip))
    main()
