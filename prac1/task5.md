#!/bin/bash
sudo install -m 755 "$1" "/usr/local/bin/$(basename "$1")"
