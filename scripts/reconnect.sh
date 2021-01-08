#! /bin/sh

# My omaBOX is connected to the internet via a 4G WiFi USB stick. Sometimes
# Ubuntu tries to connect to the WiFi before the stick has finished booting.
# This script reconnects to the network (ran daily) to make sure the omaBOX
# does connect to the network. You probably don’t need this script. Simply
# connect the network-setup-control manually if you do, skip this if you don’t.

set -e

dbus-send --system --type=method_call --print-reply --dest=io.netplan.Netplan /io/netplan/Netplan io.netplan.Netplan.Apply
